# Plan: Save & Load (Per Account)

Framing doc for build-order step 4 in [`DESIGN_NOTES.md`](initial/DESIGN_NOTES.md) ("Save/load tied to logged-in user") and the `users` / `player_saves` relationship flagged in [`LEARNING_GOALS.md`](initial/LEARNING_GOALS.md) §2. This is the missing piece between the static case content in `DESIGN_NOTES.md`'s data model (items, promotions, combinations, solution) and an actual player sitting down, playing, closing the tab, and coming back later on the same account.

---

## What "save state" actually is here

The data model in `DESIGN_NOTES.md` describes **content** — the fixed shape of the case (which items exist, what they combine into, what the solution is). None of that changes per player. What *does* change per player, and is what needs saving, is:

- Current room
- Which items are in inventory vs. still in the world vs. consumed entirely (combine-and-consume, per the case doc, destroys originals)
- Which items have been **promoted** item → evidence (this is per-playthrough, not global — the `type` field on an item in `DESIGN_NOTES.md` can't just live on the item row itself, or two players would share promotion state)
- Which flags/unlocks have fired (`heard_tape_playback`, `photo_detail_noted`, time-gated unlocks, etc. — see `missing-from-the-study-decisions.md`)
- The evidence log (ordered list, powers the notebook screen)
- The in-game turn counter (drives time-gated unlocks)
- Whether the game is finished, and which ending was reached

So "save/load" here isn't a generic blob-of-JSON feature bolted on later — it's the per-player instantiation of the static content model. Worth building right after the content tables exist, not after the whole game is otherwise working.

---

## Schema

Extends the `items` / `promotion_events` / `combinations` / `solution` tables already sketched in `DESIGN_NOTES.md`. New tables:

```
saves: {
  id, user_id (FK -> users.id, UNIQUE),   -- one active save per account, see below
  current_room_id,
  turn_count,                              -- in-game clock, drives time-gated unlocks
  status: "in_progress" | "ended_true" | "ended_partial" | "ended_wrong",
  created_at, updated_at
}

save_inventory: {
  save_id (FK), item_id (FK),
  status: "held" | "consumed",             -- consumed = combined away, no longer exists anywhere
  acquired_at_turn
  -- PK (save_id, item_id)
}

save_item_promotions: {
  save_id (FK), item_id (FK),
  promoted_at_turn
  -- PK (save_id, item_id)
  -- presence of a row = this item is type "evidence" for this save; absence = still base "item"
  -- avoids duplicating item content per-save; the base item/evidence_description text stays in `items`
}

save_flags: {
  save_id (FK), flag_key, set_at_turn
  -- PK (save_id, flag_key)
  -- covers unlock-type combination results that aren't items: heard_tape_playback, photo_detail_noted, etc.
}

save_evidence_log: {
  save_id (FK), evidence_item_id (FK), collected_at_turn
  -- PK (save_id, evidence_item_id), read ordered by collected_at_turn
  -- this is what renders the notebook/case-file screen — a log, not a re-derived query, so ordering is stable
}
```

An item's starting room is content data (lives with `items`, not with the save). At load time, "what's in room X" = every item whose default room is X, **minus** anything in that save's `save_inventory` (held or consumed) — no separate "removed from room" table needed.

### Why normalize instead of one JSON blob column

A single `state jsonb` column on `saves` would work and is less code. Deliberately not recommending it here because:

- `LEARNING_GOALS.md` §2 specifically calls for practicing joins and FK relationships as a milestone — a blob column skips that.
- The evidence log and inventory both need **ordering and set-membership queries** ("has this save collected all 3 required evidence items?") which are natural joins/`WHERE` clauses against normalized tables, and awkward against JSON.
- `save_flags` is the one place a loose key/value shape is legitimate even normalized, because the flags in `missing-from-the-study-decisions.md` are genuinely ad hoc per puzzle chain (unlike items, which are already a real table).

If this ever feels like overkill mid-build, collapsing `save_flags` + `save_item_promotions` into a single `save_state jsonb` column is a reasonable fallback — but start normalized, since the whole point of this project is the reps.

---

## Save model: single continuous autosave, not save slots

Recommendation: **one active save per user**, autosaved on every state-changing action — not a "Save Game" button, not multiple slots.

Reasoning:
- The `saves.user_id` column is `UNIQUE`, so "load" is just "does a save row exist for this user" — no save-picker UI needed.
- Every endpoint that mutates game state (move room, combine items, examine, accuse) writes through to the DB in the same request/transaction that computes the result. There's no separate "save point" a player can miss — this sidesteps an entire class of "I forgot to save" bugs and matches how most modern browser games behave.
- This keeps the learning-goal focus where `LEARNING_GOALS.md` puts it (auth, sessions, DB relationships, hosting) instead of spending build time on a save-slot UI that's orthogonal to those goals.
- Multiple save slots / multiple concurrent playthroughs per account is a legitimate stretch goal later (loosen the `UNIQUE` constraint to a normal FK, add a save-picker) — but only after v1 works end to end.

### Flow

- **New account / first play:** on first authenticated request to the game route, if no `saves` row exists for `user_id`, create one at the case's defined starting room/turn 0.
- **Load:** `GET /api/game/state` — authenticated via session cookie → look up `user_id` → fetch `saves` row + join `save_inventory`, `save_item_promotions`, `save_flags`, `save_evidence_log` → return current room description, inventory (with correct item/evidence descriptions), and evidence log to the client. This is what runs on every page load/refresh, so a player closing the tab and coming back "just works."
- **Act:** `POST /api/game/action` (move / examine / combine / use) — server validates the action against current save state + the content tables, computes the result, writes the relevant row updates (inventory, promotions, flags, evidence log, turn_count) in one transaction, returns the updated state. Client never computes game logic itself, only renders what the server returns — keeps the puzzle/solution logic un-spoofable from devtools.
- **Accuse (end game):** `POST /api/game/accuse` — compares `save_evidence_log` against `solution.required_evidence` / `sufficient_evidence`, sets `saves.status` to the matching ending, returns the ending text. Further `/api/game/action` calls should reject once `status != "in_progress"`.
- **Restart:** `POST /api/game/new` — only meaningful once `status != "in_progress"`; wipes the save's child rows and resets `current_room_id`/`turn_count`/`status` rather than deleting and re-creating the `saves` row (keeps the same `id`, simpler FKs).

### Why account-tied, not session-tied

Keying `saves` off `user_id` (not the session/cookie) is what actually delivers "save and load for their account" — same save shows up on a different browser or device after logging in again, since it's a DB row, not client or session storage. The session cookie's only job here is answering "which `user_id` is making this request" (ties directly into the auth/cookies learning goals) — it never carries game state itself.

---

## Open decisions

- [ ] Confirm single-save-per-account for v1 (recommendation above) vs. building save slots from the start
- [ ] Where `turn_count` increments — every action, or only "significant" ones (room moves, combines)? Affects how time-gated unlocks in `missing-from-the-study-decisions.md` feel to play
- [ ] What "restart" does to the notebook/evidence log UI — instant reset, or a confirmation step given there's no undo
- [ ] Whether `save_item_promotions` needs its own `evidence_description` override or can always reuse the one on `items.evidence_description` (current assumption: the latter, since evidence text isn't per-player)
