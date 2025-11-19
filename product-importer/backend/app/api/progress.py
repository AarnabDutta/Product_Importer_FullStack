# SSE endpoint for upload progress
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from app.tasks.celery_app import celery_app
import json
import asyncio
from typing import AsyncGenerator


router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/{task_id}")
async def get_progress(task_id: str):
    """Stream task progress using Server-Sent Events"""
    
    async def event_generator() -> AsyncGenerator:
        previous_state = None
        
        try:
            while True:
                try:
                    # Get task status from Celery
                    task = celery_app.AsyncResult(task_id)
                    
                    if task.state == 'PENDING':
                        data = {
                            "state": "PENDING",
                            "current": 0,
                            "total": 0,
                            "percent": 0,
                            "status": "Task pending..."
                        }
                    elif task.state == 'PROGRESS':
                        info = task.info if task.info is not None else {}
                        data = {
                            "state": "PROGRESS",
                            "current": info.get('current', 0),
                            "total": info.get('total', 1),
                            "percent": info.get('percent', 0),
                            "status": f"Processing... {info.get('percent', 0)}%"
                        }
                    elif task.state == 'SUCCESS':
                        result = task.result if task.result is not None else {}
                        data = {
                            "state": "SUCCESS",
                            "current": result.get('processed', result.get('total', 0)),
                            "total": result.get('total', 0),
                            "percent": 100,
                            "status": "Complete!",
                            "result": result
                        }
                        yield {
                            "event": "progress",
                            "data": json.dumps(data)
                        }
                        break
                    elif task.state == 'FAILURE':
                        error_msg = str(task.info) if task.info is not None else 'Unknown error'
                        data = {
                            "state": "FAILURE",
                            "status": "Import failed",
                            "error": error_msg,
                            "current": 0,
                            "total": 0,
                            "percent": 0
                        }
                        yield {
                            "event": "progress",
                            "data": json.dumps(data)
                        }
                        break
                    else:
                        data = {
                            "state": task.state,
                            "current": 0,
                            "total": 0,
                            "percent": 0,
                            "status": str(task.info) if task.info is not None else 'Processing...'
                        }
                    
                    # Send update if state changed or during progress
                    if previous_state != task.state or task.state == 'PROGRESS':
                        yield {
                            "event": "progress",
                            "data": json.dumps(data)
                        }
                        previous_state = task.state
                    
                    # Poll every 500ms for smooth progress updates
                    await asyncio.sleep(0.5)
                    
                except Exception as inner_e:
                    # Handle errors within the loop
                    error_data = {
                        "state": "FAILURE",
                        "status": "Error checking task status",
                        "error": str(inner_e),
                        "current": 0,
                        "total": 0,
                        "percent": 0
                    }
                    yield {
                        "event": "error",
                        "data": json.dumps(error_data)
                    }
                    break
                    
        except Exception as outer_e:
            # Handle generator-level errors
            error_data = {
                "state": "FAILURE",
                "status": "Fatal error",
                "error": str(outer_e),
                "current": 0,
                "total": 0,
                "percent": 0
            }
            yield {
                "event": "error",
                "data": json.dumps(error_data)
            }
    
    return EventSourceResponse(event_generator())
