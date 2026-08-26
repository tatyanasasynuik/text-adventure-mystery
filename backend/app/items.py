# Item and combination content for the case, per
# plans/initial/missing-from-the-study-decisions.md. Static content, same
# pattern as ROOMS in rooms.py — per-player state (who's holding what, which
# flags are set, what's been promoted to evidence) lives in the save_*
# tables in models.py, not here.
#
# Chain A now runs end to end: crank_jury_rigged opens the Cellar's wine
# rack (a gated exit — see the note atop ROOMS in rooms.py), which leads to
# the Tunnel, where the lit candle reveals the passage and the snagged
# thread. Chain I's polaroid+magnifying-glass combo still stands as an
# independent *second* discovery path for the same opportunity fact (per
# missing-from-the-study-decisions.md's "each key fact needs 2 discovery
# paths") — it promotes party_polaroid_group on its own, deliberately not
# unified with snagged_thread's promotion, since there's no accusation/
# solution-checking logic yet to decide whether two evidence rows proving
# the same fact should collapse into one requirement or count separately.

ITEMS = {
    # --- Study ---
    "candle_stub": {
        "name": "candle stub",
        "room": "study",
        "description": "A short stub of candle, half-melted, still sitting in a puddle of old wax on the desk.",
    },
    "ink_pad": {
        "name": "ink pad",
        "room": "study",
        "description": "A small stamp pad, the ink inside gone slightly tacky with age. Useful for lifting a print off something, if you had reason to.",
    },
    "magnifying_glass": {
        "name": "magnifying glass",
        "room": "study",
        "description": "A brass-handled magnifying glass, heavier than it looks. The kind of thing that rewards close looking.",
    },
    "window_glass_fragment": {
        "name": "glass shard",
        "room": "study",
        "description": "A shard of windowpane, sharp-edged, still clinging to the cracked frame.",
        "evidence_description": "A shard of windowpane. Under magnification the fracture lines fan outward from the outside face — this glass broke from an impact inside the room, not out.",
    },
    "alibi_note": {
        "name": "alibi note",
        "room": "study",
        "description": "A page from the guest timeline, noting who claimed to be where and when. The Niece's line reads: \"phone call, cellar, ~15 min.\"",
        "evidence_description": "The guest timeline note. The Niece's claimed call time lines up exactly with the tape's background room tone — a tone that isn't the Cellar's.",
    },
    "partial_fingerprint": {
        "name": "partial fingerprint",
        "room": "study",
        "description": "A partial print, barely visible in the dust on the empty frame's edge.",
    },
    "party_polaroid_dress": {
        "name": "dress polaroid",
        "aliases": ["polaroid of her dress", "dress photo"],
        "room": "study",
        "description": "A party-favor Polaroid of the Niece, showing off her dress in full for the camera — she'd had it out all night.",
    },

    # --- Hallway ---
    # Entryway-adjacent finds — moved here from the Study/Kitchen so the
    # Hallway isn't a pure pass-through room. See dynamic-descriptions-
    # exploration's item-distribution follow-up.
    "answering_machine_tape": {
        "name": "answering machine tape",
        "room": "hallway",
        "description": "A cassette tape from the old house intercom, labeled in faded pen with a date and time.",
    },
    "party_guestbook": {
        "name": "guestbook",
        "room": "hallway",
        "description": "The guestbook everyone signed on arrival, propped open near the door.",
    },
    "matchbook": {
        "name": "matchbook",
        "room": "hallway",
        "description": "A half-used matchbook from a local restaurant.",
    },

    # --- Stairs ---
    "party_polaroid_group": {
        "name": "group polaroid",
        "aliases": ["polaroid", "candid polaroid"],
        "room": "stairs",
        "description": "A candid Polaroid from earlier in the party — a cluster of guests, mid-laugh, someone's elbow in frame.",
        "evidence_description": "The candid Polaroid. Magnified, a blurred figure in the background is caught heading for the Kitchen/Cellar door — right around the time the Niece says she was on the phone.",
    },

    # --- Library ---
    "tape_player": {
        "name": "tape player",
        "room": "library",
        "description": "An old but functional tape player, the kind that still takes cassettes.",
    },
    "photo_album_locked": {
        "name": "locked photo album",
        "room": "library",
        "description": "A small photo album, its clasp lock stuck shut.",
    },
    "old_appraisal_letter": {
        "name": "appraisal letter",
        "room": "library",
        "description": "An old letter on a dealer's letterhead, referencing past offers to buy the missing painting — all declined.",
    },
    "dumbwaiter_diagram": {
        "name": "dumbwaiter diagram",
        "room": "library",
        "description": "A pinned-up manual diagram for the dumbwaiter mechanism.",
    },

    # --- Kitchen ---
    "broom_handle": {
        "name": "broom handle",
        "room": "kitchen",
        "description": "A broom, its handle just about the right length and thickness for something.",
    },
    "petty_cash_ledger": {
        "name": "petty cash ledger",
        "room": "kitchen",
        "description": "The household's petty cash ledger, entries in a careful hand.",
    },
    "register_receipt": {
        "name": "receipt",
        "room": "kitchen",
        "description": "A grocery receipt, tucked in with the ledger.",
    },
    "drink_glass": {
        "name": "drink glass",
        "room": "kitchen",
        "description": "A drink glass, half-full and still cold to the touch.",
    },
    "kitchen_prep_schedule": {
        "name": "prep schedule",
        "room": "kitchen",
        "description": "The Cook's handwritten timing notes for the evening's courses.",
    },

    # --- Cellar ---
    "ledger_reconciliation_note": {
        "name": "reconciliation note",
        "room": "cellar",
        "description": "A short note tucked out of sight, in a different hand — someone helping square the books.",
    },
    "gambling_iou_note": {
        "name": "IOU note",
        "room": "cellar",
        "description": "A folded IOU, tucked out of sight down here. Someone owes someone else, badly.",
    },

    # --- Garden ---
    "crank_handle_broken": {
        "name": "broken crank",
        "room": "garden",
        "description": "A crank handle from the shed, obviously incomplete — its shaft is missing entirely.",
    },
    "ornate_key": {
        "name": "ornate key",
        "room": "garden",
        "description": "A small ornate key, buried under an overturned flowerpot.",
    },
    "blueprint_old": {
        "name": "old blueprint",
        "room": "garden",
        "description": "A rolled floor plan, older than the current one on file. It shows more house than currently seems to exist.",
    },

    # --- Spawned only (produced by combos, not found in a room) ---
    "crank_jury_rigged": {
        "name": "jury-rigged crank",
        "room": None,
        "description": "The broken crank, given a new shaft from a broom handle. Sturdy enough to turn something — the housing on the Cellar's wine rack looks about right.",
    },
    "lit_candle": {
        "name": "lit candle",
        "room": None,
        "description": "The candle stub, lit off a match. It won't stay lit forever, but it's enough to see by somewhere dark — like the Tunnel.",
    },
    "snagged_thread": {
        "name": "snagged thread",
        "room": None,
        "description": "A thread, snagged on the tunnel's rough stone and pulled loose. Too fine for workman's canvas — this came off someone's clothes.",
        "evidence_description": "The snagged thread, matched against the Polaroid's close-up of the Niece's dress — same fabric, same weave. She was in that tunnel.",
    },
    "polaroid_dress_detail": {
        "name": "dress fabric detail",
        "room": None,
        "description": "A close-up of the dress's fabric and hem, picked out under the glass. A distinctive weave — you'd know it if you saw it again.",
    },
    "childhood_photo": {
        "name": "childhood photo",
        "room": None,
        "description": "A photo from the album: a young girl playing near what looks like the Cellar or the garden shed, years before the current owners.",
        "evidence_description": "The childhood photo, cross-checked against the old blueprint's floor plan. The girl in it — the Niece — is playing right on top of where the hidden passage runs.",
    },
    "fingerprint_lifted": {
        "name": "lifted fingerprint",
        "room": None,
        "description": "The partial print, lifted cleanly with the ink pad. Ready to compare against something.",
        # EXPLORATION: state_descriptions swap the examine text once a flag
        # fires, same convention items.py already used for
        # evidence_description but generalized to any flag, not just
        # "promoted to evidence" — see state.py.
        "state_descriptions": [
            {
                "condition": {"flag": "fingerprint_matched_friend"},
                "text": (
                    "The partial print, lifted cleanly with the ink pad — already "
                    "matched against the guestbook. It's the Family Friend's."
                ),
            },
        ],
    },
    "timeline_note_kitchen": {
        "name": "kitchen timeline note",
        "room": None,
        "description": "A quick cross-check of the drink's temperature against the Cook's prep schedule — whoever poured this has been gone a while.",
        "state_descriptions": [
            {
                "condition": {"flag": "son_timeline_mismatch"},
                "text": (
                    "A quick cross-check of the drink's temperature against the Cook's "
                    "prep schedule — already checked against the Son's claimed \"just got "
                    "a drink,\" and the gap's too long for that alone."
                ),
            },
        ],
    },
}

# Combinations are keyed by a frozenset of two operand ids. An operand is
# either an item id (must be held in inventory) or a room fixture id in the
# form "fixture:<room_id>:<scenery_key>" (must be examinable in the current
# room's scenery — see ROOMS[room]["scenery"] in rooms.py).
COMBINATIONS = {
    frozenset({"broom_handle", "crank_handle_broken"}): {
        "type": "consume",
        "result_item_id": "crank_jury_rigged",
        "event_message": "You lash the broom handle into the crank as a makeshift shaft. It turns freely now — you just need something for it to turn.",
    },
    frozenset({"candle_stub", "matchbook"}): {
        "type": "consume",
        "result_item_id": "lit_candle",
        "event_message": "You strike a match and light the candle stub. It won't stay lit forever — better find somewhere dark to use it.",
    },
    frozenset({"crank_jury_rigged", "fixture:cellar:wine_rack"}): {
        "type": "unlock",
        "sets_flag": "wine_rack_open",
        "event_message": "You fit the crank into the housing and turn. With a grinding shudder, the wine rack swings away from the wall, revealing a black gap beyond — a tunnel mouth.",
    },
    frozenset({"lit_candle", "fixture:tunnel:passage"}): {
        "type": "unlock",
        "spawns_item_id": "snagged_thread",
        "event_message": "By candlelight the passage keeps going, worn smooth toward what has to be the Study's foundation wall. Caught on the rough stone at shoulder height, a single snagged thread.",
    },
    frozenset({"answering_machine_tape", "tape_player"}): {
        "type": "unlock",
        "sets_flag": "heard_tape_playback",
        "event_message": "You thread the tape in and press play. Under the Niece's voice, the room tone is all wrong for the Cellar — it sounds like the Study.",
    },
    frozenset({"answering_machine_tape", "alibi_note"}): {
        "type": "unlock",
        "requires_flag": "heard_tape_playback",
        "promotes_item_id": "alibi_note",
        "event_message": "You line the tape's playback time up against the alibi note. She logged the call from the Cellar — but the tape's room tone says otherwise. The location is the lie.",
        "not_ready_message": "The note alone doesn't tell you much. Maybe there's a way to check what was actually said — and where.",
    },
    frozenset({"ornate_key", "photo_album_locked"}): {
        "type": "unlock",
        "spawns_item_id": "childhood_photo",
        "event_message": "The key turns with a stiff click. Inside the album, one photo has been flipped face-down, separate from the rest.",
    },
    frozenset({"childhood_photo", "magnifying_glass"}): {
        "type": "unlock",
        "sets_flag": "photo_detail_noted",
        "event_message": "Under the glass, the background resolves: a much younger version of the Niece, playing near the Cellar door, long before this family owned the house.",
    },
    frozenset({"childhood_photo", "blueprint_old"}): {
        "type": "unlock",
        "requires_flag": "photo_detail_noted",
        "promotes_item_id": "childhood_photo",
        "event_message": "You lay the photo against the old blueprint. She wasn't just standing near the Cellar as a child — she was standing right where the hidden passage runs. She'd have known.",
        "not_ready_message": "The photo's a nice find, but you can't place what it's showing yet.",
    },
    frozenset({"window_glass_fragment", "magnifying_glass"}): {
        "type": "unlock",
        "promotes_item_id": "window_glass_fragment",
        "event_message": "Under the glass, the fracture lines are unmistakable: this pane broke outward, from inside the room. Nobody smashed their way in through this window.",
    },
    frozenset({"petty_cash_ledger", "register_receipt"}): {
        "type": "unlock",
        "sets_flag": "butler_cleared",
        "event_message": "The receipt total doesn't match the ledger by a small, familiar amount. The Butler's missing minutes were spent skimming petty cash, not stealing a painting.",
    },
    frozenset({"partial_fingerprint", "ink_pad"}): {
        "type": "unlock",
        "spawns_item_id": "fingerprint_lifted",
        "event_message": "You dust the print and press it against the ink pad. It lifts clean.",
    },
    frozenset({"fingerprint_lifted", "party_guestbook"}): {
        "type": "unlock",
        "sets_flag": "fingerprint_matched_friend",
        "event_message": "You compare the lifted print against the guestbook signatures. It's a match — but not for anyone you'd expect. The Family Friend's.",
    },
    frozenset({"fingerprint_lifted", "old_appraisal_letter"}): {
        "type": "unlock",
        "requires_flag": "fingerprint_matched_friend",
        "sets_flag": "friend_cleared",
        "event_message": "The appraisal letter explains it: he'd made offers on the painting before, all declined. The print's from an earlier conversation admiring the frame, not the theft.",
        "not_ready_message": "You don't have anything to match this print against yet.",
    },
    frozenset({"drink_glass", "kitchen_prep_schedule"}): {
        "type": "unlock",
        "spawns_item_id": "timeline_note_kitchen",
        "event_message": "The glass is still cold, but the Cook's schedule says drinks stopped being poured well before now. Someone's had this a while.",
    },
    frozenset({"timeline_note_kitchen", "alibi_note"}): {
        "type": "unlock",
        "sets_flag": "son_timeline_mismatch",
        "event_message": "You check the timing against the Son's claimed \"just got a drink.\" That's far too long for a drink alone.",
    },
    frozenset({"gambling_iou_note", "timeline_note_kitchen"}): {
        "type": "unlock",
        "requires_flag": "son_timeline_mismatch",
        "sets_flag": "son_cleared",
        "event_message": "The IOU explains the gap: he ducked out to take a call about a debt, not to touch the painting.",
        "not_ready_message": "The IOU is grim reading, but nothing yet ties it to the missing time.",
    },
    frozenset({"dumbwaiter_diagram", "fixture:kitchen:hatch"}): {
        "type": "unlock",
        "sets_flag": "dumbwaiter_cleared",
        "event_message": "You check the hatch against the diagram. It only ever ran Kitchen to Dining, and it's far too small for a framed painting. Whatever happened, it didn't happen this way.",
    },
    frozenset({"ledger_reconciliation_note", "dumbwaiter_diagram"}): {
        "type": "unlock",
        "requires_flag": "dumbwaiter_cleared",
        "sets_flag": "cook_butler_cleared",
        "event_message": "The reconciliation note is in the Cook's hand — she's been quietly helping the Butler square the petty-cash books. The whispering you'd heard about was this, not a conspiracy.",
        "not_ready_message": "The note doesn't mean much without knowing what the Cook and Butler were actually doing near that hatch.",
    },
    frozenset({"party_polaroid_group", "magnifying_glass"}): {
        "type": "unlock",
        "promotes_item_id": "party_polaroid_group",
        "event_message": "Magnified, the blurred figure in the background resolves just enough: someone heading for the Kitchen/Cellar door, right around the time the Niece claims she was on the phone.",
    },
    frozenset({"party_polaroid_dress", "magnifying_glass"}): {
        "type": "unlock",
        "spawns_item_id": "polaroid_dress_detail",
        "event_message": "Under the glass, the dress's fabric and hem come into focus — a distinctive weave, the kind you'd recognize anywhere.",
    },
    frozenset({"snagged_thread", "polaroid_dress_detail"}): {
        "type": "unlock",
        "promotes_item_id": "snagged_thread",
        "event_message": "You hold the thread up against the Polaroid's close-up. Same weave, same fabric. Whoever snagged this on the tunnel wall was wearing her dress.",
    },
}
