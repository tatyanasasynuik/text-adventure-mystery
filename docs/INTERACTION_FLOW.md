# How a Turn Moves Through the Game

Traces one request/response cycle in the backend — from a typed command, through
verb dispatch, to the state change and reply that come back. Sourced from
`backend/app/main.py`. Split into four diagrams so each stays legible; the
overview links out to the other three where the real branching happens.

## The loop

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    Load(["Page loads"]) --> GetState["GET /api/game/state"]
    GetState --> Render["Render room description"]
    Render --> TypeCmd["Player types a command"]
    TypeCmd --> PostAction["POST /api/game/action"]
    PostAction --> ParseVerb{"parse_command"}

    ParseVerb -->|"combine, use"| Combine["handle_combine\n(see Combine & evidence)"]
    ParseVerb -->|"look, examine, x"| Examine["handle_examine\n(see Take & examine)"]
    ParseVerb -->|"take, get, grab"| Take["handle_take\n(see Take & examine)"]
    ParseVerb -->|"go, move, exit name"| Move["try_move\n(see Movement & exits)"]
    ParseVerb -->|"notebook / items / evidence"| Summary["Summary lookups"]
    ParseVerb -->|"unrecognized"| Fallback["\"Not sure how to do that yet.\""]

    Combine --> Turn["turn_count += 1"]
    Examine --> Turn
    Take --> Turn
    Move --> Turn
    Summary --> Turn
    Fallback --> Turn

    Turn --> Commit[("Commit save state to DB")]
    Commit --> Reply["Return { message, room, turn_count }"]
    Reply --> Render
```

Dispatch lives at `backend/app/main.py:393-419`, summaries at `:328-345`.

## Movement & exits

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    Move["try_move(target)"] --> ExitCheck{"exits → aliases →\ngated_exits"}
    ExitCheck -->|"direct exit"| Open["Exit is open"]
    ExitCheck -->|"alias"| Open
    ExitCheck -->|"gated, flag set"| Open
    ExitCheck -->|"gated, flag unset"| Blocked["\"You can't go that way.\""]
    ExitCheck -->|"no match"| Blocked
    Open --> DoMove["Update current room"]
    DoMove --> FirstVisit{"first visit\nto Hallway?"}
    FirstVisit -->|"yes"| Hint["Scripted notebook hint"]
    FirstVisit -->|"no"| Done["Back to the loop"]
    Hint --> Done
```

`backend/app/main.py:47-72`. Rooms form a hub-and-spoke graph (`rooms.py`);
one exit, Cellar → Tunnel, is gated behind the `wine_rack_open` flag.

## Take & examine

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    Take["handle_take(target)"] --> HasItem{"item present\nin room?"}
    HasItem -->|"yes"| AddInv["Add to inventory,\nstatus = held"]
    HasItem -->|"no"| NoItem["\"Nothing like that here.\""]

    Examine["handle_examine(target)"] --> LookupTarget{"held item →\nroom item →\nroom scenery"}
    LookupTarget -->|"found"| Describe["Return description"]
    LookupTarget -->|"none match"| NoExamine["\"Nothing like that here.\""]
```

`backend/app/main.py:226-252`. Take and examine resolve against the same
three pools: held inventory, room items, then fixed room scenery.

## Combine & evidence

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    Combine["handle_combine(text)"] --> SplitOperands["Split on with / and / on"]
    SplitOperands --> ResolveOperands["resolve_operand ×2:\nheld item id or fixture:room:key"]
    ResolveOperands --> ComboLookup{"COMBINATIONS\nfrozenset(a, b)?"}
    ComboLookup -->|"no match"| NoCombo["\"Nothing happens.\""]
    ComboLookup -->|"type = consume"| DoConsume["Remove both,\nspawn new item"]
    ComboLookup -->|"type = unlock"| DoUnlock["Keep both; may set flag,\nspawn item, and/or promote evidence"]
    DoUnlock -.->|"is_evidence"| LogEvidence[("SaveEvidenceLog")]
```

`backend/app/main.py:97-256`. This is the only puzzle mechanic: `consume`
combos burn both ingredients for a new item; `unlock` combos keep the
originals and can flip a flag or log evidence instead. There's no dialogue or
NPC system — "solving" the mystery means chaining combines that promote items
to evidence in the case file log.

## Room map

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    Study <--> Hallway
    Library <--> Hallway
    Hallway <--> Stairs
    Stairs <--> Kitchen
    Kitchen <--> Garden
    Kitchen <--> Cellar
    Cellar -.->|"requires wine_rack_open"| Tunnel
    Tunnel --> Cellar
```

`backend/app/rooms.py`. Hub-and-spoke, not a straight chain: Hallway is the
upstairs hub (Study, Library, Stairs); Stairs bridges down to Kitchen, which
is the downstairs hub (Garden, Cellar). Cellar → Tunnel is the one gated
exit in the house — it stays blocked until the wine-rack combo below sets
`wine_rack_open`. The return trip, Tunnel → Cellar, is never gated.

## Items by room

Every takeable item, grouped by where it's found. Hallway, Stairs, and
Cellar were pure pass-throughs until a redistribution pass gave each of
them a find of their own (pulled out of Study/Kitchen/Library — see
`git show 6a7e877`); combining logic didn't change, since combos only care
about what's held, not where it started. Items with no room
(`room: None` in `items.py`) only exist after a combination spawns them —
listed separately at the bottom.

| Room | Item id | Name |
|---|---|---|
| Study | `candle_stub` | candle stub |
| Study | `ink_pad` | ink pad |
| Study | `magnifying_glass` | magnifying glass |
| Study | `window_glass_fragment` | glass shard |
| Study | `alibi_note` | alibi note |
| Study | `partial_fingerprint` | partial fingerprint |
| Study | `party_polaroid_dress` | dress polaroid |
| Hallway | `answering_machine_tape` | answering machine tape |
| Hallway | `party_guestbook` | guestbook |
| Hallway | `matchbook` | matchbook |
| Stairs | `party_polaroid_group` | group polaroid |
| Library | `tape_player` | tape player |
| Library | `photo_album_locked` | locked photo album |
| Library | `old_appraisal_letter` | appraisal letter |
| Library | `dumbwaiter_diagram` | dumbwaiter diagram |
| Kitchen | `broom_handle` | broom handle |
| Kitchen | `petty_cash_ledger` | petty cash ledger |
| Kitchen | `register_receipt` | receipt |
| Kitchen | `drink_glass` | drink glass |
| Kitchen | `kitchen_prep_schedule` | prep schedule |
| Cellar | `ledger_reconciliation_note` | reconciliation note |
| Cellar | `gambling_iou_note` | IOU note |
| Garden | `crank_handle_broken` | broken crank |
| Garden | `ornate_key` | ornate key |
| Garden | `blueprint_old` | old blueprint |

Non-takeable **scenery** doubles as a combine target via the
`fixture:<room>:<key>` operand form — only three fixtures are ever used that
way: `fixture:cellar:wine_rack`, `fixture:tunnel:passage`, and
`fixture:kitchen:hatch`.

**Spawned only** (produced by a combination, never found in a room):
`crank_jury_rigged`, `lit_candle`, `snagged_thread`, `childhood_photo`,
`fingerprint_lifted`, `timeline_note_kitchen`, `polaroid_dress_detail`.

## Evidence & combination chains

All 22 entries in `items.py`'s `COMBINATIONS`, grouped into the independent
chains they form. Each diagram reads: an item flows into a `+ other operand`
step, which either produces a new item, sets a flag, or promotes something
to evidence (`is_evidence` → logged in `SaveEvidenceLog`). A step marked
"requires" only fires once that flag is already set — combine it too early
and you get the combo's `not_ready_message` instead.

### Tunnel access

Not evidence itself — this chain is what gets you into the Tunnel at all.

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Broom["broom_handle"] --> C1{{"+ crank_handle_broken"}}
    C1 --> Rig("crank_jury_rigged")
    Rig --> C2{{"+ fixture: cellar·wine_rack"}}
    C2 -->|"sets flag"| WineFlag(["wine_rack_open"])
    Candle["candle_stub"] --> C3{{"+ matchbook"}}
    C3 --> Lit("lit_candle")
    Lit --> C4{{"+ fixture: tunnel·passage"}}
    C4 -->|"spawns"| Thread("snagged_thread")
```

### The Niece — phone alibi

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Tape["answering_machine_tape"] --> C1{{"+ tape_player"}}
    C1 -->|"sets flag"| Flag1(["heard_tape_playback"])
    Tape --> C2{{"+ alibi_note\n(requires heard_tape_playback)"}}
    C2 --> Ev1[["EVIDENCE: alibi_note"]]
```

### The Niece — childhood photo

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Key["ornate_key"] --> C1{{"+ photo_album_locked"}}
    C1 --> Photo("childhood_photo")
    Photo --> C2{{"+ magnifying_glass"}}
    C2 -->|"sets flag"| Flag1(["photo_detail_noted"])
    Photo --> C3{{"+ blueprint_old\n(requires photo_detail_noted)"}}
    C3 --> Ev1[["EVIDENCE: childhood_photo"]]
```

### The Niece — dress fabric match

`snagged_thread` here is the item the Tunnel Access chain spawns.
`party_polaroid_group`'s combo is a deliberately independent second path to
the same "opportunity" fact — it doesn't merge with the thread's promotion.

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    PolaroidDress["party_polaroid_dress"] --> C1{{"+ magnifying_glass"}}
    C1 --> Detail("polaroid_dress_detail")
    Thread["snagged_thread\n(from Tunnel Access)"] --> C2{{"+ polaroid_dress_detail"}}
    Detail --> C2
    C2 --> Ev1[["EVIDENCE: snagged_thread"]]
    PolaroidGroup["party_polaroid_group"] --> C3{{"+ magnifying_glass\n(independent 2nd path)"}}
    C3 --> Ev2[["EVIDENCE: party_polaroid_group"]]
```

### The window — entry point

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Glass["window_glass_fragment"] --> C1{{"+ magnifying_glass"}}
    C1 --> Ev1[["EVIDENCE: window_glass_fragment"]]
```

### The Butler — petty cash

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Ledger["petty_cash_ledger"] --> C1{{"+ register_receipt"}}
    C1 -->|"sets flag"| Flag1(["butler_cleared"])
```

### The Family Friend — fingerprint

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Print["partial_fingerprint"] --> C1{{"+ ink_pad"}}
    C1 --> Lifted("fingerprint_lifted")
    Lifted --> C2{{"+ party_guestbook"}}
    C2 -->|"sets flag"| Flag1(["fingerprint_matched_friend"])
    Lifted --> C3{{"+ old_appraisal_letter\n(requires fingerprint_matched_friend)"}}
    C3 -->|"sets flag"| Flag2(["friend_cleared"])
```

### The Son — drink timeline

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Drink["drink_glass"] --> C1{{"+ kitchen_prep_schedule"}}
    C1 --> Note("timeline_note_kitchen")
    Note --> C2{{"+ alibi_note"}}
    C2 -->|"sets flag"| Flag1(["son_timeline_mismatch"])
    IOU["gambling_iou_note"] --> C3{{"+ timeline_note_kitchen\n(requires son_timeline_mismatch)"}}
    Note --> C3
    C3 -->|"sets flag"| Flag2(["son_cleared"])
```

### The Cook & Butler — dumbwaiter

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart LR
    Diagram["dumbwaiter_diagram"] --> C1{{"+ fixture: kitchen·hatch"}}
    C1 -->|"sets flag"| Flag1(["dumbwaiter_cleared"])
    Note["ledger_reconciliation_note"] --> C2{{"+ dumbwaiter_diagram\n(requires dumbwaiter_cleared)"}}
    Diagram --> C2
    C2 -->|"sets flag"| Flag2(["cook_butler_cleared"])
```

## What's not here yet

There's no win/lose state: `Save.status` defaults to `"in_progress"` and
nothing ever reads or changes it — an accusation/solution check is still
unbuilt. That's why these diagrams end at "reply," not at an ending. All the
`_cleared` and `_matched` flags above exist, but nothing yet reads them back
to decide whether the player's eventual accusation is correct.
