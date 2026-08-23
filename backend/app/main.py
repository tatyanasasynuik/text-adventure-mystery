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


# Prepositions/articles stripped from the target so "look at window" and
# "look window" (or "go to the hallway" and "go hallway") parse the same
# without a hardcoded startswith() check per phrasing.
FILLER_WORDS = {"to", "at", "around", "the", "a", "an", "in", "on", "toward", "towards", "of"}
LOOK_VERBS = {"look", "examine", "inspect", "x"}
GO_VERBS = {"go", "walk", "head", "move", "travel"}


def parse_command(text: str):
    words = text.split()
    if not words:
        return "", ""
    verb, *rest = words
    target = " ".join(w for w in rest if w not in FILLER_WORDS)
    return verb, target


def ensure_visited(db: Session, save: Save) -> None:
    already = (
        db.query(VisitedRoom)
        .filter_by(save_id=save.id, room_id=save.current_room_id)
        .first()
    )
    if already is None:
        db.add(VisitedRoom(save_id=save.id, room_id=save.current_room_id, first_visited_turn=save.turn_count))


def notebook_payload(db: Session, save: Save):
    visited = (
        db.query(VisitedRoom)
        .filter_by(save_id=save.id)
        .order_by(VisitedRoom.first_visited_turn)
        .all()
    )
    # "inventory" is always empty for now — no item system yet (see the TODOs
    # in rooms.py/main.py). Shape is here so the frontend panel doesn't need
    # to change once items exist, just populate this list for real.
    return {
        "visited": [ROOMS[v.room_id]["name"] for v in visited],
        "inventory": [],
    }


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
    return {
        "room": room_payload(save),
        "turn_count": save.turn_count,
        "notebook": notebook_payload(db, save),
    }


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
    # TODO: "examine <noun>" already gets a stub response below; "take <noun>"
    # still doesn't exist. Both need rooms to carry an items list (see the TODO
    # in rooms.py) before they can say anything real — right now "examine desk"
    # is indistinguishable from "examine nonsense".
    verb, target = parse_command(text)

    if verb in LOOK_VERBS:
        message = room["description"] if not target else f"You don't see anything special about the {target}."
    elif verb in GO_VERBS:
        message = try_move(save, room, target) if target else "Go where?"
    elif text in room["exits"]:
        message = try_move(save, room, text)
    elif text in ("places", "visited", "where have i been", "inventory", "inv", "i"):
        # These used to be typed commands returning a text listing; that's now
        # the notebook panel (always visible, not something you ask for).
        message = "Check your notebook — it's got a running list of that."
    else:
        message = "You're not sure how to do that yet."

    save.turn_count += 1
    ensure_visited(db, save)
    db.commit()
    db.refresh(save)

    return {
        "message": message,
        "room": room_payload(save),
        "turn_count": save.turn_count,
        "notebook": notebook_payload(db, save),
    }


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
