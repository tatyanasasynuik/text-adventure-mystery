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
    """Room + turn + status, per plans/SAVE_LOAD_PLAN.md. Inventory, flags,
    promotions, and the evidence log are separate child tables below (each
    FK'd to save_id) rather than columns here — same normalized shape the
    plan calls for, so this row itself doesn't grow as item content grows."""

    __tablename__ = "saves"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_room_id = Column(String, nullable=False)
    turn_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="in_progress")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="save")


class VisitedRoom(Base):
    """Backs the "places" command. Not in the original SAVE_LOAD_PLAN schema —
    added once it became clear players need a way to recall where they've been."""

    __tablename__ = "visited_rooms"

    save_id = Column(Integer, ForeignKey("saves.id"), primary_key=True)
    room_id = Column(String, primary_key=True)
    first_visited_turn = Column(Integer, nullable=False)


class SaveInventory(Base):
    """Per SAVE_LOAD_PLAN.md's save_inventory. item_id is a key into the
    static ITEMS dict in items.py, not an FK — there's no items table, items
    are content data the same way rooms are."""

    __tablename__ = "save_inventory"

    save_id = Column(Integer, ForeignKey("saves.id"), primary_key=True)
    item_id = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="held")  # "held" | "consumed"
    acquired_at_turn = Column(Integer, nullable=False)


class SaveFlag(Base):
    """Per SAVE_LOAD_PLAN.md's save_flags — unlock-combo results that aren't
    items (heard_tape_playback, photo_detail_noted, etc.)."""

    __tablename__ = "save_flags"

    save_id = Column(Integer, ForeignKey("saves.id"), primary_key=True)
    flag_key = Column(String, primary_key=True)
    set_at_turn = Column(Integer, nullable=False)


class SaveItemPromotion(Base):
    """Per SAVE_LOAD_PLAN.md's save_item_promotions. Row presence = that
    item is type "evidence" for this save; absence = still base "item"."""

    __tablename__ = "save_item_promotions"

    save_id = Column(Integer, ForeignKey("saves.id"), primary_key=True)
    item_id = Column(String, primary_key=True)
    promoted_at_turn = Column(Integer, nullable=False)


class SaveEvidenceLog(Base):
    """Per SAVE_LOAD_PLAN.md's save_evidence_log — ordered log powering the
    notebook/case-file screen, not a re-derived query."""

    __tablename__ = "save_evidence_log"

    save_id = Column(Integer, ForeignKey("saves.id"), primary_key=True)
    evidence_item_id = Column(String, primary_key=True)
    collected_at_turn = Column(Integer, nullable=False)
