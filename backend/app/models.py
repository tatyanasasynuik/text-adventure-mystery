from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    """Stand-in until real auth exists — just enough for `saves` to have a FK target."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)

    save = relationship("Save", back_populates="user", uselist=False)


class Save(Base):
    """Subset of the schema in plans/SAVE_LOAD_PLAN.md — room + turn only, no
    inventory/evidence tables yet since there's no item content to attach them to."""

    __tablename__ = "saves"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_room_id = Column(String, nullable=False)
    turn_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="in_progress")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="save")
