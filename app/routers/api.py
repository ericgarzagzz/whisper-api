from fastapi import APIRouter, HTTPException, UploadFile
import tempfile
from services.validations_service import check_cuda_warning
from services.transcription_service import start_transcription_process, cancel_transcription
from models.tasks import TaskStatus
import uuid
import threading
import shutil

router = APIRouter()

tasks = {}

@router.post("/transcribe", response_model=TaskStatus)
async def start_transcription(file: UploadFile):
    check_cuda_warning()
    task_id = str(uuid.uuid4())
    tasks[task_id] = { "status": "running", "result": None, "process": None }

    if file.filename is None:
        return HTTPException(status_code=400, detail="The uploaded file has not been provided or is not a valid file")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    process, queue = start_transcription_process(task_id, temp_file_path)
    tasks[task_id]["process"] = process

    def check_queue():
        while True:
            if not queue.empty():
                task_id, status, result = queue.get()
                tasks[task_id]["status"] = status
                tasks[task_id]["result"] = result
                break
            
    threading.Thread(target=check_queue, daemon=True).start()

    return TaskStatus(task_id=task_id, status="running")

@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_info = tasks[task_id]
    return TaskStatus(task_id=task_id, status=task_info["status"], result=task_info["result"])

@router.delete("/cancel/{task_id}", response_model=TaskStatus)
async def cancel_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    process = tasks[task_id]["process"]
    cancel_transcription(process)
    tasks[task_id]["status"] = "canceled"

    return TaskStatus(task_id=task_id, status=tasks[task_id]["status"])
