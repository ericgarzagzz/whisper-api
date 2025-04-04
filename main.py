from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from torch import multiprocessing
import torch
from torch.cuda import is_available
import whisper
import threading
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

tiny_whisper_model = whisper.load_model("tiny")

tasks = {}

class TranscriptionRequest(BaseModel):
    audio_file: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: str|None = None

def check_cuda_warning():
    # Check if CUDA device is available
    if torch.cuda.is_available():
        logger.info("CUDA is available and will be used")
        print("CUDA is available and will be used")
    else:
        logger.warning("CPU will be used because CUDA is not available")
        print("CPU will be used because CUDA is not available")

def transcribe_audio(task_id: str, audio_file: str, queue: multiprocessing.Queue):
    try:
        result = tiny_whisper_model.transcribe(audio_file)
        queue.put((task_id, "completed", result["text"]))
    except Exception as e:
        queue.put((task_id, "failed", str(e)))

def start_transcription_process(task_id: str, audio_file: str):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=transcribe_audio, args=(task_id, audio_file, queue))
    process.start()
    return process, queue

def cancel_transcription(process: multiprocessing.Process):
    if process.is_alive():
        process.terminate()
        process.join()

@app.post("/transcribe", response_model=TaskStatus)
async def start_transcription(request: TranscriptionRequest):
    check_cuda_warning()
    task_id = str(uuid.uuid4())
    tasks[task_id] = { "status": "running", "result": None, "process": None }

    process, queue = start_transcription_process(task_id, request.audio_file)
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

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_info = tasks[task_id]
    return TaskStatus(task_id=task_id, status=task_info["status"], result=task_info["result"])

@app.delete("/cancel/{task_id}", response_model=TaskStatus)
async def cancel_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    process = tasks[task_id]["process"]
    cancel_transcription(process)
    tasks[task_id]["status"] = "canceled"

    return TaskStatus(task_id=task_id, status=tasks[task_id]["status"])
