"""Dev-only tool for inspecting/resetting the local dev-account save.

Talks straight to dev.sqlite3 — not part of the API, never import this from
app/. Run from anywhere:

    backend/.venv/Scripts/python.exe backend/devtool.py show
    backend/.venv/Scripts/python.exe backend/devtool.py reset
    backend/.venv/Scripts/python.exe backend/devtool.py goto kitchen
    backend/.venv/Scripts/python.exe backend/devtool.py visit garden
    backend/.venv/Scripts/python.exe backend/devtool.py wipe
"""

import argparse
import sys

from app.config import DEV_USERNAME
from app.db import Base, SessionLocal, engine
from app.models import Save, SaveEvidenceLog, SaveFlag, SaveInventory, SaveItemPromotion, User, VisitedRoom
from app.rooms import ROOMS, STARTING_ROOM


def get_dev_save(db):
    user = db.query(User).filter_by(username=DEV_USERNAME).first()
    if user is None:
        return None
    return db.query(Save).filter_by(user_id=user.id).first()


def require_dev_save(db):
    save = get_dev_save(db)
    if save is None:
        sys.exit("No dev save yet — load the game in the browser once first.")
    return save


def require_room(room_id):
    if room_id not in ROOMS:
        sys.exit(f"Unknown room '{room_id}'. Options: {', '.join(ROOMS)}")


def cmd_show(db, args):
    save = get_dev_save(db)
    if save is None:
        print("No dev save yet.")
        return
    visited = (
        db.query(VisitedRoom)
        .filter_by(save_id=save.id)
        .order_by(VisitedRoom.first_visited_turn)
        .all()
    )
    print(f"room:       {save.current_room_id} ({ROOMS[save.current_room_id]['name']})")
    print(f"turn_count: {save.turn_count}")
    print(f"status:     {save.status}")
    print(f"visited:    {[v.room_id for v in visited]}")


def cmd_reset(db, args):
    save = require_dev_save(db)
    db.query(VisitedRoom).filter_by(save_id=save.id).delete()
    db.query(SaveInventory).filter_by(save_id=save.id).delete()
    db.query(SaveFlag).filter_by(save_id=save.id).delete()
    db.query(SaveItemPromotion).filter_by(save_id=save.id).delete()
    db.query(SaveEvidenceLog).filter_by(save_id=save.id).delete()
    save.current_room_id = STARTING_ROOM
    save.turn_count = 0
    save.status = "in_progress"
    db.commit()
    print(f"Reset dev save to '{STARTING_ROOM}', turn 0 (inventory, flags, promotions, and evidence log cleared).")


def cmd_goto(db, args):
    require_room(args.room)
    save = require_dev_save(db)
    save.current_room_id = args.room
    db.commit()
    print(f"Moved dev save to '{args.room}'.")


def cmd_visit(db, args):
    require_room(args.room)
    save = require_dev_save(db)
    exists = db.query(VisitedRoom).filter_by(save_id=save.id, room_id=args.room).first()
    if exists is None:
        db.add(VisitedRoom(save_id=save.id, room_id=args.room, first_visited_turn=save.turn_count))
        db.commit()
        print(f"Marked '{args.room}' as visited.")
    else:
        print(f"'{args.room}' was already marked visited.")


def cmd_wipe(db, args):
    db.query(VisitedRoom).delete()
    db.query(Save).delete()
    db.query(User).delete()
    db.commit()
    print("Wiped all rows — next page load starts a fresh dev save.")


COMMANDS = {
    "show": cmd_show,
    "reset": cmd_reset,
    "goto": cmd_goto,
    "visit": cmd_visit,
    "wipe": cmd_wipe,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("show", help="Print the dev save's current state.")
    sub.add_parser("reset", help="Back to the starting room, turn 0, cleared visited list.")

    goto = sub.add_parser("goto", help="Jump the dev save to a room, no travel/turn cost.")
    goto.add_argument("room")

    visit = sub.add_parser("visit", help="Mark a room visited without moving there.")
    visit.add_argument("room")

    sub.add_parser("wipe", help="Delete every row (users, saves, visited_rooms).")

    args = parser.parse_args()

    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        COMMANDS[args.command](db, args)
    finally:
        db.close()


if __name__ == "__main__":
    main()
