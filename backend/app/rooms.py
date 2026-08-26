# Stub room content for UX iteration — not the real case yet.
#
# TODO: the game's title is "This Late Hour" (see the Study's opening line
# below for the first callback). Look for a couple more natural spots to
# echo it as real room/ending content goes in — e.g. a late-night detail in
# the Library or Garden, or the accusation/ending scene once that exists.
# Don't force it into every room; one or two more call-backs is the goal,
# not a repeated tagline.
#
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
        "description": (
            "Firelight flickers over rows of leather-bound books — this late "
            "hour, the rest of the house should be asleep. A pale "
            "rectangle on the wall marks where a painting used to hang. Near "
            "a cracked windowpane — a few shards still clinging to the frame "
            "— a heavy oak desk holds a candle stub and a small ink pad among "
            "scattered papers. Warm light spills from beneath a door leading "
            "out to the hallway."
        ),
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
            },
            "books": {
                "text": "Rows of leather-bound books, undisturbed as far as you can tell.",
                "aliases": ["bookshelves"],
            },
        },
    },
    "hallway": {
        "name": "Hallway",
        "description": (
            "A long hallway runs the length of the house, its runner rug "
            "muffling footsteps. A narrow staircase descends near the far "
            "end, and doors lead off toward the Study and the Library."
        ),
        "exits": {"study": "study", "library": "library", "stairs": "stairs"},
        # "stairs" is the exit's canonical name, but nobody actually says
        # "go stairs" — they say "down" or "downstairs". Aliases resolve to
        # a real exits key in main.py before the exits lookup runs.
        "exit_aliases": {"downstairs": "stairs", "down": "stairs", "descend": "stairs"},
    },
    "library": {
        "name": "Library",
        "description": (
            "Dust motes drift in the lamplight. Someone has been through "
            "these shelves recently — a few books sit slightly askew."
        ),
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
        "description": (
            "The staircase turns twice on its way down, its banister worn "
            "smooth by generations of hands. Cooking smells drift up from "
            "below, growing stronger with every step."
        ),
        "exits": {"hallway": "hallway", "kitchen": "kitchen"},
        "exit_aliases": {
            "up": "hallway", "upstairs": "hallway", "ascend": "hallway",
            "down": "kitchen", "downstairs": "kitchen", "descend": "kitchen",
        },
    },
    "kitchen": {
        "name": "Kitchen",
        "description": (
            "Copper pots hang above a cooling stove. A door to the garden "
            "stands slightly ajar, letting in the smell of rain."
        ),
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
            },
        },
    },
    "cellar": {
        "name": "Cellar",
        "description": (
            "The air turns cool and mineral as you descend. Wine racks line "
            "one wall, thick with dust — except one, bricked up flush "
            "against the stone behind it, its shelves conspicuously empty."
        ),
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
        "description": (
            "The passage beyond the wine rack is narrow and low, cut "
            "straight through old stone. Cold air moves through it from "
            "somewhere — one direction carries the smell of wet earth and "
            "rain, the other a faint thread of warmth and firelight."
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
        },
    },
    "garden": {
        "name": "Garden",
        "description": (
            "Rain has flattened the beds. A scatter of glass glints in the "
            "grass below the Study's cracked window, and the shed door hangs "
            "half open at the far end of the path."
        ),
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
        },
    },
}
