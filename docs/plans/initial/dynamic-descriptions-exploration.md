# Exploration: dynamic per-item-state descriptions

Branch: `explore/dynamic-state-descriptions`. Not merged, not decided —
this is a working prototype to react to, per the original note below.

## The original call

From `DESIGN_NOTES.md`'s evidence-log section: the notebook/case-file
screen was deliberately kept as a running log rather than
conditionally-rewritten text, "so nothing changes silently." That principle
got extended informally to descriptions in general while building the
item/combine system: don't dynamically rewrite descriptions per-item-state,
unless a specific case makes the static version feel awkward — and one
already did. `item_display_description` in `main.py` swaps in
`evidence_description` once an item's promoted, which is exactly the thing
the note said not to do generally. It was allowed as a narrow exception
because promoted-evidence items get an unambiguous, permanent state change
and the swap directly serves the case-solving mechanic.

Once that exception existed, it started feeling arbitrary that nothing else
gets the same treatment — items whose flavor text becomes stale after some
other flag fires (`fingerprint_lifted` still saying "ready to compare"
after the comparison already happened), scenery whose text was written
before a mechanic locked in (the Kitchen hatch saying "if you knew how it
worked" after you've already found out), room descriptions that keep
naming objects sitting on a desk after they've been carried out of the
room. That's the "feels awkward" this branch is exploring.

## What's here

`backend/app/state.py` — two small composition helpers, both driven by the
same one-key condition dicts (`{"flag": ...}`, `{"evidence": ...}`,
`{"held": ...}`):

- **`swap_text`** — the state supersedes the base text. Use when the old
  wording becomes actively wrong once the condition holds (a claim that's
  no longer true). Last matching variant in a listed order wins, so list
  variants in escalating order — the same convention `evidence_description`
  already used implicitly.
- **`layered_text`** — the state appends a note without touching the base
  text. Use when the base is still true but incomplete (the room's fine not
  mentioning that an item's gone, as long as something says so). Every
  matching layer's text is appended, in order.

Applied in three places as demonstrations, not a full pass over all
content:

- **Item** (`items.py`): `fingerprint_lifted` and `timeline_note_kitchen`
  get a `state_descriptions` swap keyed on a flag, generalizing the
  existing `evidence_description` pattern beyond "promoted to evidence."
- **Scenery** (`rooms.py`, Kitchen `hatch`): a `state_descriptions` swap
  keyed on `dumbwaiter_cleared`.
- **Room** (`rooms.py`, Study): a `state_notes` layered list — two entries
  note when `candle_stub`/`ink_pad` have been taken, one notes once the
  glass fragment's been made evidence.

Everything else (Library, Stairs, Garden, all other items) is untouched —
deliberately, so there's a live A/B to compare rather than a wholesale
rewrite to judge in one shot.

## Open questions this doesn't answer yet

- **Combinatorial growth for rooms with more state.** The Study's desk
  demo only has two independent single-item conditions. A room where
  several items/flags interact (a fuller "what's changed here" picture)
  would need either more layers than feels readable, or a real templating
  approach — this prototype doesn't prove out at that scale.
- **swap vs. layer, chosen by feel.** Right now it's a judgment call per
  entry, not a rule. Might be fine (matches how the rest of the content is
  authored) or might need a sharper guideline once there's more of it.
- **Does this fix the awkwardness, or just relocate it?** The alternative
  never explored: leave descriptions static and instead make the *log*
  (notebook/evidence) carry all of the "here's what's changed" weight,
  which was the original design intent. Worth comparing against actually
  playing both branches before deciding.
