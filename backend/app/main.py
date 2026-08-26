from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import DEV_USERNAME
from .db import Base, engine, get_db
from .items import COMBINATIONS, ITEMS
from .models import Save, SaveEvidenceLog, SaveFlag, SaveInventory, SaveItemPromotion, User, VisitedRoom
from .rooms import ROOMS, STARTING_ROOM
from .state import has_flag, held_item_ids, is_evidence, layered_text, swap_text

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


def room_description(db: Session, save: Save, room_id: str) -> str:
    room = ROOMS[room_id]
    # "description_parts" is the opt-in for a room that needs a clause
    # rewritten in place (a swap) rather than only ever appended to (a
    # layer) — e.g. the Study's desk clause naming exactly what's still on
    # it, not "holds a candle stub" plus a footnote once it doesn't. Plain
    # strings pass through unchanged; a {"base", "variants"} dict resolves
    # like item_display_description's evidence_description swap does. Rooms
    # that don't need this keep using a flat "description" string.
    parts = room.get("description_parts")
    if parts is not None:
        base = " ".join(
            swap_text(db, save, part["base"], part.get("variants", [])) if isinstance(part, dict) else part
            for part in parts
        )
    else:
        base = room["description"]
    return layered_text(db, save, base, room.get("state_notes", []))


def room_payload(db: Session, save: Save):
    room = ROOMS[save.current_room_id]
    return {"name": room["name"], "description": room_description(db, save, save.current_room_id)}


def try_move(db: Session, save: Save, room: dict, target: str) -> str:
    target = room.get("exit_aliases", {}).get(target, target)
    if target in room["exits"]:
        save.current_room_id = room["exits"][target]
        new_room = ROOMS[save.current_room_id]
        return f"You head to the {new_room['name']}. {room_description(db, save, save.current_room_id)}"
    gate = room.get("gated_exits", {}).get(target)
    if gate:
        if gate.get("requires_flag") and not has_flag(db, save, gate["requires_flag"]):
            return gate.get("blocked_message", "You can't go that way yet.")
        save.current_room_id = gate["target"]
        new_room = ROOMS[save.current_room_id]
        return f"You head to the {new_room['name']}. {room_description(db, save, save.current_room_id)}"
    return "You can't go that way."


def move_with_narration(db: Session, save: Save, room: dict, target: str) -> str:
    # Study only ever leads to Hallway, and Hallway is unreachable any other
    # way this early, so a first-ever arrival here always means "came from
    # the Study" — a cheap, safe way to nudge the player toward the notebook
    # existing at all, right as it becomes useful.
    first_time_hallway = target == "hallway" and not has_visited(db, save, "hallway")
    message = try_move(db, save, room, target)
    if first_time_hallway and save.current_room_id == "hallway":
        message += " You jot a quick note in your notebook: been in the Study."
    return message


# Prepositions/articles stripped from the target so "look at window" and
# "look window" (or "go to the hallway" and "go hallway") parse the same
# without a hardcoded startswith() check per phrasing. NOT used for combine
# parsing (see parse_combine) — "on"/"and" there are the delimiter between
# the two things being combined, not noise to discard.
FILLER_WORDS = {"to", "at", "around", "the", "a", "an", "in", "on", "toward", "towards", "of"}
LOOK_VERBS = {"look", "examine", "inspect", "x"}
GO_VERBS = {"go", "walk", "head", "move", "travel"}
TAKE_VERBS = {"take", "get", "grab"}
COMBINE_VERBS = {"combine", "use"}
COMBINE_CONNECTORS = {"with", "and", "on"}

# Two separate typed commands, each answered inline in the log — not a UI
# element, so the player has to learn they exist by trying, same as any other
# verb. "notebook" is the places-visited log; "items" is the inventory;
# "evidence" is the promoted subset of it. Deliberately not merged into one
# command.
PLACES_PHRASES = {"notebook", "places", "visited", "where have i been"}
ITEMS_PHRASES = {"items", "item", "inventory", "inv", "i"}
EVIDENCE_PHRASES = {"evidence", "clues", "case file", "casefile"}


def parse_command(text: str):
    words = text.split()
    if not words:
        return "", ""
    verb, *rest = words
    # "pick up X" is the one verb phrase that's two words before its target;
    # everything else here is a single verb word.
    if verb == "pick" and rest[:1] == ["up"]:
        verb, rest = "take", rest[1:]
    target = " ".join(w for w in rest if w not in FILLER_WORDS)
    return verb, target


def parse_combine(rest_words):
    """"combine X with Y" / "combine X and Y" / "use X on Y" -> (X, Y), or
    None if there's no connector to split on. Operates on raw words, not
    filler-stripped text — "on" is meaningful here, unlike everywhere else."""
    for i, word in enumerate(rest_words):
        if word in COMBINE_CONNECTORS:
            left = [w for w in rest_words[:i] if w not in FILLER_WORDS - COMBINE_CONNECTORS]
            right = [w for w in rest_words[i + 1:] if w not in FILLER_WORDS - COMBINE_CONNECTORS]
            if left and right:
                return " ".join(left), " ".join(right)
    return None


def _exact_forms(canonical_id: str, name: str, aliases):
    # The id itself only counts for an *exact* match ("window glass fragment"
    # typed in full) — it's an internal identifier, not prose, and folding
    # it into the fuzzy pass below would leak unrelated words (a "glass
    # shard" item with id window_glass_fragment would fuzzy-match bare
    # "window", stealing that from the window's own scenery text).
    return {name.lower(), canonical_id.replace("_", " "), *(a.lower() for a in aliases)}


def _fuzzy_forms(name: str, aliases):
    return {name.lower(), *(a.lower() for a in aliases)}


def match_item(target: str, item_ids) -> str | None:
    """Resolve typed text to one of the given item ids. Exact name/alias/id
    match first; falls back to sharing a word with the item's *name* or an
    alias (never the raw id), so "candle" still resolves without needing
    every synonym listed, but a compound id doesn't leak stray keywords."""
    target = target.lower().strip()
    if not target:
        return None
    items = {item_id: ITEMS[item_id] for item_id in item_ids}
    for item_id, item in items.items():
        if target in _exact_forms(item_id, item["name"], item.get("aliases", [])):
            return item_id
    target_words = set(target.split())
    for item_id, item in items.items():
        for form in _fuzzy_forms(item["name"], item.get("aliases", [])):
            form_words = set(form.split())
            # Containment, not mere overlap: "timeline note" must fully
            # contain or be contained by a candidate phrase. A bare shared
            # word ("note") would otherwise match alibi_note, gambling_iou_note,
            # and kitchen_timeline_note all at once — whichever came first in
            # dict order, silently wrong the rest of the time.
            if form_words <= target_words or target_words <= form_words:
                return item_id
    return None


def match_scenery(target: str, scenery: dict) -> str | None:
    """Same two-pass exact-then-fuzzy strategy as match_item, over canonical
    scenery ids instead of item ids — see the note atop ROOMS in rooms.py on
    why every alias must resolve back to the same canonical id."""
    target = target.lower().strip()
    if not target or not scenery:
        return None
    for key, entry in scenery.items():
        if target in _exact_forms(key, key.replace("_", " "), entry.get("aliases", [])):
            return key
    target_words = set(target.split())
    for key, entry in scenery.items():
        for form in _fuzzy_forms(key.replace("_", " "), entry.get("aliases", [])):
            form_words = set(form.split())
            if form_words <= target_words or target_words <= form_words:
                return key
    return None


def room_item_ids(db: Session, save: Save, room_id: str) -> set[str]:
    taken_or_gone = {
        row.item_id for row in db.query(SaveInventory).filter_by(save_id=save.id).all()
    }
    return {
        item_id
        for item_id, item in ITEMS.items()
        if item["room"] == room_id and item_id not in taken_or_gone
    }


def item_display_description(db: Session, save: Save, item_id: str) -> str:
    # Generalized evidence_description: it's folded in here as an implicit
    # last variant so existing items.py entries don't need editing, but any
    # item can now also carry an explicit "state_descriptions" list (see
    # fingerprint_lifted / timeline_note_kitchen in items.py) for swaps keyed
    # on a flag rather than only "promoted to evidence".
    item = ITEMS[item_id]
    variants = list(item.get("state_descriptions", []))
    if "evidence_description" in item:
        variants.append({"condition": {"evidence": item_id}, "text": item["evidence_description"]})
    return swap_text(db, save, item["description"], variants)


def resolve_operand(name: str, db: Session, save: Save, room: dict) -> str | None:
    """A combine operand is either something held in inventory, or a fixed
    piece of room scenery used in place ("use diagram on hatch") — see the
    "fixture:<room>:<key>" convention in items.py's COMBINATIONS."""
    held = held_item_ids(db, save)
    item_id = match_item(name, held)
    if item_id:
        return item_id
    scenery_key = match_scenery(name, room.get("scenery", {}))
    if scenery_key:
        return f"fixture:{save.current_room_id}:{scenery_key}"
    return None


def handle_take(db: Session, save: Save, room: dict, target: str) -> str:
    if not target:
        return "Take what?"
    room_ids = room_item_ids(db, save, save.current_room_id)
    item_id = match_item(target, room_ids)
    if item_id:
        db.add(SaveInventory(save_id=save.id, item_id=item_id, status="held", acquired_at_turn=save.turn_count))
        return f"You take the {ITEMS[item_id]['name']}."
    if match_item(target, held_item_ids(db, save)):
        return "You're already carrying that."
    if match_scenery(target, room.get("scenery", {})):
        return "That's not something you can carry."
    return "You don't see that here."


def handle_examine(db: Session, save: Save, room: dict, target: str) -> str:
    if not target:
        return room_description(db, save, save.current_room_id)
    item_id = match_item(target, held_item_ids(db, save)) or match_item(
        target, room_item_ids(db, save, save.current_room_id)
    )
    if item_id:
        prefix = "(Evidence) " if is_evidence(db, save, item_id) else ""
        return prefix + item_display_description(db, save, item_id)
    scenery_key = match_scenery(target, room.get("scenery", {}))
    if scenery_key:
        scenery = room["scenery"][scenery_key]
        return swap_text(db, save, scenery["text"], scenery.get("state_descriptions", []))
    return f"You don't see anything special about the {target}."


def handle_combine(db: Session, save: Save, room: dict, rest_words) -> str:
    parsed = parse_combine(rest_words)
    if not parsed:
        return "Combine what with what?"
    left_op = resolve_operand(parsed[0], db, save, room)
    right_op = resolve_operand(parsed[1], db, save, room)
    if not left_op or not right_op:
        return "You don't have both of those to hand."
    if left_op == right_op:
        return "You can't combine that with itself."
    combo = COMBINATIONS.get(frozenset({left_op, right_op}))
    if not combo:
        return "Nothing happens when you combine those."
    requires_flag = combo.get("requires_flag")
    if requires_flag and not has_flag(db, save, requires_flag):
        return combo.get("not_ready_message", "Nothing useful happens yet.")

    spawns_item_id = combo.get("spawns_item_id")
    already_spawned = spawns_item_id and (
        db.query(SaveInventory).filter_by(save_id=save.id, item_id=spawns_item_id).first() is not None
    )
    already_flagged = combo.get("sets_flag") and has_flag(db, save, combo["sets_flag"])
    already_promoted = combo.get("promotes_item_id") and is_evidence(db, save, combo["promotes_item_id"])
    if already_flagged or already_promoted or already_spawned:
        return combo["event_message"]

    if combo["type"] == "consume":
        for operand in (left_op, right_op):
            row = db.query(SaveInventory).filter_by(save_id=save.id, item_id=operand, status="held").first()
            row.status = "consumed"
        db.add(SaveInventory(
            save_id=save.id, item_id=combo["result_item_id"], status="held", acquired_at_turn=save.turn_count,
        ))
    else:  # unlock: originals stay, since real clues shouldn't vanish when used
        if combo.get("sets_flag"):
            db.add(SaveFlag(save_id=save.id, flag_key=combo["sets_flag"], set_at_turn=save.turn_count))
        if combo.get("spawns_item_id"):
            db.add(SaveInventory(
                save_id=save.id, item_id=combo["spawns_item_id"], status="held", acquired_at_turn=save.turn_count,
            ))
        if combo.get("promotes_item_id"):
            db.add(SaveItemPromotion(
                save_id=save.id, item_id=combo["promotes_item_id"], promoted_at_turn=save.turn_count,
            ))
            db.add(SaveEvidenceLog(
                save_id=save.id, evidence_item_id=combo["promotes_item_id"], collected_at_turn=save.turn_count,
            ))
    return combo["event_message"]


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


def items_summary(db: Session, save: Save) -> str:
    held = held_item_ids(db, save)
    if not held:
        return "You aren't carrying anything yet."
    labels = [
        ITEMS[item_id]["name"] + (" (evidence)" if is_evidence(db, save, item_id) else "")
        for item_id in held
    ]
    return "You're carrying: " + ", ".join(sorted(labels)) + "."


def evidence_summary(db: Session, save: Save) -> str:
    rows = (
        db.query(SaveEvidenceLog)
        .filter_by(save_id=save.id)
        .order_by(SaveEvidenceLog.collected_at_turn)
        .all()
    )
    if not rows:
        return "You haven't pieced together anything conclusive yet."
    lines = [ITEMS[row.evidence_item_id]["evidence_description"] for row in rows]
    return "Case file so far:\n" + "\n".join(f"- {line}" for line in lines)


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
    return {"room": room_payload(db, save), "turn_count": save.turn_count}


@app.post("/api/game/action")
def post_action(body: ActionRequest, db: Session = Depends(get_db)):
    save = get_or_create_dev_save(db)
    room = ROOMS[save.current_room_id]
    text = body.input.strip().lower()

    # TODO: meta commands the player will reach for — "what can I do", "where can
    # I go", "help". "Where can I go" is just room["exits"].keys() rendered as a
    # sentence, no new data needed. "What can I do" is less obvious now that
    # items/combine exist too — probably exits + inventory + "combine X with Y"
    # as a syntax hint, but worth deciding deliberately rather than dumping the
    # whole verb list.
    #
    # TODO: teach navigation by playing it, not exposition. The opening room/
    # scene should nudge the player into typing something (e.g. narration that
    # models "go hallway" in passing) rather than a "type HELP" banner or a
    # scripted walkthrough overlay — "places"/"inventory"/"evidence" below and
    # the meta commands above are the fallback net, not the primary onboarding.
    words = text.split()

    if words and words[0] in COMBINE_VERBS:
        message = handle_combine(db, save, room, words[1:])
    else:
        verb, target = parse_command(text)

        if verb in LOOK_VERBS:
            message = handle_examine(db, save, room, target)
        elif verb in TAKE_VERBS:
            message = handle_take(db, save, room, target)
        elif verb in GO_VERBS:
            message = move_with_narration(db, save, room, target) if target else "Go where?"
        elif (
            text in room["exits"]
            or text in room.get("exit_aliases", {})
            or text in room.get("gated_exits", {})
        ):
            message = move_with_narration(db, save, room, text)
        elif text in PLACES_PHRASES:
            message = "You flip open your notebook. " + places_summary(visited_room_names(db, save))
        elif text in ITEMS_PHRASES:
            message = "You check your things. " + items_summary(db, save)
        elif text in EVIDENCE_PHRASES:
            message = evidence_summary(db, save)
        else:
            message = "You're not sure how to do that yet."

    save.turn_count += 1
    ensure_visited(db, save)
    db.commit()
    db.refresh(save)

    return {"message": message, "room": room_payload(db, save), "turn_count": save.turn_count}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
