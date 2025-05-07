from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class Scream(Base):
    __tablename__ = 'screams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    reactions: Mapped[list['Reaction']] = relationship(
        'Reaction',
        back_populates='scream',
        lazy='selectin',
        cascade='all, delete-orphan',
    )


class Reaction(Base):
    __tablename__ = 'reactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    scream_id: Mapped[int] = mapped_column(ForeignKey('screams.id'))
    reaction: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scream: Mapped['Scream'] = relationship(
        'Scream',
        back_populates='reactions',
    )
