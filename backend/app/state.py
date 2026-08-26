# EXPLORATION BRANCH (explore/dynamic-state-descriptions): composing
# state-dependent description text for items, scenery, and rooms. See
# plans/initial/dynamic-descriptions-exploration.md for why this exists —
# short version, main's evidence_description swap (main.py's
# item_display_description) already broke the "descriptions stay static"
# rule for one case, and it started to feel inconsistent that nothing else
# gets the same treatment. This is a prototype of a general version, not a
# locked-in pattern.
#
# Two composition strategies, picked per caller depending on what kind of
# change the state represents:
#
# - swap_text: the state SUPERSEDES the base text — you now know something
#   that makes the old wording wrong (e.g. "ready to compare against
#   something" once it's already been compared). Last matching variant in
#   listed order wins, so list variants in escalating order — the same
#   convention evidence_description already used implicitly.
# - layered_text: the state ADDS a note without invalidating the base (e.g.
#   a room description gaining a sentence about an item that's since been
#   taken from it, rather than needing the original sentence rewritten to
#   not mention it). Every matching layer's text is appended, in order.
#
# has_flag/is_evidence/held_item_ids moved here from main.py so this module
# doesn't import from main (main imports from here instead) — same
# functions, no behavior change.

from sqlalchemy.orm import Session

from .models import Save, SaveFlag, SaveInventory, SaveItemPromotion


def has_flag(db: Session, save: Save, flag_key: str) -> bool:
    return db.query(SaveFlag).filter_by(save_id=save.id, flag_key=flag_key).first() is not None


def is_evidence(db: Session, save: Save, item_id: str) -> bool:
    return db.query(SaveItemPromotion).filter_by(save_id=save.id, item_id=item_id).first() is not None


def held_item_ids(db: Session, save: Save) -> set[str]:
    rows = db.query(SaveInventory).filter_by(save_id=save.id, status="held").all()
    return {row.item_id for row in rows}


def condition_met(db: Session, save: Save, condition: dict) -> bool:
    """A condition is a single-key dict naming what kind of check it is.
    Deliberately only one key is read per dict — a condition that needed
    "flag X AND held Y" is a sign the text belongs split into two entries,
    not a reason to add and/or combinators here. "held" is the one
    exception: its value can be an item id, or a list of item ids meaning
    all of them — still one kind of check (what's in the inventory), just
    checking more than one item at a time, e.g. a desk clause that needs to
    read differently once BOTH the candle and the ink pad are gone rather
    than either alone."""
    if "flag" in condition:
        return has_flag(db, save, condition["flag"])
    if "evidence" in condition:
        return is_evidence(db, save, condition["evidence"])
    if "held" in condition:
        target = condition["held"]
        held = held_item_ids(db, save)
        if isinstance(target, list):
            return all(item_id in held for item_id in target)
        return target in held
    raise ValueError(f"Unrecognized condition: {condition!r}")


def swap_text(db: Session, save: Save, base: str, variants: list) -> str:
    result = base
    for variant in variants:
        if condition_met(db, save, variant["condition"]):
            result = variant["text"]
    return result


def layered_text(db: Session, save: Save, base: str, layers: list) -> str:
    parts = [base]
    for layer in layers:
        if condition_met(db, save, layer["condition"]):
            parts.append(layer["text"])
    return " ".join(parts)
