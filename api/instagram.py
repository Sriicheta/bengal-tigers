"""Public read-only Instagram feed endpoint backed by Vercel Blob."""

from __future__ import annotations

import copy
import json
import sys
from http.server import BaseHTTPRequestHandler

from scripts.refresh_instagram import load_feed_snapshot


def _request_origin(request: BaseHTTPRequestHandler) -> str:
    protocol = request.headers.get("x-forwarded-proto", "http")
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "localhost")
    return f"{protocol}://{host}".rstrip("/")


def _absolute_fallback_images(feed: dict, origin: str) -> dict:
    result = copy.deepcopy(feed)
    for post in result.get("posts", []):
        image = post.get("image")
        if isinstance(image, str) and image.startswith("/"):
            post["image"] = f"{origin}{image}"
    return result


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict, source: str) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=60, s-maxage=300, stale-while-revalidate=86400")
        self.send_header("X-Instagram-Feed-Source", source)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _handle(self) -> None:
        try:
            feed, source = load_feed_snapshot()
            feed = _absolute_fallback_images(feed, _request_origin(self))
            self._send_json(200, feed, source)
        except Exception as error:
            print(f"Instagram feed read failed: {error}", file=sys.stderr)
            self._send_json(503, {"error": "Instagram feed is temporarily unavailable"}, "error")

    def do_GET(self) -> None:
        self._handle()

    def do_HEAD(self) -> None:
        self._handle()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()
