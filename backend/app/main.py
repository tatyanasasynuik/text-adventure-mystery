from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import DEV_USERNAME
from .db import Base, engine, get_db
from .models import Save, User, VisitedRoom
from .rooms import ROOMS, STARTING_ROOM

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_or_create_dev_save(db: Session) -> Save:
    user = db.query(User).filter_by(username=DEV_USERNAME).first()
    if user is None:
        user = User(username=DEV_USERNAME)
        db.add(user)
        db.flush()
    save = db.query(Save).filter_by(user_id=user.id).first()
    if save is None:
        save = Save(user_id=user.id, current_room_id=STARTING_ROOM, turn_count=0)
        db.add(save)
    db.commit()
    db.refresh(save)
    return save


def room_payload(save: Save):
    room = ROOMS[save.current_room_id]
    return {"name": room["name"], "description": room["description"]}


def try_move(save: Save, room: dict, target: str) -> str:
    if target in room["exits"]:
        save.current_room_id = room["exits"][target]
        new_room = ROOMS[save.current_room_id]
        return f"You head to the {new_room['name']}. {new_room['description']}"
    return "You can't go that way."


def ensure_visited(db: Session, save: Save) -> None:
    already = (
        db.query(VisitedRoom)
        .filter_by(save_id=save.id, room_id=save.current_room_id)
        .first()
    )
    if already is None:
        db.add(VisitedRoom(save_id=save.id, room_id=save.current_room_id, first_visited_turn=save.turn_count))


def places_message(db: Session, save: Save) -> str:
    visited = (
        db.query(VisitedRoom)
        .filter_by(save_id=save.id)
        .order_by(VisitedRoom.first_visited_turn)
        .all()
    )
    names = [ROOMS[v.room_id]["name"] for v in visited]
    if not names:
        return "You haven't been anywhere yet."
    return "You've been to: " + ", ".join(names) + "."


class ActionRequest(BaseModel):
    input: str


@app.get("/api/hello")
def hello():
    return {"message": "Hello, detective. Welcome to the case."}


@app.get("/api/game/state")
def get_state(db: Session = Depends(get_db)):
    save = get_or_create_dev_save(db)
    ensure_visited(db, save)
    db.commit()
    return {"room": room_payload(save), "turn_count": save.turn_count}


@app.post("/api/game/action")
def post_action(body: ActionRequest, db: Session = Depends(get_db)):
    save = get_or_create_dev_save(db)
    room = ROOMS[save.current_room_id]
    text = body.input.strip().lower()

    # TODO: meta commands the player will reach for — "what can I do", "where can
    # I go", "help". "Where can I go" is just room["exits"].keys() rendered as a
    # sentence, no new data needed. "What can I do" is less obvious once items
    # exist (per plans/SAVE_LOAD_PLAN.md) — probably exits + inventory verbs, but
    # worth deciding once there's an inventory to list.
    #
    # TODO: teach navigation by playing it, not exposition. The opening room/
    # scene should nudge the player into typing something (e.g. narration that
    # models "go hallway" in passing) rather than a "type HELP" banner or a
    # scripted walkthrough overlay — "places"/"inventory" below and the meta
    # commands above are the fallback net, not the primary onboarding.
    #
    # TODO: "examine <noun>"/"take <noun>" verbs, once rooms carry an items
    # list (see the TODO in rooms.py). Scenery gets a flavor line back either
    # way; only inventory-type items also move into save_inventory. Room
    # descriptions already name things (desk, candle stub, ink pad) that
    # currently do nothing if you try to interact with them.
    if text in ("look", "look around"):
        message = room["description"]
    elif text.startswith("go "):
        target = text[3:].strip()
        if target.startswith("to "):
            target = target[3:].strip()
        message = try_move(save, room, target)
    elif text in room["exits"]:
        message = try_move(save, room, text)
    elif text in ("places", "visited", "where have i been"):
        message = places_message(db, save)
    elif text in ("inventory", "inv", "i"):
        message = "You aren't carrying anything yet."
    else:
        message = "You're not sure how to do that yet."

    save.turn_count += 1
    ensure_visited(db, save)
    db.commit()
    db.refresh(save)

    return {"message": message, "room": room_payload(save), "turn_count": save.turn_count}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
