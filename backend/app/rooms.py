# Stub room content for UX iteration — not the real case yet.
# Real content and the item/evidence chains live in
# plans/initial/missing-from-the-study-decisions.md; this just gives the
# turn loop somewhere to move around while the frontend gets built out.
#
# Layout is hub-and-spoke rather than a straight chain: Hallway connects
# Study and Library, with Stairs bridging down to Kitchen/Garden. This also
# gives the future Cellar (see the "Room mapping" open decision in
# missing-from-the-study-decisions.md) a natural place to extend from —
# continuing down past Stairs into Kitchen.

STARTING_ROOM = "study"

ROOMS = {
    "study": {
        "name": "Study",
        "description": (
            "Firelight flickers over rows of leather-bound books. A pale "
            "rectangle on the wall marks where a painting used to hang. Near "
            "a cracked windowpane — a few shards still clinging to the frame "
            "— a heavy oak desk holds a candle stub and a small ink pad among "
            "scattered papers. Warm light spills from beneath a door leading "
            "out to the hallway."
        ),
        "exits": {"hallway": "hallway"},
    },
    "hallway": {
        "name": "Hallway",
        "description": (
            "A long hallway runs the length of the house, its runner rug "
            "muffling footsteps. A narrow staircase descends near the far "
            "end, and doors lead off toward the Study and the Library."
        ),
        "exits": {"study": "study", "library": "library", "stairs": "stairs"},
    },
    "library": {
        "name": "Library",
        "description": (
            "Dust motes drift in the lamplight. Someone has been through "
            "these shelves recently — a few books sit slightly askew."
        ),
        "exits": {"hallway": "hallway"},
    },
    "stairs": {
        "name": "Stairs",
        "description": (
            "The staircase turns twice on its way down, its banister worn "
            "smooth by generations of hands. Cooking smells drift up from "
            "below, growing stronger with every step."
        ),
        "exits": {"hallway": "hallway", "kitchen": "kitchen"},
    },
    "kitchen": {
        "name": "Kitchen",
        "description": (
            "Copper pots hang above a cooling stove. A door to the garden "
            "stands slightly ajar, letting in the smell of rain."
        ),
        "exits": {"stairs": "stairs", "garden": "garden"},
    },
    "garden": {
        "name": "Garden",
        "description": (
            "Rain has flattened the beds. A scatter of glass glints in the "
            "grass below the Study's cracked window, and the shed door hangs "
            "half open at the far end of the path."
        ),
        "exits": {"kitchen": "kitchen"},
    },
}
