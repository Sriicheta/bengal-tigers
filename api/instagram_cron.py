"""Authenticated Vercel Cron endpoint that refreshes the stored feed snapshot."""

from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler

from scripts.refresh_instagram import extract_with_gallery_dl, publish_feed_to_blob


def cron_authorization_status(authorization: str | None) -> tuple[bool, str]:
    secret = os.environ.get("CRON_SECRET")
    if not secret:
        if os.environ.get("VERCEL"):
            return False, "CRON_SECRET is not configured"
        return True, "local development"

    supplied = authorization or ""
    expected = f"Bearer {secret}"
    if hmac.compare_digest(supplied, expected):
        return True, "authorized"
    return False, "invalid authorization"


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        authorized, reason = cron_authorization_status(self.headers.get("authorization"))
        if not authorized:
            status = 503 if reason.startswith("CRON_SECRET") else 401
            self._send_json(status, {"ok": False, "error": reason})
            return

        try:
            posts = extract_with_gallery_dl()
            feed = publish_feed_to_blob(posts)
        except Exception as error:
            self._send_json(502, {"ok": False, "error": str(error)})
            return

        self._send_json(200, {
            "ok": True,
            "posts": len(feed["posts"]),
            "fetchedAt": feed["fetchedAt"],
        })
