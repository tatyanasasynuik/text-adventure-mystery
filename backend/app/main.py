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


def move_with_narration(db: Session, save: Save, room: dict, target: str) -> str:
    # Study only ever leads to Hallway, and Hallway is unreachable any other
    # way this early, so a first-ever arrival here always means "came from
    # the Study" — a cheap, safe way to nudge the player toward the notebook
    # existing at all, right as it becomes useful.
    first_time_hallway = target == "hallway" and not has_visited(db, save, "hallway")
    message = try_move(save, room, target)
    if first_time_hallway and save.current_room_id == "hallway":
        message += " You jot a quick note in your notebook: been in the Study."
    return message


# Prepositions/articles stripped from the target so "look at window" and
# "look window" (or "go to the hallway" and "go hallway") parse the same
# without a hardcoded startswith() check per phrasing.
FILLER_WORDS = {"to", "at", "around", "the", "a", "an", "in", "on", "toward", "towards", "of"}
LOOK_VERBS = {"look", "examine", "inspect", "x"}
GO_VERBS = {"go", "walk", "head", "move", "travel"}

# Two separate typed commands, each answered inline in the log — not a UI
# element, so the player has to learn they exist by trying, same as any other
# verb. "notebook" is the places-visited log; "items" is the (currently
# empty) inventory. Deliberately not merged into one command.
PLACES_PHRASES = {"notebook", "places", "visited", "where have i been"}
ITEMS_PHRASES = {"items", "item", "inventory", "inv", "i"}


def parse_command(text: str):
    words = text.split()
    if not words:
        return "", ""
    verb, *rest = words
    target = " ".join(w for w in rest if w not in FILLER_WORDS)
    return verb, target


def has_visited(db: Session, save: Save, room_id: str) -> bool:
    return (
        db.query(VisitedRoom).filter_by(save_id=save.id, room_id=room_id).first()
        is not None
    )


def ensure_visited(db: Session, save: Save) -> None:
    if not has_visited(db, save, save.current_room_id):
        db.add(VisitedRoom(save_id=save.id, room_id=save.current_room_id, first_visited_turn=save.turn_count))


def visited_room_names(db: Session, save: Save):
    visited = (
        db.query(VisitedRoom)
        .filter_by(save_id=save.id)
        .order_by(VisitedRoom.first_visited_turn)
        .all()
    )
    return [ROOMS[v.room_id]["name"] for v in visited]


def places_summary(names) -> str:
    if not names:
        return "You haven't been anywhere yet."
    return "You've been to: " + ", ".join(names) + "."


def items_summary(names) -> str:
    if not names:
        return "You aren't carrying anything yet."
    return "You're carrying: " + ", ".join(names) + "."


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
    # TODO: "examine <noun>" already gets a stub response below; "take <noun>"
    # still doesn't exist. Both need rooms to carry an items list (see the TODO
    # in rooms.py) before they can say anything real — right now "examine desk"
    # is indistinguishable from "examine nonsense".
    verb, target = parse_command(text)

    if verb in LOOK_VERBS:
        message = room["description"] if not target else f"You don't see anything special about the {target}."
    elif verb in GO_VERBS:
        message = move_with_narration(db, save, room, target) if target else "Go where?"
    elif text in room["exits"]:
        message = move_with_narration(db, save, room, text)
    elif text in PLACES_PHRASES:
        message = "You flip open your notebook. " + places_summary(visited_room_names(db, save))
    elif text in ITEMS_PHRASES:
        message = "You check your things. " + items_summary([])  # inventory always empty for now
    else:
        message = "You're not sure how to do that yet."

    save.turn_count += 1
    ensure_visited(db, save)
    db.commit()
    db.refresh(save)

    return {"message": message, "room": room_payload(save), "turn_count": save.turn_count}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
