# Design Notes: Text Adventure Mystery Project

Consolidated from earlier planning conversations — stack decisions, data model, and case design. Meant to sit alongside `LEARNING_GOALS.md` in the repo so Claude Code has the same context.

---

## Stack

- **Backend:** Node/Express or Python/FastAPI — pick whichever you're stronger in
- **Auth:** don't roll your own from scratch to start. Passport.js (Node) or FastAPI-Users, or a simpler sessions + bcrypt setup. Explore JWTs later once that's solid.
- **Database:** Postgres or SQLite to start (users, save states, story progress) — Postgres if you want production-realistic practice
- **Frontend:** plain HTML/CSS/JS, or React for extra frontend reps. UI is mostly a scrolling log + input box.
- **Hosting:** Railway, Render, or Fly.io — easiest for a full-stack app with a DB, free/cheap tiers, straightforward deploys

**Suggested build order:**
1. Scaffold backend + DB, get signup/login working end-to-end first
2. Minimal game engine: rooms/nodes as data (JSON or DB table), player location tied to session
3. Bare-bones frontend hitting the API, rendering room text + choices
4. Save/load tied to logged-in user
5. Polish — styling, maybe a simple admin view for authoring story content

---

## Game concept

Text-based mystery / logic puzzle. Design backwards from the solution: decide who did it, why, how, and what evidence exists, before writing scenes — keeps every clue logically consistent instead of retrofitted.

**Scaffold order for the case itself:**
1. The crime, concretely — what happened, step by step, in real time, who/what/when/why (write it like an answer key, not a story)
2. Culprit's motive + means + opportunity
3. Timeline of events before/during/after — source for alibis and time-gated events later

**Clue design:**
- List every fact the player needs to solve it
- For each, decide where/how it's discovered (room, NPC conversation, item)
- Each key fact should have at least 2 discovery paths (players miss things)
- Red herrings: 1–2 max, and resolvable — not just noise

**Suspect design:** 3–5 suspects, each with a motive, an alibi (true or crackable), and one catchable inconsistency.

**Solving mechanic:** accusation — player presents evidence + names a suspect at the end. Wrong/insufficient evidence leads to a weaker or wrong ending.

### Example case sketch (from planning — adjust as needed)
- 4 rooms, 3 suspects, 5 evidence items, 2–3 combine interactions, one time-gated inconsistency
- Evidence example: muddy footprints inside (implicates Butler — no mud near garden entry); broken window glass (combine with magnifying glass → reveals glass fell outward, clearing the "break-in" theory); debt letter (motive); guest list + timeline note (unaccounted-for window); partial fingerprint on a frame (combine with ink pad → match)
- Required evidence for the true ending: footprints, glass direction, timing note (the core logical chain). Debt letter and fingerprint are supporting/bonus.

---

## Data model

### Items & evidence promotion
Items start as plain inventory objects. When a combo/trigger fires, the item is **reclassified** from item → evidence: its description updates, and an explicit event message fires at that moment (not a silent mutation the player might miss on re-examine).

```
items: {
  id, name, description, type: "item" | "evidence",
  evidence_description: (only set once promoted)
}

promotion_events: {
  trigger: (item_a_id, item_b_id) or (flag),
  promotes_item_id,
  new_description,
  event_message,   // the "aha" text shown at the moment of discovery
  adds_to_evidence_log: true
}
```

Why: the player isn't relying on memory to re-check items — the notification fires right when it matters. The item→evidence transition is a real state change, easy to reason about and query ("show all evidence") for both the notebook and the accusation scene.

### Combinations (consume vs unlock, with time gating)

```
combinations: {
  (item_a_id, item_b_id): {
    type: "consume" | "unlock",
    result_item_id: (if consume),
    unlock_flag / unlock_dialogue_id / unlock_event_id: (if unlock),
    description_on_combine,
    requires: { flags: [...], min_game_time: X, after_event: Y }  // gating conditions
  }
}
```

- **Consume → new item:** e.g. `wire + battery` → `makeshift_torch` (originals gone). Good for practical/tool items.
- **Unlock → flag/dialogue, items stay:** e.g. `photograph + magnifying_glass` sets a flag and unlocks a new question for a suspect. Evidence-type combos should generally be unlock, not consume — real clues shouldn't disappear once used.
- **Time-gated unlock:** sets a flag plus `unlocks_at: game_time + N`. Checking that thread before then returns a "not yet" message. Good for stakeouts, lab results, a suspect needing time to slip up. Keep the in-game clock simple — a turn/scene counter rather than real time.

### Evidence log / accusation

```
solution: {
  correct_suspect_id,
  required_evidence: [flag_ids],   // must have ALL of these for the full/true ending
  sufficient_evidence: [flag_ids], // any N of these also works, if you want a flexible bar
}

endings: {
  correct_full: "...",       // all required evidence presented
  correct_partial: "...",    // right suspect, missing evidence
  wrong_suspect: "...",      // accused someone else
}
```

- Each promoted (unlock-type) evidence item appends to an `evidence_collected: [flag_id]` list on the player's session, ordered by discovery time
- A "notebook"/case-file screen just lists these — running log, not conditionally-rewritten text, so nothing changes silently
- The evidence list doubles as a soft hint system (players cross-reference what they've collected) and gates the accusation scene (can't attempt it until some minimum evidence threshold is met)

---

## Open decisions / not yet locked in
- Final backend language choice (Node vs Python)
- Actual case content (real suspects/evidence/solution beyond the example sketch above)
- Whether frontend is plain JS or React
