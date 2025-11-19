import pandas as pd
from celery import Task
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from app.database import SessionLocal
from app.models import Product
from app.tasks.celery_app import celery_app
import os


class DatabaseTask(Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, name='import_products_task')
def import_products_task(self, file_path: str, chunk_size: int = 5000):
    """
    Import products from CSV file with duplicate handling - OPTIMIZED
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # Validate required columns
        required_columns = ['sku', 'name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Handle optional columns with defaults
        if 'description' in df.columns:
            df['description'] = df['description'].fillna('')
        else:
            df['description'] = ''
        
        if 'active' in df.columns:
            df['active'] = df['active'].fillna(True)
        else:
            df['active'] = True
        
        # Calculate timestamps once for all rows (major optimization)
        current_time = datetime.utcnow()
        df['created_at'] = current_time
        df['updated_at'] = current_time
        
        # Convert data types upfront for better performance
        df['sku'] = df['sku'].astype(str)
        df['name'] = df['name'].astype(str)
        df['description'] = df['description'].astype(str)
        df['active'] = df['active'].astype(bool)
        
        # Process in larger chunks for better performance
        processed = 0
        
        for i in range(0, total_rows, chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            
            # Deduplicate within the chunk - keep last occurrence
            chunk = chunk.drop_duplicates(subset=['sku'], keep='last')
            
            # Convert chunk to list of dicts more efficiently
            values_list = chunk.to_dict('records')
            
            # Use PostgreSQL INSERT ... ON CONFLICT DO UPDATE
            stmt = insert(Product).values(values_list)
            
            # Define what to do on conflict (duplicate SKU)
            stmt = stmt.on_conflict_do_update(
                index_elements=['sku'],
                set_={
                    'name': stmt.excluded.name,
                    'description': stmt.excluded.description,
                    'active': stmt.excluded.active,
                    'updated_at': stmt.excluded.updated_at
                }
            )
            
            # Execute the statement
            self.db.execute(stmt)
            self.db.commit()
            
            processed += len(chunk)
            
            # Update progress less frequently (only every 2 chunks or at end)
            if i % (chunk_size * 2) == 0 or processed >= total_rows:
                progress = int((processed / total_rows) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed,
                        'total': total_rows,
                        'percent': progress
                    }
                )
        
        # Final progress update
        self.update_state(
            state='PROGRESS',
            meta={
                'current': processed,
                'total': total_rows,
                'percent': 100
            }
        )
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            'status': 'completed',
            'total': total_rows,
            'processed': processed,
            'message': f'Successfully imported {processed} products'
        }
        
    except Exception as e:
        self.db.rollback()
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e
