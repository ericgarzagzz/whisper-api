from sqlmodel import Session, select
from ..models.transcribe_segments import TranscribeSegment
from ..services.db_service import TranscriptionTask, TranscriptionTaskResult, TranscriptionTaskResultSegment, engine
import uuid
from typing import Sequence

def search_transcription_tasks() -> Sequence[TranscriptionTask]:
    with Session(engine) as session:
        statement = select(TranscriptionTask).order_by(TranscriptionTask.created_at.desc())
        tasks = session.exec(statement)
        return tasks.all()

def get_transcription_task(task_id: uuid.UUID) -> TranscriptionTask | None:
    session = Session(engine)
    task = session.get(TranscriptionTask, task_id)
    return task

def get_transcription_task_last_result_segments(
    task_id: uuid.UUID
) -> list[TranscriptionTaskResultSegment]:
    with Session(engine) as session:
        statement = (
            select(TranscriptionTaskResult)
            .where(TranscriptionTaskResult.task_id == task_id)
            .order_by(TranscriptionTaskResult.id.desc())
        )
        last_result = session.exec(statement).first()

        if last_result is None:
            return []

        return last_result.segments
    
def get_transcription_task_full(task_id: uuid.UUID) -> TranscriptionTask | None:
    with Session(engine) as session:
        statement = select(TranscriptionTask, TranscriptionTaskResult, list[TranscriptionTaskResultSegment]).where(TranscriptionTask.id == task_id).where(TranscriptionTaskResult.task_id == TranscriptionTask.id).where(TranscriptionTaskResultSegment.result_id == TranscriptionTaskResult.id)
        tasks = session.exec(statement)
        task_tuple = tasks.first()
        return task_tuple

def create_transcription_task(task_id: uuid.UUID, status: str, result: str|None):
    with Session(engine) as session:
        task = TranscriptionTask(id=task_id, status=status, result=result)
        session.add(task)
        session.commit()
        
def update_transcription_task_status(task_id: uuid.UUID, status: str) -> TranscriptionTask:
    with Session(engine) as session:
        task = session.get(TranscriptionTask, task_id)
        task.status = status
        session.commit()
        session.refresh(task)
        return task

def create_transcription_task_result(task_id: uuid.UUID, status: str, segments: list[TranscribeSegment]):
    with Session(engine) as session:
        task = session.get(TranscriptionTask, task_id)
        task.status = status
        result = TranscriptionTaskResult()
        for s in segments:
            segment = TranscriptionTaskResultSegment(
                seek=s["seek"],
                start=s["start"],
                end=s["end"],
                text=s["text"],
                temperature=s["temperature"],
                avg_logprob=s["avg_logprob"],
                compression_ratio=s["compression_ratio"],
                no_speech_prob=s["no_speech_prob"]
            )
            result.segments.append(segment)

        if len(result.segments) > 0:
            task.results.append(result)

        session.add(task)
        session.commit()
