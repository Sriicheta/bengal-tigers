"""Refresh the static Instagram feed used by the Vite site.

gallery-dl does the Instagram extraction. This script keeps the public contract
small, downloads stable local thumbnails, and atomically replaces the feed only
after every post has been processed successfully.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = PROJECT_ROOT / "public"
MEDIA_ROOT = PUBLIC_ROOT / "instagram"
FEED_PATH = PUBLIC_ROOT / "data" / "instagram-posts.json"
BLOB_FEED_PATH = "instagram/feed.json"

USERNAME = "bengaltigers.ccl"
PROFILE_URL = f"https://www.instagram.com/{USERNAME}/"
POSTS_URL = f"{PROFILE_URL}posts/"
POST_LIMIT = 6


def _iso_datetime(value: Any) -> str:
    if isinstance(value, (int, float)):
        parsed = datetime.fromtimestamp(value, tz=UTC)
    elif isinstance(value, str) and value.strip():
        text = value.strip().replace(" ", "T")
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return value.strip()
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        parsed = parsed.astimezone(UTC)
    else:
        return ""

    return parsed.isoformat(timespec="seconds").replace("+00:00", "Z")


def _integer(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first_present(metadata: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in metadata and metadata[key] is not None:
            return metadata[key]
    return None


def parse_gallery_payload(payload: list[Any]) -> list[dict[str, Any]]:
    """Turn gallery-dl message tuples into one card per Instagram post."""
    errors = [row[1] for row in payload if isinstance(row, list) and row and row[0] == -1]
    if errors:
        message = "; ".join(str(error.get("message", error)) for error in errors)
        raise RuntimeError(f"gallery-dl could not read the profile: {message}")

    posts: dict[str, dict[str, Any]] = {}
    for row in payload:
        if not isinstance(row, list) or len(row) < 3 or row[0] != 3:
            continue

        source_image, metadata = row[1], row[2]
        if not isinstance(source_image, str) or not source_image.startswith("http"):
            continue
        if not isinstance(metadata, dict) or _integer(metadata.get("num")) not in (None, 1):
            continue

        shortcode = str(metadata.get("post_shortcode") or metadata.get("shortcode") or "")
        if not shortcode or shortcode in posts:
            continue

        post_url = str(metadata.get("post_url") or f"https://www.instagram.com/p/{shortcode}/")
        post_type = str(metadata.get("type") or ("reel" if "/reel/" in post_url else "post"))
        published_at = _iso_datetime(metadata.get("post_date") or metadata.get("date"))

        posts[shortcode] = {
            "id": shortcode,
            "shortcode": shortcode,
            "url": post_url,
            "caption": str(metadata.get("description") or "").strip(),
            "publishedAt": published_at,
            "likes": _integer(_first_present(metadata, "likes", "like_count")),
            "comments": _integer(_first_present(metadata, "comments", "comment_count")),
            "type": "reel" if post_type in {"reel", "video"} else "post",
            "sourceImage": source_image,
            "headers": metadata.get("_http_headers") if isinstance(metadata.get("_http_headers"), dict) else {},
        }

    ordered = sorted(posts.values(), key=lambda post: post["publishedAt"], reverse=True)
    if not ordered:
        raise RuntimeError("gallery-dl returned no usable Instagram posts")
    return ordered[:POST_LIMIT]


def _cookie_file_from_environment(stack: contextlib.ExitStack) -> Path | None:
    cookie_path = os.environ.get("INSTAGRAM_COOKIES_FILE")
    if cookie_path:
        resolved = Path(cookie_path).expanduser().resolve()
        if not resolved.is_file():
            raise RuntimeError(f"INSTAGRAM_COOKIES_FILE does not exist: {resolved}")
        return resolved

    encoded = os.environ.get("INSTAGRAM_COOKIES_B64")
    if not encoded:
        return None

    try:
        cookie_bytes = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise RuntimeError("INSTAGRAM_COOKIES_B64 is not valid base64") from error

    temporary = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="instagram-cookies-")))
    cookie_file = temporary / "cookies.txt"
    cookie_file.write_bytes(cookie_bytes)
    return cookie_file


def extract_with_gallery_dl() -> list[dict[str, Any]]:
    with contextlib.ExitStack() as stack:
        cookie_file = _cookie_file_from_environment(stack)
        command = [
            sys.executable,
            "-m",
            "gallery_dl",
            "--dump-json",
            "-o",
            "extractor.instagram.include=posts",
            "-o",
            "extractor.instagram.max-posts=12",
            "-o",
            "extractor.instagram.previews=video",
            "-o",
            "extractor.instagram.videos=false",
        ]
        if cookie_file:
            command.extend(("--cookies", str(cookie_file)))
        command.append(POSTS_URL)

        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )
        if completed.returncode:
            detail = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "unknown error"
            raise RuntimeError(f"gallery-dl exited with {completed.returncode}: {detail}")

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError("gallery-dl returned invalid JSON") from error
        if not isinstance(payload, list):
            raise RuntimeError("gallery-dl returned an unexpected response")
        return parse_gallery_payload(payload)


def load_seed(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    posts = data.get("posts") if isinstance(data, dict) else None
    if not isinstance(posts, list) or not posts:
        raise RuntimeError("seed file must contain a non-empty posts array")
    return posts[:POST_LIMIT]


def _image_extension(response: requests.Response) -> str:
    content_type = response.headers.get("content-type", "").partition(";")[0].lower()
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(content_type, ".jpg")


def _public_post(post: dict[str, Any], image: str) -> dict[str, Any]:
    shortcode = re.sub(r"[^A-Za-z0-9_-]", "", str(post.get("shortcode") or post.get("id") or ""))
    if not shortcode:
        raise RuntimeError("each post needs a valid shortcode")

    return {
        "id": str(post.get("id") or shortcode),
        "shortcode": shortcode,
        "url": str(post.get("url") or f"https://www.instagram.com/p/{shortcode}/"),
        "caption": str(post.get("caption") or "").strip(),
        "image": image,
        "publishedAt": _iso_datetime(post.get("publishedAt")),
        "likes": _integer(post.get("likes")),
        "comments": _integer(post.get("comments")),
        "type": "reel" if post.get("type") == "reel" else "post",
    }


def _feed_document(public_posts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "account": {
            "username": USERNAME,
            "handle": f"@{USERNAME}",
            "url": PROFILE_URL,
        },
        "fetchedAt": datetime.now(tz=UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "posts": public_posts,
    }


def _validate_feed(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or not isinstance(value.get("posts"), list) or not value["posts"]:
        raise RuntimeError("stored Instagram feed has an invalid shape")
    return value


def build_remote_feed(posts: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the backend snapshot using Instagram CDN thumbnail URLs."""
    public_posts = []
    for post in posts[:POST_LIMIT]:
        source_image = str(post.get("sourceImage") or "")
        if not source_image.startswith("http"):
            raise RuntimeError("each post needs an HTTP sourceImage")
        public_posts.append(_public_post(post, source_image))
    return _feed_document(public_posts)


def publish_feed_to_blob(posts: list[dict[str, Any]], put_blob=None) -> dict[str, Any]:
    """Atomically replace the private Vercel Blob JSON snapshot."""
    if put_blob is None:
        from vercel.blob import put as put_blob

    feed = build_remote_feed(posts)
    body = (json.dumps(feed, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    put_blob(
        BLOB_FEED_PATH,
        body,
        access="private",
        content_type="application/json",
        overwrite=True,
        cache_control_max_age=60,
    )
    return feed


def read_blob_feed(get_blob=None) -> dict[str, Any]:
    if get_blob is None:
        from vercel.blob import get as get_blob

    result = get_blob(BLOB_FEED_PATH, access="private", use_cache=False, timeout=15)
    return _validate_feed(json.loads(result.content))


def read_static_feed() -> dict[str, Any]:
    return _validate_feed(json.loads(FEED_PATH.read_text(encoding="utf-8")))


def load_feed_snapshot() -> tuple[dict[str, Any], str]:
    """Read Blob in production, falling back to the bundled bootstrap snapshot."""
    if os.environ.get("BLOB_READ_WRITE_TOKEN"):
        try:
            return read_blob_feed(), "blob"
        except Exception:
            pass
    return read_static_feed(), "static-fallback"


def write_feed(posts: list[dict[str, Any]]) -> None:
    MEDIA_ROOT.parent.mkdir(parents=True, exist_ok=True)
    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    expected_names: set[str] = set()

    with tempfile.TemporaryDirectory(prefix="instagram-media-", dir=PUBLIC_ROOT) as temporary_name:
        staging = Path(temporary_name)
        public_posts: list[dict[str, Any]] = []

        for post in posts:
            shortcode = re.sub(r"[^A-Za-z0-9_-]", "", str(post.get("shortcode") or post.get("id") or ""))
            source_image = str(post.get("sourceImage") or "")
            if not shortcode or not source_image.startswith("http"):
                raise RuntimeError("each post needs a shortcode and an HTTP sourceImage")

            headers = {
                "Referer": PROFILE_URL,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36",
                **{str(key): str(value) for key, value in dict(post.get("headers") or {}).items()},
            }
            response = requests.get(source_image, headers=headers, timeout=30)
            response.raise_for_status()
            if not response.headers.get("content-type", "").lower().startswith("image/"):
                raise RuntimeError(f"Instagram returned non-image content for {shortcode}")
            extension = _image_extension(response)
            filename = f"{shortcode}{extension}"
            (staging / filename).write_bytes(response.content)

            public_posts.append(_public_post(post, f"/instagram/{filename}"))

        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        expected_names = {Path(post["image"]).name for post in public_posts}
        for staged_file in staging.iterdir():
            os.replace(staged_file, MEDIA_ROOT / staged_file.name)

    feed = _feed_document(public_posts)
    temporary_feed = FEED_PATH.with_suffix(".json.tmp")
    temporary_feed.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary_feed, FEED_PATH)
    for old_file in MEDIA_ROOT.iterdir():
        if old_file.is_file() and old_file.name not in expected_names:
            old_file.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, help="bootstrap from a structured local seed file")
    parser.add_argument("--blob", action="store_true", help="publish the snapshot to Vercel Blob")
    args = parser.parse_args()

    try:
        posts = load_seed(args.seed.resolve()) if args.seed else extract_with_gallery_dl()
        if args.blob:
            publish_feed_to_blob(posts)
        else:
            write_feed(posts)
    except Exception as error:
        print(f"Instagram refresh failed; the existing static feed was left untouched: {error}", file=sys.stderr)
        return 1

    print(f"Updated {FEED_PATH.relative_to(PROJECT_ROOT)} with {len(posts)} posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
