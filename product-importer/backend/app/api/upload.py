# File upload endpoint
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.tasks.import_tasks import import_products_task
from app.schemas import UploadResponse
from app.config import settings
from app.utils.csv_processor import validate_csv_headers
import os
import aiofiles

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    file_path = os.path.join(settings.upload_dir, file.filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            if len(content) > settings.max_upload_size:
                raise HTTPException(status_code=400, detail="File too large")
            await f.write(content)
        
        is_valid, message = validate_csv_headers(file_path)
        if not is_valid:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=message)
        
        task = import_products_task.apply_async(args=[file_path])
        
        return {
            "task_id": task.id,
            "message": "File uploaded successfully. Processing started."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
