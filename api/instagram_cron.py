"""Authenticated Vercel Cron endpoint that refreshes the stored feed snapshot."""

from __future__ import annotations

import hmac
import json
import os
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Vercel may invoke this file with a function-local working directory, so make
# the project root importable before importing project modules.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.refresh_instagram import (  # noqa: E402
    blob_credential_status,
    cookies_configured,
    extract_posts,
    publish_feed_to_blob,
)


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

    def _log(self, message: str) -> None:
        # print() goes to the Vercel Function logs; never log secret values.
        print(f"[instagram_cron] {message}", file=sys.stderr, flush=True)

    def do_GET(self) -> None:
        authorized, reason = cron_authorization_status(self.headers.get("authorization"))
        if not authorized:
            status = 503 if reason.startswith("CRON_SECRET") else 401
            self._log(f"rejected: {reason} (status {status})")
            self._send_json(status, {"ok": False, "error": reason})
            return

        blob_status = blob_credential_status()
        self._log(
            "start: cookies_configured="
            f"{cookies_configured()} blob={blob_status}"
        )

        started = time.monotonic()
        try:
            # Serverless-safe: direct Instagram REST call when INSTAGRAM_USER_ID
            # is set, gallery-dl subprocess only as a local fallback.
            posts = extract_posts()
        except Exception as error:
            elapsed = time.monotonic() - started
            self._log(
                f"extract failed after {elapsed:.1f}s: {type(error).__name__}: {error}\n"
                f"{traceback.format_exc()}"
            )
            self._send_json(502, {
                "ok": False,
                "stage": "extract",
                "error": str(error),
            })
            return

        try:
            feed = publish_feed_to_blob(posts)
        except Exception as error:
            elapsed = time.monotonic() - started
            self._log(
                f"publish failed after {elapsed:.1f}s"
                f" ({len(posts)} posts extracted):"
                f" {type(error).__name__}: {error}\n"
                f"{traceback.format_exc()}"
            )
            self._send_json(502, {
                "ok": False,
                "stage": "publish",
                "error": str(error),
            })
            return

        elapsed = time.monotonic() - started
        self._log(f"success: {len(feed['posts'])} posts in {elapsed:.1f}s")
        self._send_json(200, {
            "ok": True,
            "posts": len(feed["posts"]),
            "fetchedAt": feed["fetchedAt"],
        })
