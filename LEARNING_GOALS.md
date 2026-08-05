# Learning Goals: Text Adventure Mystery Project

A working checklist of concepts to actually understand — not just get working — while building the login-gated text adventure.

---

## 1. Cookies
**Why it shows up here:** keeping a player logged in / tracking their session between requests.

- [ ] What a cookie actually is (a header, not magic) — `Set-Cookie` on response, `Cookie` on request
- [ ] Session cookies vs persistent cookies (expiry)
- [ ] `HttpOnly`, `Secure`, `SameSite` flags — what each one protects against
- [ ] Cookie-based sessions vs token-based (JWT) — tradeoffs, not just "which is better"
- [ ] How to inspect cookies in the browser (DevTools → Application tab) while your app runs

**Good milestone:** explain to yourself why a stolen cookie without `HttpOnly` is a bigger deal than one with it.

---

## 2. Databases
**Why it shows up here:** users, save states, story/evidence progress.

- [ ] Tables, rows, primary/foreign keys — how `users` and `player_saves` relate
- [ ] Basic SQL: SELECT, INSERT, UPDATE, JOIN
- [ ] What an ORM (e.g. SQLAlchemy, Prisma) is doing for you under the hood — and what it hides
- [ ] Migrations — why you don't just hand-edit the schema in prod
- [ ] SQLite (dev) vs Postgres (prod) — why you might start on one and move to the other

**Good milestone:** write one query by hand before letting an ORM generate it, so you know what it's doing for you.

---

## 3. Auth
**Why it shows up here:** player accounts, login/logout, protecting save data per-user.

- [ ] Password hashing — why plaintext storage is a non-starter, what bcrypt actually does (salt + slow hash)
- [ ] Login flow end-to-end: submit credentials → verify hash → create session/token → set cookie
- [ ] Authentication vs authorization (who you are vs what you're allowed to do)
- [ ] Session-based auth vs JWT — and why "don't roll your own crypto" doesn't mean "don't understand it"
- [ ] Logout — what actually needs to happen server-side, not just deleting a cookie client-side

**Good milestone:** trace a single login request through your own code, cookie to database and back, without skipping a step.

---

## 4. Hosting a webpage
**Why it shows up here:** getting this thing live somewhere other than localhost.

- [ ] Static hosting vs a server that runs your backend code (this project needs the latter)
- [ ] Domains, DNS basics (A records, CNAME) — enough to point a domain at your host
- [ ] HTTPS/TLS — what a cert does, why platforms like Railway/Render give you one for free
- [ ] Environment variables / secrets in production (not committed to git)
- [ ] Basic deploy flow: push to git → build → deploy, and what "build" actually does

**Good milestone:** deploy a trivial "hello world" version before deploying the real app, so deploy problems and app problems don't get tangled together.

---

## 5. Self-hosted backend
**Why it shows up here:** you're running your own Express/FastAPI server, not using a BaaS like Firebase.

- [ ] Request/response cycle — what happens between a client hitting an endpoint and getting JSON back
- [ ] Routing — how your framework maps URL + method to a handler function
- [ ] Middleware — what it is, why auth checks and logging usually live there
- [ ] Process management — what keeps your server running (and restarts it) after a crash, in production
- [ ] Logs — where they go once you're not staring at a terminal on your own machine

**Good milestone:** intentionally crash your server, then figure out (without help) why it went down using only the logs.

---

## Parked (not this project)
**Networking fundamentals** — you flagged this as minor interest, and it's real but mostly orthogonal to this build (you'll touch HTTP requests/responses, but not routing, DNS internals, TCP/IP, etc. in depth). Worth its own smaller project later — something like a CLI tool that does raw socket requests, or just working through a networking course — rather than bolting it onto a text adventure game.

---

## Suggested order
Auth and DBs will come first naturally (you can't have saves without users). Cookies fall out of building auth. Hosting comes last, once there's something worth deploying. Self-hosted backend concepts are threaded through the whole thing rather than a discrete phase — you'll pick them up by hitting them.
