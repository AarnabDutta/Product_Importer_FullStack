import pandas as pd
import os
from typing import List, Dict, Any, Generator
from app.config import settings


def validate_csv_headers(file_path: str) -> tuple[bool, str]:
    """
    Validate that the CSV file contains all required columns.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        df = pd.read_csv(file_path, nrows=0)
        required_columns = ['sku', 'name', 'description']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        return True, "Valid CSV format"
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def process_csv_chunk(file_path: str, chunk_size: int = 10000) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Process CSV file in chunks to handle large files efficiently.
    
    Args:
        file_path: Path to the CSV file
        chunk_size: Number of rows to process per chunk
        
    Yields:
        List of dictionaries containing product data for each chunk
    """
    try:
        chunk_iterator = pd.read_csv(
            file_path, 
            chunksize=chunk_size,
            keep_default_na=False,
            dtype=str
        )
        
        for chunk in chunk_iterator:
            records = []
            for _, row in chunk.iterrows():
                sku_value = str(row['sku']).strip()
                name_value = str(row['name']).strip()
                description_value = str(row.get('description', '')).strip() if row.get('description') else ''
                
                if not sku_value or not name_value:
                    continue
                
                record = {
                    'sku': sku_value,
                    'name': name_value,
                    'description': description_value,
                    'active': True
                }
                records.append(record)
            
            yield records
            
    except Exception as e:
        raise Exception(f"Error processing CSV: {str(e)}")


def get_total_rows(file_path: str) -> int:
    """
    Get the total number of rows in the CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Total number of rows (excluding header)
    """
    try:
        df = pd.read_csv(
            file_path, 
            keep_default_na=False, 
            dtype=str
        )
        return len(df)
    except Exception as e:
        raise Exception(f"Error counting rows: {str(e)}")
