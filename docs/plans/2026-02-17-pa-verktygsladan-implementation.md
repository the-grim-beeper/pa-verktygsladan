# PA_verktygslådan Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a portal app that unifies 5 existing tools behind one domain, one password, and one landing page on Railway.

**Architecture:** A FastAPI portal app handles auth and serves a landing page, then reverse-proxies requests to 5 independent backend services on Railway's internal network. Each existing app runs in its own container unchanged (or with minimal config tweaks).

**Tech Stack:** Python 3.12, FastAPI, httpx (async proxy), Docker, Railway

---

### Task 1: Create the portal FastAPI app with auth and landing page

**Files:**
- Create: `pa-verktygsladan/app/__init__.py`
- Create: `pa-verktygsladan/app/main.py`
- Create: `pa-verktygsladan/app/config.py`
- Create: `pa-verktygsladan/app/proxy.py`
- Create: `pa-verktygsladan/app/landing.py`
- Create: `pa-verktygsladan/requirements.txt`

**Step 1: Create `requirements.txt`**

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
httpx>=0.27.0
```

**Step 2: Create `app/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    site_password: str = ""
    media_trainer_url: str = "http://media-trainer.railway.internal:8000"
    lulea_tool_url: str = "http://lulea-tool.railway.internal:8080"
    svenska_roster_url: str = "http://svenska-roster.railway.internal:8000"
    buss49p_tool_url: str = "http://buss49p-tool.railway.internal:8081"
    decision_engine_url: str = "http://decision-engine.railway.internal:8080"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Map tool slugs to their internal URLs
TOOL_ROUTES = {
    "media-trainer": settings.media_trainer_url,
    "lulea": settings.lulea_tool_url,
    "svenska-roster": settings.svenska_roster_url,
    "buss49p": settings.buss49p_tool_url,
    "decision-engine": settings.decision_engine_url,
}
```

**Step 3: Create `app/landing.py`**

This module returns the HTML for the landing page. Dark theme, Swedish text, 5 tool cards in a responsive grid.

```python
TOOLS = [
    {
        "slug": "media-trainer",
        "name": "Medieträning",
        "desc": "AI-analys av video — få tidsstämplad feedback på kroppsspråk, röst och budskap.",
        "icon": "🎬",
    },
    {
        "slug": "lulea",
        "name": "Luleå-analys",
        "desc": "Strategisk beslutsanalys för Luleå-klassens ytstridsfartyg.",
        "icon": "🚢",
    },
    {
        "slug": "svenska-roster",
        "name": "Syntetisk Fokusgrupp",
        "desc": "Multi-agent fokusgrupp med genuint diversa AI-deltagare.",
        "icon": "🗣️",
    },
    {
        "slug": "buss49p",
        "name": "Buss 49P",
        "desc": "Beslutsstöd för FMV:s Buss 49P upphandling.",
        "icon": "🚌",
    },
    {
        "slug": "decision-engine",
        "name": "Beslutsmotor",
        "desc": "Generell AI-stödd beslutsmodellering med dokumentanalys.",
        "icon": "⚖️",
    },
]


def landing_page_html() -> str:
    cards = ""
    for t in TOOLS:
        cards += f"""
        <a href="/tools/{t['slug']}/" class="card">
          <span class="icon">{t['icon']}</span>
          <h2>{t['name']}</h2>
          <p>{t['desc']}</p>
        </a>"""

    return f"""\
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PA Verktygslådan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{min-height:100vh;background:#030712;color:#f3f4f6;font-family:'Inter',system-ui,sans-serif}}
header{{border-bottom:1px solid #1f2937;padding:1.5rem 2rem}}
header h1{{font-size:1.5rem;font-weight:700;letter-spacing:-0.02em}}
header span{{color:#6b7280;font-weight:400;font-size:0.9rem;margin-left:0.75rem}}
main{{max-width:72rem;margin:0 auto;padding:3rem 1.5rem}}
.subtitle{{text-align:center;color:#9ca3af;margin-bottom:2.5rem;font-size:1.05rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.25rem}}
.card{{display:block;background:#111827;border:1px solid #1f2937;border-radius:1rem;padding:1.75rem;
       text-decoration:none;color:inherit;transition:border-color .2s,transform .15s}}
.card:hover{{border-color:#3b82f6;transform:translateY(-2px)}}
.icon{{font-size:2rem;display:block;margin-bottom:0.75rem}}
.card h2{{font-size:1.1rem;font-weight:600;margin-bottom:0.5rem}}
.card p{{color:#9ca3af;font-size:0.875rem;line-height:1.5}}
</style>
</head>
<body>
<header><h1>PA Verktygslådan<span>Analysverktyg</span></h1></header>
<main>
  <p class="subtitle">Välj ett verktyg nedan för att komma igång.</p>
  <div class="grid">{cards}</div>
</main>
</body>
</html>"""


LOGIN_PAGE = """\
<!DOCTYPE html>
<html lang="sv">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logga in — PA Verktygslådan</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:#030712;color:#f3f4f6;font-family:'Inter',system-ui,sans-serif}
  .card{background:#111827;border:1px solid #374151;border-radius:1rem;padding:2.5rem;width:100%;max-width:360px}
  h1{font-size:1.25rem;margin:0 0 1.5rem}
  input{width:100%;padding:.75rem;border-radius:.5rem;border:1px solid #4b5563;
        background:#1f2937;color:#f3f4f6;font-size:1rem;box-sizing:border-box}
  input:focus{outline:none;border-color:#3b82f6}
  button{width:100%;margin-top:1rem;padding:.75rem;border-radius:.5rem;border:none;
         background:#3b82f6;color:#fff;font-size:1rem;cursor:pointer;font-weight:500}
  button:hover{background:#2563eb}
  .err{color:#f87171;font-size:.875rem;margin-top:.75rem;display:none}
</style></head>
<body><div class="card"><h1>PA Verktygslådan</h1>
<form method="POST" action="/login">
  <input type="password" name="password" placeholder="Lösenord" autofocus>
  <button type="submit">Logga in</button>
  %%ERROR%%
</form></div></body></html>"""
```

**Step 4: Create `app/proxy.py`**

The reverse proxy module. Uses httpx to forward requests, strips the `/tools/{slug}` prefix. Handles streaming responses (critical for SSE in media-trainer and svenska_roster).

```python
import logging

import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse, Response

from .config import TOOL_ROUTES

logger = logging.getLogger(__name__)

# Persistent async client (connection pooling)
_client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0), follow_redirects=True)


async def proxy_request(tool_slug: str, path: str, request: Request) -> Response:
    """Forward a request to the target tool service."""
    base_url = TOOL_ROUTES.get(tool_slug)
    if not base_url:
        return Response(content="Tool not found", status_code=404)

    target_url = f"{base_url}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Read request body
    body = await request.body()

    # Forward headers (skip host and connection)
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ("host", "connection", "transfer-encoding"):
            headers[key] = value

    method = request.method

    # Build the proxied request
    req = _client.build_request(
        method=method,
        url=target_url,
        headers=headers,
        content=body if body else None,
    )

    # Stream the response back
    upstream = await _client.send(req, stream=True)

    # Check if this is a streaming response (SSE, chunked)
    content_type = upstream.headers.get("content-type", "")
    is_streaming = (
        "text/event-stream" in content_type
        or "chunked" in upstream.headers.get("transfer-encoding", "")
    )

    if is_streaming:
        async def stream_body():
            async for chunk in upstream.aiter_bytes():
                yield chunk
            await upstream.aclose()

        # Forward relevant response headers
        resp_headers = {}
        for key in ("content-type", "cache-control", "x-accel-buffering"):
            if key in upstream.headers:
                resp_headers[key] = upstream.headers[key]

        return StreamingResponse(
            stream_body(),
            status_code=upstream.status_code,
            headers=resp_headers,
        )
    else:
        content = await upstream.aread()
        await upstream.aclose()

        resp_headers = {}
        for key, value in upstream.headers.items():
            if key.lower() not in ("transfer-encoding", "connection", "content-encoding", "content-length"):
                resp_headers[key] = value

        return Response(
            content=content,
            status_code=upstream.status_code,
            headers=resp_headers,
        )
```

**Step 5: Create `app/main.py`**

```python
import hashlib
import hmac

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response

from .config import settings, TOOL_ROUTES
from .landing import landing_page_html, LOGIN_PAGE
from .proxy import proxy_request

app = FastAPI(title="PA Verktygslådan")

_COOKIE_NAME = "pa_auth"
_TOKEN = hashlib.sha256(settings.site_password.encode()).hexdigest() if settings.site_password else ""


def _is_authenticated(request: Request) -> bool:
    if not settings.site_password:
        return True
    cookie = request.cookies.get(_COOKIE_NAME, "")
    return hmac.compare_digest(cookie, _TOKEN)


# --- Auth routes ---

@app.get("/login")
async def login_page():
    return HTMLResponse(LOGIN_PAGE.replace("%%ERROR%%", ""))


@app.post("/login")
async def login(request: Request):
    form = await request.form()
    password = form.get("password", "")
    if password == settings.site_password:
        response = HTMLResponse(
            '<html><head><meta http-equiv="refresh" content="0;url=/"></head></html>'
        )
        response.set_cookie(
            _COOKIE_NAME, _TOKEN,
            httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30,
        )
        return response
    return HTMLResponse(
        LOGIN_PAGE.replace("%%ERROR%%", '<p class="err" style="display:block">Fel lösenord</p>'),
        status_code=401,
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# --- Landing page ---

@app.get("/")
async def landing(request: Request):
    if not _is_authenticated(request):
        return HTMLResponse(LOGIN_PAGE.replace("%%ERROR%%", ""))
    return HTMLResponse(landing_page_html())


# --- Reverse proxy catch-all ---

@app.api_route("/tools/{tool_slug}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(tool_slug: str, path: str, request: Request):
    if not _is_authenticated(request):
        return HTMLResponse(LOGIN_PAGE.replace("%%ERROR%%", ""), status_code=401)
    if tool_slug not in TOOL_ROUTES:
        return Response(content="Verktyget hittades inte", status_code=404)
    return await proxy_request(tool_slug, path, request)


# Handle /tools/{slug}/ (trailing slash, no path)
@app.api_route("/tools/{tool_slug}", methods=["GET"])
async def proxy_root(tool_slug: str, request: Request):
    if not _is_authenticated(request):
        return HTMLResponse(LOGIN_PAGE.replace("%%ERROR%%", ""), status_code=401)
    if tool_slug not in TOOL_ROUTES:
        return Response(content="Verktyget hittades inte", status_code=404)
    return await proxy_request(tool_slug, "", request)
```

**Step 6: Create `app/__init__.py`**

Empty file.

**Step 7: Verify syntax**

Run: `cd /Users/nicklaslundblad/pa-verktygsladan && python -m py_compile app/main.py && python -m py_compile app/config.py && python -m py_compile app/proxy.py && python -m py_compile app/landing.py`

**Step 8: Commit**

```bash
git add -A
git commit -m "feat: portal app with auth, landing page, and reverse proxy"
```

---

### Task 2: Add Dockerfile and railway.toml for the portal

**Files:**
- Create: `pa-verktygsladan/Dockerfile`
- Create: `pa-verktygsladan/railway.toml`

**Step 1: Create `Dockerfile`**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/

ENV PORT=8000
EXPOSE ${PORT}
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
```

**Step 2: Create `railway.toml`**

```toml
[build]
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/api/health"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**Step 3: Commit**

```bash
git add Dockerfile railway.toml
git commit -m "feat: add Dockerfile and Railway config for portal"
```

---

### Task 3: Add Dockerfiles for Express apps (lulea, buss49p)

These two repos have no Dockerfile. They need simple Node.js Docker images.

**Files:**
- Create: `/Users/nicklaslundblad/lulea-decision-tool/Dockerfile`
- Create: `/Users/nicklaslundblad/lulea-decision-tool/railway.toml`
- Create: `/Users/nicklaslundblad/buss49p-decision-tool/Dockerfile`
- Create: `/Users/nicklaslundblad/buss49p-decision-tool/railway.toml`

**Step 1: Create Dockerfile for lulea-decision-tool**

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

ENV PORT=8080
EXPOSE ${PORT}
CMD ["node", "server.js"]
```

**Step 2: Create railway.toml for lulea-decision-tool**

```toml
[build]
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/api/health"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

Note: If lulea-decision-tool doesn't have a `/api/health` endpoint, add one:
In `server.js`, add before the listen call: `app.get('/api/health', (req, res) => res.json({ status: 'ok' }));`

**Step 3: Create identical Dockerfile for buss49p-decision-tool**

Same Dockerfile content but with `PORT=8081`.

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

ENV PORT=8081
EXPOSE ${PORT}
CMD ["node", "server.js"]
```

**Step 4: Create railway.toml for buss49p-decision-tool**

Same as lulea but check for /api/health endpoint.

**Step 5: Add health check endpoints if missing**

Check both `server.js` files for `/api/health` or similar. If missing, add:
```javascript
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));
```

**Step 6: Commit in each repo**

```bash
cd /Users/nicklaslundblad/lulea-decision-tool
git add Dockerfile railway.toml server.js
git commit -m "feat: add Dockerfile and Railway config for suite deployment"

cd /Users/nicklaslundblad/buss49p-decision-tool
git add Dockerfile railway.toml server.js
git commit -m "feat: add Dockerfile and Railway config for suite deployment"
```

---

### Task 4: Create combined Dockerfile for svenska_roster

svenska_roster currently has separate frontend/backend Dockerfiles for Docker Compose. Railway needs a single service. Create a combined Dockerfile that builds the frontend and serves it from the backend.

**Files:**
- Create: `/Users/nicklaslundblad/svenska_roster/Dockerfile` (root level, combined)
- Create: `/Users/nicklaslundblad/svenska_roster/railway.toml`
- Modify: `/Users/nicklaslundblad/svenska_roster/backend/main.py` — add static file serving

**Step 1: Add static file serving to the backend**

At the end of `backend/main.py` (after all API routes), add SPA fallback:

```python
# --- Static file serving for production (built frontend) ---
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse as _FileResponse

_STATIC_DIR = Path(os.environ.get("STATIC_DIR", ""))
if _STATIC_DIR.is_dir():
    # Serve assets first
    _assets = _STATIC_DIR / "assets"
    if _assets.is_dir():
        app.mount("/assets", StaticFiles(directory=_assets), name="static-assets")

    # SPA fallback: serve index.html for non-API routes
    @app.get("/{path:path}")
    async def spa_fallback(path: str):
        file_path = _STATIC_DIR / path
        if file_path.is_file():
            return _FileResponse(file_path)
        return _FileResponse(_STATIC_DIR / "index.html")
```

**Step 2: Create combined Dockerfile at repo root**

```dockerfile
# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + built frontend
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend-build /app/frontend/dist ./static

ENV STATIC_DIR=/app/static
ENV PORT=8000
EXPOSE ${PORT}
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
```

**Step 3: Create railway.toml**

```toml
[build]
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**Step 4: Commit**

```bash
cd /Users/nicklaslundblad/svenska_roster
git add Dockerfile railway.toml backend/main.py
git commit -m "feat: combined Dockerfile for Railway + static file serving"
```

---

### Task 5: Push all repos to GitHub

**Step 1: Create GitHub repo for portal**

```bash
cd /Users/nicklaslundblad/pa-verktygsladan
gh repo create the-grim-beeper/pa-verktygsladan --public --source=. --push
```

**Step 2: Push changes to existing repos**

```bash
cd /Users/nicklaslundblad/lulea-decision-tool && git push origin main
cd /Users/nicklaslundblad/buss49p-decision-tool && git push origin main
cd /Users/nicklaslundblad/svenska_roster && git push origin main
```

(media-trainer and decision-engine don't need changes yet — their Vite base config only matters when deployed behind the proxy, and the proxy strips the prefix so they work as-is.)

---

### Task 6: Verify portal works locally

**Step 1: Install deps and run portal**

```bash
cd /Users/nicklaslundblad/pa-verktygsladan
pip install -r requirements.txt
SITE_PASSWORD=test \
  MEDIA_TRAINER_URL=http://localhost:8000 \
  LULEA_TOOL_URL=http://localhost:8080 \
  SVENSKA_ROSTER_URL=http://localhost:8000 \
  BUSS49P_TOOL_URL=http://localhost:8081 \
  DECISION_ENGINE_URL=http://localhost:8080 \
  uvicorn app.main:app --port 9000
```

**Step 2: Test in browser**

- `http://localhost:9000/` → should show login page
- Enter password "test" → should show landing page with 5 cards
- Click any card → should proxy to that tool (if running locally)

**Step 3: Test health endpoint**

```bash
curl http://localhost:9000/api/health
# Expected: {"status":"ok"}
```

---

## Summary of Changes Per Repo

| Repo | Changes | New Files |
|------|---------|-----------|
| **pa-verktygsladan** (NEW) | Portal app: auth, landing page, reverse proxy | `app/main.py`, `app/config.py`, `app/proxy.py`, `app/landing.py`, `Dockerfile`, `railway.toml`, `requirements.txt` |
| **lulea-decision-tool** | Health endpoint (if missing) | `Dockerfile`, `railway.toml` |
| **buss49p-decision-tool** | Health endpoint (if missing) | `Dockerfile`, `railway.toml` |
| **svenska_roster** | Static file serving in backend | `Dockerfile` (root), `railway.toml` |
| **media-trainer** | No changes needed | — |
| **decision-engine** | No changes needed | — |

## Railway Deployment (after code is ready)

1. Create Railway project "pa-verktygsladan"
2. Add 6 services from GitHub repos
3. Set environment variables on each service (API keys, SITE_PASSWORD)
4. Make only the portal service public
5. Assign domain
