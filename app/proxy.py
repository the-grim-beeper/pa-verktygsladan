import logging

import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse, Response

from .config import TOOL_ROUTES

logger = logging.getLogger(__name__)

# Persistent async client (connection pooling, generous timeout for AI calls)
_client = httpx.AsyncClient(
    timeout=httpx.Timeout(300.0, connect=10.0),
    follow_redirects=True,
)


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

    # Forward headers (skip hop-by-hop headers)
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
    try:
        upstream = await _client.send(req, stream=True)
    except httpx.ConnectError:
        logger.error("Cannot connect to %s for tool '%s'", base_url, tool_slug)
        return Response(
            content=f"Tjänsten '{tool_slug}' är inte tillgänglig just nu.",
            status_code=502,
            media_type="text/plain; charset=utf-8",
        )
    except httpx.TimeoutException:
        logger.error("Timeout connecting to %s for tool '%s'", base_url, tool_slug)
        return Response(
            content=f"Tjänsten '{tool_slug}' svarar inte (timeout).",
            status_code=504,
            media_type="text/plain; charset=utf-8",
        )

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
            if key.lower() not in (
                "transfer-encoding", "connection",
                "content-encoding", "content-length",
            ):
                resp_headers[key] = value

        return Response(
            content=content,
            status_code=upstream.status_code,
            headers=resp_headers,
        )
