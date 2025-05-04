from pydantic import BaseModel, Field


class Stats(BaseModel):
    screams_count: int = Field(..., ge=0)
