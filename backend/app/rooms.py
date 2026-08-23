# Stub room content for UX iteration — not the real case yet.
# Real content and the item/evidence chains live in
# plans/initial/missing-from-the-study-decisions.md; this just gives the
# turn loop somewhere to move around while the frontend gets built out.

STARTING_ROOM = "study"

ROOMS = {
    "study": {
        "name": "Study",
        "description": (
            "Firelight flickers over rows of leather-bound books. A pale "
            "rectangle on the wall marks where a painting used to hang."
        ),
        "exits": {"library": "library"},
    },
    "library": {
        "name": "Library",
        "description": (
            "Dust motes drift in the lamplight. Someone has been through "
            "these shelves recently — a few books sit slightly askew."
        ),
        "exits": {"study": "study", "kitchen": "kitchen"},
    },
    "kitchen": {
        "name": "Kitchen",
        "description": (
            "Copper pots hang above a cooling stove. A door to the garden "
            "stands slightly ajar, letting in the smell of rain."
        ),
        "exits": {"library": "library", "garden": "garden"},
    },
    "garden": {
        "name": "Garden",
        "description": (
            "Rain has flattened the beds. Near the shed, a window pane lies "
            "in pieces on the ground."
        ),
        "exits": {"kitchen": "kitchen"},
    },
}
