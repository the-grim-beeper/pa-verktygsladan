# PA_verktygslådan — Unified Tool Suite Design

## Goal

Combine 5 independent web apps into a single unified suite ("PA_verktygslådan") behind one domain, one password, and one landing page. Each app runs independently as a Railway service; a lightweight portal app provides the shared gateway.

## Architecture

### Overview

A new **portal app** (FastAPI, ~200 lines) acts as the single entry point. It handles authentication, serves a landing page, and reverse-proxies requests to each tool's internal Railway service.

```
Internet → pa-verktygsladan.up.railway.app
                    │
             ┌──────┴──────┐
             │  Portal App  │
             │  (FastAPI)   │
             │              │
             │  - /login    │  Password gate
             │  - /         │  Landing page (tool cards)
             │  - /tools/*  │  Reverse proxy
             └──┬─┬─┬─┬─┬──┘
                │ │ │ │ │
    ┌───────────┘ │ │ │ └───────────┐
    ▼             ▼ ▼ ▼             ▼
  media-        lulea svenska   buss49p   decision-
  trainer       tool  roster    tool      engine
  (internal)   (int) (int)    (int)     (int)
```

### Railway Project Structure

All services live in one Railway project:

| Service | Repo | Internal URL | Public? |
|---------|------|-------------|---------|
| **portal** | pa-verktygsladan | — (public-facing) | Yes |
| **media-trainer** | media-trainer | media-trainer.railway.internal:8000 | No |
| **lulea-tool** | lulea-decision-tool | lulea-tool.railway.internal:8080 | No |
| **svenska-roster** | svenska_roster | svenska-roster.railway.internal:8000 | No |
| **buss49p-tool** | buss49p-decision-tool | buss49p-tool.railway.internal:8081 | No |
| **decision-engine** | decision-engine | decision-engine.railway.internal:8080 | No |

Only the portal gets a public domain. All other services communicate via Railway's private network.

### URL Routing

```
/                          → Portal landing page
/login                     → Password login
/tools/media-trainer/*     → media-trainer service
/tools/lulea/*             → lulea-decision-tool service
/tools/svenska-roster/*    → svenska_roster service
/tools/buss49p/*           → buss49p-decision-tool service
/tools/decision-engine/*   → decision-engine service
```

### Authentication

Single shared password at the portal level:
- `SITE_PASSWORD` environment variable on the portal service
- SHA-256 hashed cookie (`site_auth`), httponly, samesite=lax, 30-day expiry
- Cookie covers all `/tools/*` paths (same domain)
- Individual app password gates disabled/bypassed (internal network only)
- Same pattern as media-trainer's existing auth, proven and simple

### Portal App Components

**1. Password gate middleware** (~30 lines)
- Checks `site_auth` cookie on every request except `/login` and `/api/health`
- Shows Swedish login page if not authenticated
- Same design as media-trainer's existing implementation

**2. Landing page** (~100 lines HTML)
- Dark theme matching existing apps (gray-950 background)
- Title: "PA Verktygslådan"
- 5 cards in a responsive grid, each with:
  - Tool name (Swedish)
  - 1-sentence description
  - Icon/emoji
  - Link to `/tools/{app-name}/`
- Cards:
  - Medieträning → /tools/media-trainer/
  - Luleå-klassen → /tools/lulea/
  - Syntetisk Fokusgrupp → /tools/svenska-roster/
  - Buss 49P → /tools/buss49p/
  - Beslutsmotor → /tools/decision-engine/

**3. Reverse proxy** (~60 lines)
- Uses `httpx.AsyncClient` to forward requests
- Strips `/tools/{app-name}` prefix before forwarding
- Passes through headers, body, SSE streams, WebSocket (if needed)
- Handles streaming responses (critical for media-trainer's SSE and svenska_roster's LLM streaming)

### Changes to Existing Apps

Minimal changes required:

**React apps (media-trainer, svenska_roster, decision-engine):**
- Set `base: '/tools/{app-name}/'` in `vite.config.ts`
- Ensure API calls use relative paths (most already do)
- Remove individual password middleware (portal handles auth)

**Express apps (lulea-decision-tool, buss49p-decision-tool):**
- Add `app.use('/tools/{app-name}', ...)` base path OR rely on proxy stripping the prefix
- Ensure static file paths are relative
- Remove individual password middleware

**Approach: Proxy strips the prefix** — the portal removes `/tools/{app-name}` before forwarding, so each app sees requests at `/` as before. This means **zero changes** to routing in existing apps. Only the Vite `base` config needs updating for React apps (so asset URLs are correct).

### Tech Stack for Portal

- **Backend:** Python 3.12 + FastAPI + httpx (async HTTP client for proxying)
- **Frontend:** Static HTML/CSS (no build step needed — it's just a landing page)
- **Docker:** Single-stage Python image
- **Dependencies:** fastapi, uvicorn, httpx

### Environment Variables (Portal)

```
SITE_PASSWORD=<shared-password>
MEDIA_TRAINER_URL=http://media-trainer.railway.internal:8000
LULEA_TOOL_URL=http://lulea-tool.railway.internal:8080
SVENSKA_ROSTER_URL=http://svenska-roster.railway.internal:8000
BUSS49P_TOOL_URL=http://buss49p-tool.railway.internal:8081
DECISION_ENGINE_URL=http://decision-engine.railway.internal:8080
```

### Deployment Steps

1. Create Railway project "pa-verktygsladan"
2. Add each existing repo as a service (5 services)
3. Create portal service from new pa-verktygsladan repo
4. Configure environment variables on each service
5. Set portal as the only public-facing service
6. Assign custom domain to portal

## What This Does NOT Include

- No database migration or unification
- No frontend framework migration
- No shared component library
- No user accounts or per-user data
- No modifications to app business logic
