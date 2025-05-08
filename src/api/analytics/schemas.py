"""`/analytics` route schemas."""

from pydantic import BaseModel, Field
from typing import Dict


class Stats(BaseModel):
    """Scream reaction statistics."""

    screams_count: int = Field(..., ge=0)
    reactions_count: Dict[str, int] = Field(default_factory=dict)
