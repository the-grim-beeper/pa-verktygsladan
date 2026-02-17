import hashlib
import hmac

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response

from .config import settings, TOOL_ROUTES
from .landing import landing_page_html, LOGIN_PAGE
from .proxy import proxy_request

app = FastAPI(title="PA Verktygslådan")

_COOKIE_NAME = "pa_auth"
_TOKEN = (
    hashlib.sha256(settings.site_password.encode()).hexdigest()
    if settings.site_password
    else ""
)


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
            _COOKIE_NAME,
            _TOKEN,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )
        return response
    return HTMLResponse(
        LOGIN_PAGE.replace(
            "%%ERROR%%",
            '<p class="err" style="display:block">Fel lösenord</p>',
        ),
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


@app.api_route(
    "/tools/{tool_slug}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy(tool_slug: str, path: str, request: Request):
    if not _is_authenticated(request):
        return HTMLResponse(LOGIN_PAGE.replace("%%ERROR%%", ""), status_code=401)
    if tool_slug not in TOOL_ROUTES:
        return Response(content="Verktyget hittades inte", status_code=404)
    return await proxy_request(tool_slug, path, request)


# Handle /tools/{slug} and /tools/{slug}/ (no sub-path)
@app.api_route("/tools/{tool_slug}", methods=["GET"])
async def proxy_root(tool_slug: str, request: Request):
    if not _is_authenticated(request):
        return HTMLResponse(LOGIN_PAGE.replace("%%ERROR%%", ""), status_code=401)
    if tool_slug not in TOOL_ROUTES:
        return Response(content="Verktyget hittades inte", status_code=404)
    return await proxy_request(tool_slug, "", request)
