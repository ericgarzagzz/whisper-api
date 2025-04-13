import mimetypes
from functools import lru_cache
import os
import re
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from app.config import Settings
from app.services.storage_service import download_file, get_file, get_file_range, stat_file
from app.services.transcription_task import get_transcription_task
from app.utils.streaming import parse_range

router = APIRouter()

@lru_cache()
def get_settings():
    return Settings()

@router.get("/download/{task_id}")
async def download_from_task(
    task_id: str, 
    settings: Annotated[Settings, Depends(get_settings)]
):
    task_id_uuid = uuid.UUID(task_id)
    task_info = get_transcription_task(task_id_uuid)
    if task_info is None:
        raise HTTPException(status_code=404, detail="Task not found")

    file_content = download_file(settings.minio_bucket_name, task_info.file_path)
    return Response(content=file_content, media_type="application/octet-stream", headers={
        "Content-Disposition": f"attachment; filename={task_info.name}"
    })

@router.get("/stream/{task_id}")
async def stream_from_task(
    task_id: str, 
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request
):
    task_id_uuid = uuid.UUID(task_id)
    task_info = get_transcription_task(task_id_uuid)
    if task_info is None:
        raise HTTPException(status_code=404, detail="Task not found")

    object_stat_file = stat_file(settings.minio_bucket_name, task_info.file_path)

    media_type = mimetypes.guess_type(task_info.name)[0]

    range_header = request.headers.get("Range", None)
    if range_header:
        range_start, range_end = parse_range(range_header, object_stat_file.size)
        if range_start is None or range_end is None:
            raise HTTPException(status_code=416, detail="Range Not Satisfiable")

        content_range = f"bytes {range_start}-{range_end}/{object_stat_file.size}"
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Range": content_range,
            "Content-Length": str(range_end - range_start + 1),
            "Content-Type": media_type
        }

        def file_stream():
            return get_file_range(settings.minio_bucket_name, task_info.file_path, range_start, range_end - range_start + 1)

        return StreamingResponse(file_stream(), headers=headers, media_type=media_type)

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(object_stat_file.size),
        "Content-Type": media_type
    }

    return StreamingResponse(get_file(settings.minio_bucket_name, task_info.file_path), headers=headers, media_type=media_type)
