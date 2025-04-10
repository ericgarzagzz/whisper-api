from pydantic import BaseModel
from ..services.db_service import TranscriptionTaskResultSegment

class TranscribeSegment(BaseModel):
    id: int
    seek: float
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    
    @classmethod
    def from_entity(cls, segment: TranscriptionTaskResultSegment) -> "TranscribeSegment":
        return cls(
            id=segment.id,
            seek=segment.seek,
            start=segment.start,
            end=segment.end,
            text=segment.text,
            tokens=[],  # Since tokens not yet implemented in DB model
            temperature=segment.temperature,
            avg_logprob=segment.avg_logprob,
            compression_ratio=segment.compression_ratio,
            no_speech_prob=segment.no_speech_prob
        )
