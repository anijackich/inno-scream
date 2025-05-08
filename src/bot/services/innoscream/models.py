"""Data models for screams and statistics.

This module defines Pydantic models used throughout the application
to represent scream messages and user statistics related to scream reactions.
"""

from datetime import datetime

from pydantic import BaseModel


class Scream(BaseModel):
    """Represents an anonymous scream message.

    Attributes:
        scream_id (int): Unique identifier for the scream.
        user_id (int): ID of the user who submitted the scream.
        text (str): Content of the scream.
        created_at (datetime): Timestamp when the scream was created.
        reactions (dict[str, int]): Mapping of reactions to reactions count.
    """

    scream_id: int
    user_id: int
    text: str
    created_at: datetime
    reactions: dict[str, int]


class Stats(BaseModel):
    """Statistics for a user's scream activity.

    Attributes:
        screams_count (int): Total number of screams posted by the user.
        reactions_count (dict[str, int]): Mapping of reactions
        to how many times each was received.
    """

    screams_count: int
    reactions_count: dict[str, int]
