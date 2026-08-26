# Missing from the Study — Design Decisions

Reference doc for fleshing out items, combos, and evidence. Locked decisions live under "Decided." Open questions live under "Needs a Decision" — resolve those to unblock remaining content.

## Tone & Setting

- **Voice:** Second-person, immersive ("you notice/you feel"), sensory prose that doubles as interaction hints.
- **Style:** Modern-day cozy mystery — genteel country-house bones, contemporary tech/texture. Cumberbatch-*Sherlock* energy: quick, observational, deduction-flavored, warm rather than grim.
- **Setting:** One house — Study, Kitchen, Library, Garden, plus the connecting Hallway and Stairs (both hold their own finds now, not just pass-through) — and a **Cellar** that opens into a hidden **Tunnel** once unlocked mid-game.
- **Puzzle philosophy:** Monkey Island–style. Items are keys, not clue-lookups — they're only meaningful once combined, then aimed at the environment. Avoid "examine object, notice dust" beats; prefer assemble → use-on-room → reveal.

## The Case (Answer Key)

- **Crime:** A valuable painting is stolen from the Study during a dinner party.
- **The twist:** It's a locked-room puzzle, not a whodunit-by-vibes. A forgotten servant's tunnel connects the Cellar to the Garden shed, missing from the current floor plan since a decades-old renovation. The Study was watched/in guests' sightline all night — the real question is *how* anyone got in and out unseen.
- **Culprit: the Niece.** Visited the house as a child before it changed hands and discovered the tunnel then. Motive: inheritance dispute (unchanged from earlier draft).
- **How she did it:** Excused herself to take a phone call "in the cellar for privacy." Actually used the tunnel to reach a disused passage behind the Study wall, took the painting, and returned in time to resume the call. Her phone-record alibi is real — the *location* is the lie.
- **Butler:** now a pure red herring. His unaccounted 10 minutes is unrelated (skimming petty cash), not theft.
- **Gardener/window:** stays as the second red herring — clears the "outside break-in" theory and redirects players toward an inside/hidden-access job.

### Suspects

| Suspect | Motive | Alibi | Inconsistency |
|---|---|---|---|
| Niece (guilty) | Inheritance dispute | "Was on the phone in the cellar" — phone records confirm a call happened | Audio evidence proves she wasn't actually in the cellar when it happened |
| Butler | Debt to pay off | "Was serving drinks all night" | Unaccounted ~10 minutes — but it's petty cash, not the painting |
| Gardener | None real | Outside near a "broken" window | Window glass fell outward, not inward — already broken from inside |

## Puzzle Chains

Each chain ends by promoting an item to `type: "evidence"` with an explicit "aha" event message. Required chains (A, B, C) form the core logical proof; D and E are supporting/red-herring resolution.

### Chain A — Opening the Tunnel (proves *opportunity*)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `blueprint_old` (Garden shed) | context only | Establishes the house has more floor plan than currently visible. No consume/unlock — just narrative context that motivates step 3. |
| 2 | Find `crank_handle_broken` (Garden shed) | context only | Obviously incomplete — missing its shaft. |
| 3 | Combine `broom_handle` (Kitchen) + `crank_handle_broken` | **consume** | → `crank_jury_rigged` |
| 4 | Use `crank_jury_rigged` on the Cellar's bricked-up wine rack | **room interaction** | Wine rack grinds open, revealing the tunnel mouth |
| 5 | Combine `candle_stub` (Study) + `matchbook` (Hallway) | **consume** | → `lit_candle` |
| 6 | Use `lit_candle` in the Tunnel | **unlock** | Reveals the passage exits near the Study wall; surfaces `snagged_thread` |
| 7 | Combine `party_polaroid_dress` (party-favor Polaroid showing her dress in full, found in the Study/Dining area — she'd been showing it off all night) + `magnifying_glass` | **unlock** | Zooms in on the fabric pattern/hem detail → sets `polaroid_dress_detail` |
| 8 | Combine `snagged_thread` + `polaroid_dress_detail` | **unlock → promote** | → `thread_match_evidence` (Evidence: physical presence in the tunnel) |

### Chain B — Breaking the Alibi (proves *the location lie*)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `answering_machine_tape` (Hallway, by the house phone) | context only | An old house intercom/answering system caught background audio during a call. |
| 2 | Find `tape_player` (Library) | context only | Old but functional. |
| 3 | Combine `answering_machine_tape` + `tape_player` | **unlock** | Plays back the recording — sets flag `heard_tape_playback`; room tone sounds like the Study, not the Cellar |
| 4 | Combine `heard_tape_playback` flag + `alibi_note` (guest list/timeline, already documents her claimed call time/location) | **unlock → promote** | → `location_contradiction_evidence` (Evidence: she wasn't where she said) |

### Chain C — Establishing Means (proves *she knew about the tunnel*)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `photo_album_locked` (Library) | context only | Small clasp lock, stuck shut. |
| 2 | Find `ornate_key` (Garden, buried under a flowerpot) | context only | |
| 3 | Combine `ornate_key` + `photo_album_locked` | **unlock** | Album opens — reveals `childhood_photo` |
| 4 | Combine `childhood_photo` + `magnifying_glass` (existing tool) | **unlock** | Confirms date/location detail — sets flag `photo_detail_noted` (young Niece playing near the cellar/shed, years before the current owners) |
| 5 | Combine `childhood_photo` + `blueprint_old` (from Chain A, step 1) | **unlock → promote** | → `means_evidence` (Evidence: she'd have known the passage existed) |

### Chain D — Clearing the Break-In Theory (red herring resolution)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Combine `window_glass_fragment` (Study) + `magnifying_glass` | **unlock → promote** | → `outward_break_evidence` — glass fell *outward*, not inward. Clears the Gardener/outside-break-in theory. Supporting, not required. |

### Chain E — Resolving the Butler (red herring resolution)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Combine `petty_cash_ledger` (Kitchen) + `register_receipt` (Kitchen) | **unlock** | → `butler_explanation` — accounts for his 10 unattended minutes as unrelated pettiness, not theft. Resolves suspicion; not evidence toward the accusation. |

**Required evidence for the true ending:** `thread_match_evidence`, `location_contradiction_evidence`, `means_evidence` (Chains A–C — the core logical proof). `outward_break_evidence` and `butler_explanation` are supporting/optional, but a satisfying playthrough probably wants both resolved before the final accusation.

## Expanded Cast (Red Herrings)

A crowded dinner party in a storm — nobody's outside, no one can claim fresh-air alibis, and the whole house becomes the locked room. This also gives the Niece a plausible, unsuspicious reason to duck into the Cellar (the only quiet, private spot left in a full house).

| Suspect | Motive | Alibi | Inconsistency |
|---|---|---|---|
| Family Friend (rich) | Coveted the painting — made offers to buy it in the past, all declined | Was admiring/discussing it with the host earlier (innocent) | His prints are on the frame — but from that earlier conversation, not the theft |
| Son | Gambling debt, wants the painting sold/liquidated | "Just got a drink" in the Kitchen | Gone far longer than a drink takes |
| Houseguest (another guest's plus-one) | None — barely knows the family | "Got lost looking for the bathroom" | Seen near the Study — looks suspicious, but she's just an outsider in an unfamiliar house |
| Cook (new — balances the Butler) | None | In the Kitchen the whole time (true) | Knows only kitchen/dining/dumbwaiter territory, unlike the Butler's full-house access; seen quietly talking with the Butler, which *reads* like collusion but isn't |

### Chain F — Family Friend's Fingerprints (red herring resolution)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `partial_fingerprint` on the frame (Study) | context only | |
| 2 | Combine `partial_fingerprint` + `ink_pad` (Study desk) | **unlock** | → `fingerprint_lifted` |
| 3 | Combine `fingerprint_lifted` + `party_guestbook` (signed on arrival, Hallway entryway) | **unlock** | Matches the Family Friend, not the culprit |
| 4 | Combine `fingerprint_lifted` match + `old_appraisal_letter` (found in his coat/bag, or Library desk — references his past offers to buy the painting) | **unlock → promote** | → `friend_explanation` (resolves, non-evidence) |

### Chain G — The Son's Missing Time (red herring resolution)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `drink_glass`, half-full and still cold (Kitchen) | context only | |
| 2 | Combine `drink_glass` + `kitchen_prep_schedule` (Cook's written party timing notes, Kitchen) | **unlock** | → `timeline_note_kitchen` |
| 3 | Combine `timeline_note_kitchen` + `alibi_note` (his claimed "just got a drink") | **unlock** | Reveals he was gone too long for a drink alone |
| 4 | Find `gambling_iou_note` (tucked behind crates, Cellar) and combine with the timing mismatch | **unlock → promote** | → `son_explanation` — he ducked out to take a private call about a debt, unrelated to the painting |

### Chain H — The Dumbwaiter Red Herring (mechanism-level herring)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `dumbwaiter_hatch` (Kitchen) — looks like a way to move something between floors unseen | context only | |
| 2 | Combine `dumbwaiter_hatch` + `dumbwaiter_diagram` (pinned to a corkboard, Library) | **unlock** | Reveals it only runs Kitchen↔Dining and is too small for a framed painting — clears the "moved via dumbwaiter" theory |
| 3 | Combine `ledger_reconciliation_note` (wedged into the wine rack, Cellar) + `dumbwaiter_diagram` | **unlock → promote** | → `cook_butler_explanation` — what looked like whispered collusion was the Cook quietly helping the Butler square the petty-cash books. Friendly, not conspiratorial. |

### Chain I — The Houseguest's Accidental Witness (second discovery path for opportunity)

| Step | Action | Type | Result |
|---|---|---|---|
| 1 | Find `party_polaroid_group` (tucked into a framed photo, Stairs) | context only | |
| 2 | Combine `party_polaroid_group` + `magnifying_glass` | **unlock → promote** | Zooms into the background — a blurred figure heading toward the Kitchen/Cellar door at the right time. Functions as a **second discovery path** for the Niece's opportunity (Chain A), for players who miss the tunnel thread or the tape. |

## Mechanics (Decided)

- **Combine logic:** mostly *combine-and-consume* (crafting-style — originals gone, new item produced). A subset are *combine-and-unlock* (originals persist; sets a flag/event) — used for anything evidence-shaped, since real clues shouldn't vanish once used.
- **Evidence promotion:** items start as plain `type: "item"`. A combo/flag trigger reclassifies them to `type: "evidence"`, swaps in an `evidence_description`, and fires an explicit "aha" event message (not a silent mutation) — this feeds the evidence log/notebook.
- **Item-first design:** the puzzle is driven by finding, examining, and combining items — not by interrogating suspects correctly. Every required and supporting clue above has a concrete item-combo path.
- **Dialogue's role:** context and hints only, never a required solve step. NPCs can flavor the scene (a guest mentions something in passing) or nudge a stuck player toward an item they've overlooked, but no chain requires picking the "right" dialogue option to progress.
- **Solving mechanic:** end-game accusation — player names a suspect and presents evidence. Missing required evidence → weaker/wrong ending.
- **Discovery redundancy:** each key fact should have at least 2 discovery paths. Chain I now covers Chain A/B as a backup route; Chains C and F–H are still single-path (see below).
- **Red herrings:** Butler, Gardener/window, Family Friend, Son, Houseguest, and the Cook/Butler "collusion" — six in total, each resolvable via its own short item chain (D–H) rather than left as noise.
- **World logic — the storm:** heavy rain keeps everyone inside all night. This removes "step outside" as an option for any alibi, makes the house itself the locked room, and explains why the Niece took her call in the Cellar instead of outdoors. It also masks the tunnel-crank noise and explains poor sightlines near the Garden shed.

## Needs a Decision

- [ ] **Backup discovery paths for Chains C, F, G, H.** Only Chain A/B has a confirmed second route (Chain I). What's the fallback for `ornate_key`, the fingerprint match, the Son's IOU note, and the dumbwaiter diagram?
- [ ] **Room mapping for the Cellar/Tunnel.** Confirm which existing room the Cellar is accessed from (Kitchen seems natural) and whether the Tunnel counts as its own explorable space or a single interaction beat.
- [ ] **Tool items.** `magnifying_glass` is now used four times (Chains C, D, F, I) — confirm it's a single reusable tool found early, not separate finds.
- [ ] **Polaroid item family.** `party_polaroid_dress` and `party_polaroid_group` both come from a shared "party Polaroids" pool — decide if this is one stack the player sorts through (finding relevant ones as they go) or separate fixed pickups.
- [ ] **Ending variants.** What does the game show for: all 3 required evidence + correct accusation vs. partial evidence vs. wrong accusation?
