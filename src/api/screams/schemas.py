"""`/screams` route schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class Scream(BaseModel):
    """Scream object."""

    scream_id: int = Field(...)
    user_id: int = Field(...)
    text: str = Field(...)
    created_at: datetime = Field(...)
    reactions: dict[str, int] = Field(...)


class ScreamCreate(BaseModel):
    """Scream creation data."""

    user_id: int = Field(...)
    text: str = Field(...)


class ReactionCreate(BaseModel):
    """Reaction creation data."""

    scream_id: int = Field(...)
    user_id: int = Field(...)
    reaction: str = Field(...)
