# Stub room content for UX iteration — not the real case yet.
# Real content and the item/evidence chains live in
# plans/initial/missing-from-the-study-decisions.md; the takeable items
# themselves are content, not this file's problem — see items.py.
#
# Layout is hub-and-spoke rather than a straight chain: Hallway connects
# Study and Library, with Stairs bridging down to Kitchen/Garden. Kitchen
# continues down into the Cellar, and the Cellar's wine rack opens onto the
# Tunnel (see the "Room mapping" decision in missing-from-the-study-
# decisions.md — resolved: Cellar off Kitchen, freely walkable; the wine
# rack itself is the gated piece; Tunnel is one small dead-ended room rather
# than a full second network reaching the Garden shed or the Study).
#
# The wine rack is the one exit in the house that isn't always open —
# see "gated_exits" on the Cellar below. It works like a normal exits entry
# except it also carries a requires_flag: try_move refuses the move and
# returns blocked_message until that flag is set (by combining the
# jury-rigged crank with the wine rack, in items.py's COMBINATIONS). Every
# other room's exits are unconditional, so this is deliberately its own
# dict rather than folded into "exits".
#
# "scenery" is examine-only flavor for nouns already named in the room
# description that are never takeable (the desk itself, the wall, the
# window) — as opposed to items.py's takeable objects that happen to sit on
# or near them (the candle stub on the desk, the glass shard in the window).
# Each entry is keyed by a canonical id with its own "text" and "aliases" —
# same shape as items.py's ITEMS, so a player typing any alias always
# resolves to the same canonical id. That matters because a scenery id can
# double as a combine target from items.py's COMBINATIONS via the
# "fixture:<room_id>:<key>" operand form (see the Kitchen's "hatch" below):
# if aliases silently resolved to different ids, "use diagram on the
# dumbwaiter" and "use diagram on the hatch" would hit different fixture
# ids and only one phrasing would ever work.

STARTING_ROOM = "study"

ROOMS = {
    "study": {
        "name": "Study",
        # EXPLORATION: description_parts (see room_description in main.py)
        # composes the room description from clauses resolved independently
        # via swap_text (see state.py), instead of one flat string — so once
        # an item's gone, the clause that named it rewrites to a trace (wax,
        # ink stain) rather than the base sentence staying "holds a candle
        # stub" with a footnote bolted on after it. Each clause is its own
        # {"base", "variants"} dict so the window clause and the desk clause
        # swap on their own conditions without needing every held/not-held
        # combination across the *whole* room spelled out as one variant.
        "description_parts": [
            "Firelight flickers over rows of leather-bound books. A pale "
            "rectangle on the wall marks where a painting used to hang.",
            {
                "base": "Near a cracked windowpane — a few shards still clinging to the frame —",
                "variants": [
                    {
                        "condition": {"held": "window_glass_fragment"},
                        "text": "Near a cracked windowpane, swept clear of glass now —",
                    },
                ],
            },
            {
                "base": "a heavy oak desk holds a candle stub and a small ink pad among scattered papers.",
                "variants": [
                    {
                        "condition": {"held": "ink_pad"},
                        "text": (
                            "a heavy oak desk holds a candle stub among scattered papers, "
                            "beside a smudge of dried ink where the pad used to sit."
                        ),
                    },
                    {
                        "condition": {"held": "candle_stub"},
                        "text": (
                            "a heavy oak desk holds a small ink pad among scattered papers, "
                            "next to a puddle of hardened wax where the candle stub used to sit."
                        ),
                    },
                    {
                        # Both gone reads differently than either alone, so this
                        # comes last and wins over the two single-item variants
                        # above once it's also true — see condition_met's "held"
                        # list note in state.py.
                        "condition": {"held": ["candle_stub", "ink_pad"]},
                        "text": (
                            "a heavy oak desk holds only scattered papers now, save for a "
                            "puddle of hardened wax and a smudge of dried ink marking where "
                            "the candle and ink pad used to sit."
                        ),
                    },
                ],
            },
            "Warm light spills from beneath a door leading out to the hallway.",
        ],
        "state_notes": [
            {
                "condition": {"evidence": "window_glass_fragment"},
                "text": (
                    "Under closer study, you're fairly sure now: that glass broke "
                    "outward, from inside this room."
                ),
            },
        ],
        "exits": {"hallway": "hallway"},
        "scenery": {
            "desk": {
                "text": "The desk itself is heavy old oak, scarred with water rings. Whatever's sitting on top of it is worth its own look.",
                "aliases": ["oak desk"],
            },
            "wall": {
                "text": "A pale rectangle stands out against the darker wallpaper around it — years of a painting keeping the sun off, gone now.",
                "aliases": ["square", "rectangle", "pale rectangle", "mark", "wallpaper"],
            },
            "frame": {
                "text": "The frame's still hanging, empty. Whoever took the painting didn't bother with it — or didn't have time to.",
                "aliases": ["empty frame", "picture frame"],
            },
            "window": {
                "text": "The windowpane is cracked through, a few shards still hanging on in the frame.",
                "aliases": ["windowpane", "cracked window"],
                "state_descriptions": [
                    {
                        "condition": {"held": "window_glass_fragment"},
                        "text": "The windowpane is cracked through — you already picked the loose shard out of the frame.",
                    },
                ],
            },
            "books": {
                "text": "Rows of leather-bound books, undisturbed as far as you can tell.",
                "aliases": ["bookshelves"],
            },
        },
    },
    "hallway": {
        "name": "Hallway",
        "description_parts": [
            "A long hallway runs the length of the house, its runner rug "
            "muffling footsteps. A narrow staircase descends near the far "
            "end, and doors lead off toward the Study and the Library.",
            {
                "base": "Just inside the door, a guestbook lies propped open on a "
                "side table, a half-used matchbook resting beside it.",
                "variants": [
                    {
                        "condition": {"held": "matchbook"},
                        "text": "Just inside the door, a guestbook lies propped open "
                        "alone on the side table now — the matchbook that sat "
                        "beside it is already gone.",
                    },
                    {
                        "condition": {"held": "party_guestbook"},
                        "text": "Just inside the door, a half-used matchbook sits alone "
                        "on the side table now — the guestbook that sat beside it "
                        "is already gone.",
                    },
                    {
                        "condition": {"held": ["matchbook", "party_guestbook"]},
                        "text": "The side table by the door is bare now, both the "
                        "guestbook and the matchbook already taken.",
                    },
                ],
            },
            {
                "base": "Near the house phone, a cassette tape sits ejected from the "
                "old intercom machine, labeled in faded pen with a date and time.",
                "variants": [
                    {
                        "condition": {"held": "answering_machine_tape"},
                        "text": "The old intercom machine by the house phone sits empty "
                        "now — the cassette tape that was ejected from it is already "
                        "gone.",
                    },
                ],
            },
        ],
        "exits": {"study": "study", "library": "library", "stairs": "stairs"},
        # "stairs" is the exit's canonical name, but nobody actually says
        # "go stairs" — they say "down" or "downstairs". Aliases resolve to
        # a real exits key in main.py before the exits lookup runs.
        "exit_aliases": {"downstairs": "stairs", "down": "stairs", "descend": "stairs"},
        "scenery": {
            # EXPLORATION: pure ambiance, not a chain — gives the Houseguest
            # (in the cast table's "Expanded Cast" but with no item chain of
            # her own) a physical trace in the house without inventing a
            # resolution chain for a suspect who's barely in the story.
            "glove": {
                "text": (
                    "A single glove, dropped and half-kicked under the runner rug. "
                    "Not fine enough to be anyone's going-out pair — probably the "
                    "plus-one who spent half the night lost looking for the bathroom."
                ),
                "aliases": ["dropped glove", "single glove"],
            },
        },
    },
    "library": {
        "name": "Library",
        "description_parts": [
            "Dust motes drift in the lamplight. Someone has been through "
            "these shelves recently — a few books sit slightly askew.",
            {
                "base": "On the reading table, an old tape player sits, the kind that "
                "still takes cassettes.",
                "variants": [
                    {
                        "condition": {"held": "tape_player"},
                        "text": "The reading table sits bare now — the tape player "
                        "that sat on it is already gone.",
                    },
                ],
            },
            {
                "base": "Pinned to a corkboard by the door, a manual diagram shows the "
                "dumbwaiter mechanism.",
                "variants": [
                    {
                        "condition": {"held": "dumbwaiter_diagram"},
                        "text": "The corkboard by the door holds only a bare pin now — "
                        "the diagram that hung there is already gone.",
                    },
                ],
            },
            {
                "base": "A small photo album, its clasp lock stuck shut, sits on a lower "
                "shelf beside an old appraisal letter on a dealer's letterhead.",
                "variants": [
                    {
                        "condition": {"held": "photo_album_locked"},
                        "text": "A lower shelf holds just the old appraisal letter now — "
                        "the locked photo album's already been taken.",
                    },
                    {
                        "condition": {"held": "old_appraisal_letter"},
                        "text": "A lower shelf holds just the locked photo album now — "
                        "the appraisal letter's already been taken.",
                    },
                    {
                        "condition": {"held": ["photo_album_locked", "old_appraisal_letter"]},
                        "text": "That lower shelf sits empty now, both the album and the "
                        "letter already gone.",
                    },
                ],
            },
        ],
        "exits": {"hallway": "hallway"},
        "scenery": {
            "shelves": {
                "text": "A few books sit slightly askew, like someone pulled them out and didn't quite line them back up.",
                "aliases": ["books", "bookshelves"],
            },
        },
    },
    "stairs": {
        "name": "Stairs",
        "description_parts": [
            "The staircase turns twice on its way down, its banister worn "
            "smooth by generations of hands. Cooking smells drift up from "
            "below, growing stronger with every step.",
            {
                "base": "A candid Polaroid from the party is tucked into the edge "
                "of a framed photo on the wall — a cluster of guests, mid-laugh, "
                "someone's elbow in frame.",
                "variants": [
                    {
                        "condition": {"held": "party_polaroid_group"},
                        "text": "The framed photo on the wall stands alone now — the "
                        "candid Polaroid tucked into its edge is already gone.",
                    },
                ],
            },
        ],
        "exits": {"hallway": "hallway", "kitchen": "kitchen"},
        "exit_aliases": {
            "up": "hallway", "upstairs": "hallway", "ascend": "hallway",
            "down": "kitchen", "downstairs": "kitchen", "descend": "kitchen",
        },
    },
    "kitchen": {
        "name": "Kitchen",
        # EXPLORATION: several items live in this one room, so unlike the
        # Study's paired desk clause, most of these are their own
        # single-item clause rather than grouped — a compound "all taken"
        # variant only makes sense for items actually described together
        # (the ledger and its tucked-in receipt). Each clause still swaps to
        # a trace independently once its item's gone.
        "description_parts": [
            "Copper pots hang above a cooling stove. A door to the garden "
            "stands slightly ajar, letting in the smell of rain.",
            {
                "base": "A broom leans in the corner, its handle looking about the "
                "right length and thickness for something.",
                "variants": [
                    {
                        "condition": {"held": "broom_handle"},
                        "text": "The corner where a broom used to lean is empty now.",
                    },
                ],
            },
            {
                "base": "On the counter, the household's petty cash ledger sits open, "
                "a grocery receipt tucked in with it.",
                "variants": [
                    {
                        "condition": {"held": "register_receipt"},
                        "text": "On the counter, the petty cash ledger sits open, the "
                        "receipt that was tucked into it already gone.",
                    },
                    {
                        "condition": {"held": "petty_cash_ledger"},
                        "text": "On the counter, a grocery receipt lies alone now — the "
                        "ledger it was tucked into has already been taken.",
                    },
                    {
                        "condition": {"held": ["petty_cash_ledger", "register_receipt"]},
                        "text": "The counter's mostly bare now — both the ledger and its "
                        "tucked-in receipt already taken.",
                    },
                ],
            },
            {
                "base": "A drink glass, half-full and still cold, sits on the counter.",
                "variants": [
                    {
                        "condition": {"held": "drink_glass"},
                        "text": "A faint ring of condensation on the counter is all "
                        "that's left of a drink glass that was sitting there.",
                    },
                ],
            },
            {
                "base": "The Cook's handwritten prep schedule is pinned to the wall.",
                "variants": [
                    {
                        "condition": {"held": "kitchen_prep_schedule"},
                        "text": "A bare pin on the wall marks where the Cook's prep "
                        "schedule used to hang.",
                    },
                ],
            },
        ],
        "exits": {"stairs": "stairs", "garden": "garden", "cellar": "cellar"},
        "exit_aliases": {
            "upstairs": "stairs", "up": "stairs", "ascend": "stairs",
            "downstairs": "cellar", "down": "cellar", "descend": "cellar",
        },
        "scenery": {
            "stove": {
                "text": "A cooling stove, pots still hanging above it from dinner service.",
                "aliases": ["cooling stove"],
            },
            "pots": {
                "text": "Copper pots, hung in a neat row.",
                "aliases": ["copper pots"],
            },
            "hatch": {
                "text": "A small hatch set into the wall — a dumbwaiter. Looks like it could move something between floors unseen, if you knew how it worked.",
                "aliases": ["dumbwaiter hatch", "dumbwaiter"],
                # EXPLORATION: swap_text (see state.py) — this scenery text
                # said "if you knew how it worked" before the diagram combo;
                # after dumbwaiter_cleared fires, that phrasing is just
                # wrong (you do know, and it's a dead end), so this
                # supersedes rather than appends like the Study's notes do.
                "state_descriptions": [
                    {
                        "condition": {"flag": "dumbwaiter_cleared"},
                        "text": (
                            "A small hatch set into the wall — a dumbwaiter. You've "
                            "already checked it against the diagram: it only ever ran "
                            "Kitchen to Dining, and it's too small regardless. Whatever "
                            "happened, it didn't happen this way."
                        ),
                    },
                ],
            },
        },
    },
    "cellar": {
        "name": "Cellar",
        "description_parts": [
            "The air turns cool and mineral as you descend. Wine racks line "
            "one wall, thick with dust — except one, bricked up flush "
            "against the stone behind it, its shelves conspicuously empty.",
            {
                "base": "Wedged into a gap in the nearest wine rack, a short note in "
                "a different hand sits half-hidden — someone helping square the "
                "household books.",
                "variants": [
                    {
                        "condition": {"held": "ledger_reconciliation_note"},
                        "text": "That gap in the wine rack is empty now — the note "
                        "wedged into it is already gone.",
                    },
                ],
            },
            {
                "base": "Behind a stack of crates, a folded IOU note is tucked out of "
                "sight — someone owes someone else, badly.",
                "variants": [
                    {
                        "condition": {"held": "gambling_iou_note"},
                        "text": "The gap behind the crates is empty now — the folded "
                        "IOU note that was tucked there is already gone.",
                    },
                ],
            },
        ],
        "exits": {"kitchen": "kitchen"},
        "exit_aliases": {"up": "kitchen", "upstairs": "kitchen", "ascend": "kitchen"},
        "gated_exits": {
            "tunnel": {
                "target": "tunnel",
                "requires_flag": "wine_rack_open",
                "blocked_message": "The wine rack is bricked up solid — there's no way through, not yet.",
            },
        },
        "scenery": {
            "wine_rack": {
                "text": "A wine rack built into the wall, shelves empty, its backing bricked up solid. There's a housing on one side, like something's missing that ought to turn it.",
                "aliases": ["wine rack", "rack", "bricked-up wine rack", "bricked up wine rack"],
            },
        },
    },
    "tunnel": {
        "name": "Tunnel",
        # EXPLORATION: "initials" and "tin" are pure ambiance — no combo, no
        # evidence, nothing required reads their text. The Tunnel's on the
        # required path (Chain A lights the candle and finds snagged_thread
        # here), so it's a guaranteed audience for two lines establishing
        # "this place is old and forgotten," not a lead to chase.
        "description": (
            "The passage beyond the wine rack is narrow and low, cut "
            "straight through old stone. Cold air moves through it from "
            "somewhere — one direction carries the smell of wet earth and "
            "rain, the other a faint thread of warmth and firelight. Here "
            "and there the stone bears older marks — scratched initials "
            "with a date long past, and something small and rusted wedged "
            "into a crack near the floor."
        ),
        "exits": {"cellar": "cellar"},
        "exit_aliases": {"back": "cellar", "out": "cellar"},
        "scenery": {
            "passage": {
                "text": (
                    "The stone here is worn smooth in a line at about shoulder height — "
                    "like something's been dragged past this spot more than once."
                ),
                "aliases": ["wall", "tunnel wall", "stonework", "far end"],
            },
            "initials": {
                "text": (
                    "A set of initials and a date, scratched into the stone at "
                    "about waist height. The date's decades old — whoever left "
                    "this passed through long before tonight, and never came "
                    "back to add to it."
                ),
                "aliases": ["carving", "carved initials", "scratches", "marks", "date"],
            },
            "tin": {
                "text": (
                    "A small rusted tin, wedged into a crack near the floor, its "
                    "lid long gone. Whatever it once held, someone left it here "
                    "and forgot about it a long time ago."
                ),
                "aliases": ["rusted tin", "old tin", "can", "tin can"],
            },
        },
    },
    "garden": {
        "name": "Garden",
        "description_parts": [
            "Rain has flattened the beds. A scatter of glass glints in the "
            "grass below the Study's cracked window, and the shed door hangs "
            "half open at the far end of the path, muddy boot prints crossing "
            "back and forth near it.",
            {
                "base": "Just inside the shed, a rolled floor plan lies half-tucked "
                "under a workbench, and a broken crank handle sits abandoned "
                "nearby, its shaft missing entirely.",
                "variants": [
                    {
                        "condition": {"held": "blueprint_old"},
                        "text": "Just inside the shed, a broken crank handle sits "
                        "abandoned, its shaft missing entirely — the rolled floor "
                        "plan that was tucked under the workbench is already gone.",
                    },
                    {
                        "condition": {"held": "crank_handle_broken"},
                        "text": "Just inside the shed, a rolled floor plan lies "
                        "half-tucked under a workbench — the broken crank handle "
                        "that sat nearby is already gone.",
                    },
                    {
                        "condition": {"held": ["blueprint_old", "crank_handle_broken"]},
                        "text": "The shed's mostly empty now, both the floor plan and "
                        "the broken crank handle already taken.",
                    },
                ],
            },
            {
                "base": "Near the path, an overturned flowerpot half-buries a small "
                "ornate key.",
                "variants": [
                    {
                        "condition": {"held": "ornate_key"},
                        "text": "The overturned flowerpot lies empty now, the ornate key "
                        "that was half-buried beneath it already taken.",
                    },
                ],
            },
        ],
        "exits": {"kitchen": "kitchen"},
        "scenery": {
            "shed": {
                "text": "The shed door hangs half open. Whatever was in here has been picked through.",
                "aliases": ["shed door"],
            },
            "flowerpot": {
                "text": "An overturned flowerpot, half-sunk in the mud.",
                "aliases": ["pot", "flowerpots"],
            },
            "flowerbed": {
                "text": "The beds are flattened flat by the rain, nothing growing back yet.",
                "aliases": ["beds", "flower beds"],
            },
            # EXPLORATION: pure ambiance, not a chain — reinforces the
            # existing Gardener/window red herring (Chain D already clears
            # the outside-break-in theory) without inventing a new combo.
            "boot_prints": {
                "text": (
                    "A trail of muddy boot prints runs from the shed toward the "
                    "fence and back again, going nowhere near the house. The "
                    "Gardener's, probably, checking the beds before the rain "
                    "really set in."
                ),
                "aliases": ["boot prints", "footprints", "muddy prints", "tracks"],
            },
        },
    },
}
