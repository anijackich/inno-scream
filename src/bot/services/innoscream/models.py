from datetime import datetime

from pydantic import BaseModel


class Scream(BaseModel):
    scream_id: int
    user_id: int
    text: str
    created_at: datetime
    reactions: dict[str, int]


class Stats(BaseModel):
    screams_count: int
    reactions_count: dict[str, int]
