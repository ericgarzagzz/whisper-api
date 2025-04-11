from pydantic import BaseModel
from .transcribe_segments import TranscribeSegment

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: list[TranscribeSegment]|str|None = None

class TaskListItem(BaseModel):
    task_id: str
    status: str
