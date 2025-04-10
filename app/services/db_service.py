from typing import Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel, create_engine

class TranscriptionTask(SQLModel, table=True):
    __tablename__ = "transcription_task"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: str
    results: list["TranscriptionTaskResult"] = Relationship(back_populates="task")

class TranscriptionTaskResult(SQLModel, table=True):
    __tablename__ = "transcription_task_result"
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="transcription_task.id")
    task: TranscriptionTask = Relationship(back_populates="results")
    segments: list["TranscriptionTaskResultSegment"] = Relationship(back_populates="result")

class TranscriptionTaskResultSegment(SQLModel, table=True):
    __tablename__ = "transcription_task_result_segment"
    id: Optional[int] = Field(default=None, primary_key=True)
    seek: float
    start: float
    end: float
    text: str
    # TODO: Include tokens in the result
    # tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    result_id: Optional[int] = Field(foreign_key="transcription_task_result.id")
    result: Optional[TranscriptionTaskResult] = Relationship(back_populates="segments")

sqlite_file_name = "db.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)
