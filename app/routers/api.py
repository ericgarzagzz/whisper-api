from fastapi import APIRouter, HTTPException, UploadFile
import tempfile
from ..services.validations_service import check_cuda_warning
from ..services.transcription_service import start_transcription_process, cancel_transcription
from ..models.tasks import TaskStatus, TranscribeSegment
import uuid
import threading
import shutil
from ..services.transcription_task import create_transcription_task_result, get_transcription_task, get_transcription_task_last_result_segments, create_transcription_task, update_transcription_task_status

router = APIRouter()

tasks = {}

@router.post("/transcribe", response_model=TaskStatus)
async def start_transcription(file: UploadFile):
    check_cuda_warning()
    task_id = uuid.uuid4()
    task_id_str = str(task_id)
    tasks[task_id_str] = { "status": "running", "result": None, "process": None }
    create_transcription_task(task_id, status="running", result=None)

    if file.filename is None:
        return HTTPException(status_code=400, detail="The uploaded file has not been provided or is not a valid file")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    process, queue = start_transcription_process(task_id_str, temp_file_path)
    tasks[task_id_str]["process"] = process

    def check_queue():
        while True:
            if not queue.empty():
                task_id, status, result = queue.get()
                print(f"Queue got result: {result}")
                tasks[task_id]["status"] = status
                tasks[task_id]["result"] = result
                create_transcription_task_result(
                    task_id=uuid.UUID(task_id),
                    status=status,
                    segments=result
                )
                break
            
    threading.Thread(target=check_queue, daemon=True).start()

    return TaskStatus(task_id=task_id_str, status="running")

@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    task_id_uuid = uuid.UUID(task_id)
    task_info = get_transcription_task(task_id_uuid)
    segments_entities = get_transcription_task_last_result_segments(task_id_uuid)
    segments: list[TranscribeSegment] = []
    for s in segments_entities:
        segments.append(TranscribeSegment.from_entity(s))

    if task_info is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    return TaskStatus(task_id=task_id, status=task_info.status, result=segments)

@router.delete("/cancel/{task_id}", response_model=TaskStatus)
async def cancel_task(task_id: str):
    task_id_uuid = uuid.UUID(task_id)
    task_info = get_transcription_task(task_id_uuid)

    if task_info is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_id in tasks:
        process = tasks[task_id]["process"]
        cancel_transcription(process)
        tasks[task_id]["status"] = "canceled"
        task_info = update_transcription_task_status(uuid.UUID(task_id), "canceled")

    return TaskStatus(task_id=task_id, status=task_info.status)
