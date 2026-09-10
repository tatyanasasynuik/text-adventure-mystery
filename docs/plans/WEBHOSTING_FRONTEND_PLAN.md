# Plan: Web Hosting & Frontend

Framing doc for two of the open items in [`DESIGN_NOTES.md`](initial/DESIGN_NOTES.md) — how the frontend is built and how the whole thing gets hosted. Ties directly into [`LEARNING_GOALS.md`](initial/LEARNING_GOALS.md) sections 4 (Hosting) and 5 (Self-hosted backend). Nothing here is locked — same spirit as the "Open decisions" section in the design notes.

---

## Frontend

### Recommendation: plain HTML/CSS/JS to start

Design notes list this as a genuine open choice (plain JS vs React). Recommending plain JS first, for a reason that's actually about the *hosting* learning goal, not the frontend one:

> "Deploy a trivial hello world version before deploying the real app, so deploy problems and app problems don't get tangled together." — `LEARNING_GOALS.md`

Same logic applies one level up: if the frontend is plain static files, a deploy failure is obviously a hosting/config problem, not a build-tooling problem. React adds a build step (bundler, JSX transform, `npm run build` output directory) that's one more thing to debug simultaneously with sessions/cookies/DB during the parts of this project that are actually about auth. React stays a legitimate stretch goal *after* the game is live and working — swapping the frontend later is a contained, well-scoped exercise, and "extra frontend reps" doesn't disappear by deferring it.

### Shape

- Single-page app feel without a framework: one `index.html`, a `game.js` that owns state + rendering, `style.css`.
- UI is a scrolling log (append-only div) + a text input / button-based choice list, per the design notes.
- Talks to the backend purely over `fetch()` calls to JSON endpoints (`/api/login`, `/api/game/state`, `/api/game/action`, etc.) — keep the frontend dumb, all game logic server-side. This matters for the puzzle design (evidence/flags) since the client shouldn't be trusted with solution state.
- Session auth via cookie means `fetch()` calls need `credentials: "include"` if frontend and backend ever end up on different origins (see below).

### Where it lives, relative to the backend

Two options, worth deciding *with* the hosting choice rather than before it:

1. **Same origin, server-rendered static files** — Express/FastAPI serves the `frontend/` folder as static assets alongside the API. One deploy, one URL, no CORS to think about. Simplest for a first deploy.
2. **Separate static host** (e.g. Netlify/Vercel/GitHub Pages for frontend, API on Railway/Render/Fly) — closer to a "real" production split, but introduces CORS + cross-origin cookies (`SameSite=None; Secure`) as extra surface area.

**Recommendation: option 1 for the first deploy.** It directly serves the cookie learning goals (`SameSite` matters less when there's no cross-origin question yet) and matches "hello world before real app." Revisit option 2 later if you want the CORS/cross-origin practice on purpose.

---

## Hosting

### Platform: Fly.io (revised — see below)

Originally recommended Render for the lowest-friction git-push deploy. Revised to **Fly.io**, since existing devops experience removes the main reason Render was favored (avoiding a steeper learning curve) — Fly's CLI-driven, `fly.toml`-based flow is a better match for that background and leaves more room to use the infra experience already there instead of hiding it behind a dashboard.

| | Fly.io | Render | Railway |
|---|---|---|---|
| Free/cheap web tier | Small free allowance, pay-as-you-go past that | Yes (sleeps when idle) | Trial credit, then paid |
| Postgres | Two paths — see below | Managed, free tier (90-day expiry on free instances) | Managed |
| Deploy flow | `fly deploy`, config in `fly.toml`, CLI-driven | Git push → auto build/deploy via dashboard | Similar to Render |
| TLS / custom domain | Automatic, CLI-driven (`fly certs`) | Automatic on `.onrender.com` | Automatic |
| Fit here | More moving parts, but that's the point — matches existing devops background and leaves room for the self-run-DB stretch goal | Lowest-friction, better if the DB/deploy internals should stay out of the way | Similar tradeoffs to Render |

### Postgres on Fly: two paths, start with the managed one

Fly actually offers two distinct Postgres options, which map directly onto "add self-managed DB later" as a real phase-2 feature rather than a vague someday:

1. **Fly Managed Postgres (MPG)** — Fly's current fully-managed offering: backups, replication, version upgrades, and scaling handled by Fly. This is the v1 choice — get auth + save/load working against a DB that "just works" before adding DB operations as a second layer of complexity.
2. **Self-run Postgres on Fly** — Postgres deployed as a plain Fly app on a Machine with a persistent Volume, operated the same way any self-hosted Postgres would be (your own backups, restarts, disk/memory headroom, upgrades). Fly's older `flyctl postgres create` unmanaged-cluster tooling is deprecated, so build this path as an ordinary Fly app rather than through that command.

Because both are still just Postgres reachable via a `DATABASE_URL`, moving from (1) to (2) later is a connection-string swap plus taking on the ops work — no application code changes, no schema changes, no risk to the save/load design in `SAVE_LOAD_PLAN.md`. That makes it a clean phase-2 milestone: ship the game on MPG first, then stand up self-run Postgres as a dedicated exercise once the app itself is stable, with MPG as the fallback to revert to if the self-run instance falls over.

### Deploy shape (Fly.io + same-origin frontend from above)

- One Fly **app**, defined by `fly.toml`, running the Node/Express (or FastAPI) container and serving the static frontend files from the same origin.
- **Postgres:** start on Fly Managed Postgres, connected via a `DATABASE_URL` set through `fly secrets set` (never committed — same principle as Render's dashboard env vars, just CLI-driven here).
- **Environment variables/secrets:** `DATABASE_URL`, session secret, `NODE_ENV=production` / `ENV=production`, all via `fly secrets set`, not `fly.toml` (that file is committed to git).
- **Build:** Fly builds from a `Dockerfile` (or its buildpack-style auto-detection) rather than a bare build command — worth writing an explicit `Dockerfile` early given the devops background, instead of leaning on auto-detection.

### Suggested milestones (maps to `LEARNING_GOALS.md` §4)

1. **Hello-world deploy first.** `fly launch` a bare Express/FastAPI app returning "hello" on `/`, confirm it's live with HTTPS on the `*.fly.dev` URL. Don't touch the real app until this works.
2. **Add the DB.** Provision Fly Managed Postgres, connect via `DATABASE_URL`, confirm the app can read/write a trivial table in production before wiring real auth to it.
3. **Deploy the real app.** Push the actual game once auth + DB work locally, using the same secrets pattern proven in steps 1–2.
4. **Custom domain (optional/stretch).** `fly certs` + a CNAME once everything else is stable — the DNS learning-goal item, fully decoupled from app correctness.
5. **Logs.** Deliberately break something in production (e.g. bad secret) and diagnose it via `fly logs` without redeploying blind — the "crash your server, find out why from logs only" milestone.
6. **Self-run Postgres (stretch, phase 2).** Once the app is stable on Managed Postgres, stand up Postgres as its own Fly app + Volume, migrate `DATABASE_URL` over, and practice backups/restores and a restart by hand. Treat MPG as the rollback path if this goes sideways mid-exercise.

---

## Open decisions this doc surfaces (add to `DESIGN_NOTES.md` once resolved)

- [x] Confirm Fly.io vs Render vs Railway — **Fly.io**, per devops background
- [ ] Confirm plain JS vs React for frontend (recommendation above: plain JS first)
- [ ] Confirm same-origin static serving vs split frontend/backend hosting (recommendation above: same-origin first)
- [ ] Custom domain — wanted at all, or is `*.fly.dev` fine for a learning project?
- [ ] Timing for the self-run-Postgres stretch goal — right after v1 ships, or later once more of the game content is built out?
