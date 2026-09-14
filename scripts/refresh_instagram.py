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
FETCH_TIMEOUT_DEFAULT = 240


def instagram_user_id() -> str | None:
    """Numeric Instagram user ID from the environment, if configured.

    Returns the stripped ID, or None when INSTAGRAM_USER_ID is unset/empty.
    Never logs or exposes cookie values; the ID itself is a public identifier.
    """
    raw = (os.environ.get("INSTAGRAM_USER_ID") or "").strip()
    if not raw:
        return None
    if not raw.isdigit():
        raise RuntimeError("INSTAGRAM_USER_ID must contain digits only")
    return raw


def instagram_target_url() -> str:
    """Posts URL for gallery-dl.

    Uses the stable ``id:<ID>`` form when INSTAGRAM_USER_ID is set, which
    bypasses gallery-dl's fragile username -> ID lookup (topsearch/web scrape)
    that raises ``NotFoundError: Requested user could not be found``.
    Falls back to the username-based POSTS_URL otherwise.
    """
    user_id = instagram_user_id()
    if user_id:
        return f"https://www.instagram.com/id:{user_id}/posts/"
    return POSTS_URL


INSTAGRAM_API_APP_ID = "936619743392459"
INSTAGRAM_API_TIMEOUT = 15
_CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Chrome/140.0 Safari/537.36"
)


def cookies_configured() -> bool:
    """True when Instagram session cookies were supplied (without revealing them)."""
    cookie_path = (os.environ.get("INSTAGRAM_COOKIES_FILE") or "").strip()
    encoded = (os.environ.get("INSTAGRAM_COOKIES_B64") or "").strip()
    return bool(cookie_path or encoded)


def blob_credential_status() -> dict[str, bool]:
    """Presence (not values) of the Blob credentials Vercel may inject."""
    return {
        "readWriteToken": bool(os.environ.get("BLOB_READ_WRITE_TOKEN")),
        "storeId": bool(os.environ.get("BLOB_STORE_ID")),
        "oidcToken": bool(os.environ.get("VERCEL_OIDC_TOKEN")),
    }


def has_blob_credentials() -> bool:
    """True when at least one Blob auth path looks available.

    The Python SDK accepts the legacy ``BLOB_READ_WRITE_TOKEN`` or the newer
    OIDC pair (``BLOB_STORE_ID`` plus an auto-injected ``VERCEL_OIDC_TOKEN``).
    A connected store historically injects the read-write token, so either
    form counts as configured here; the SDK raises the final verdict.
    """
    status = blob_credential_status()
    return bool(status["readWriteToken"] or status["storeId"])


def _fetch_timeout_seconds() -> int:
    """Subprocess budget for gallery-dl; override with INSTAGRAM_FETCH_TIMEOUT."""
    try:
        configured = int(os.environ.get("INSTAGRAM_FETCH_TIMEOUT", FETCH_TIMEOUT_DEFAULT))
    except (TypeError, ValueError):
        return FETCH_TIMEOUT_DEFAULT
    return max(10, min(configured, FETCH_TIMEOUT_DEFAULT))


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
    cookie_path = (os.environ.get("INSTAGRAM_COOKIES_FILE") or "").strip()
    if cookie_path:
        resolved = Path(cookie_path).expanduser().resolve()
        if not resolved.is_file():
            raise RuntimeError(f"INSTAGRAM_COOKIES_FILE does not exist: {resolved}")
        return resolved

    encoded = (os.environ.get("INSTAGRAM_COOKIES_B64") or "").strip()
    if not encoded:
        return None

    try:
        cookie_bytes = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise RuntimeError("INSTAGRAM_COOKIES_B64 is not valid base64") from error
    if not cookie_bytes:
        raise RuntimeError("INSTAGRAM_COOKIES_B64 decoded to empty content")

    temporary = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="instagram-cookies-")))
    cookie_file = temporary / "cookies.txt"
    cookie_file.write_bytes(cookie_bytes)
    return cookie_file


def extract_with_gallery_dl() -> list[dict[str, Any]]:
    import importlib.util

    if importlib.util.find_spec("gallery_dl") is None:
        raise RuntimeError(
            "gallery-dl module is not installed; "
            "check requirements.txt is installed for the function runtime"
        )

    with contextlib.ExitStack() as stack:
        cookie_file = _cookie_file_from_environment(stack)
        anonymous = cookie_file is None
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
        command.append(instagram_target_url())

        try:
            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=_fetch_timeout_seconds(),
                check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError(f"gallery-dl executable not found: {error}") from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                f"gallery-dl timed out after {error.timeout}s; "
                "Instagram may be throttling the function"
            ) from error

        if completed.returncode:
            stderr_text = (completed.stderr or "").strip()
            # Last few lines carry the actionable message; keep it bounded.
            tail = stderr_text.splitlines()[-3:] if stderr_text else []
            detail = " | ".join(line.strip() for line in tail if line.strip()) or "unknown error"
            hint = (
                " INSTAGRAM_COOKIES_B64/INSTAGRAM_COOKIES_FILE is not set;"
                " Instagram usually blocks anonymous automated fetches."
                if anonymous
                else " Session cookies may be expired; export fresh cookies and update INSTAGRAM_COOKIES_B64."
            )
            raise RuntimeError(f"gallery-dl exited with {completed.returncode}: {detail}.{hint}")

        stdout_text = completed.stdout or ""
        try:
            payload = json.loads(stdout_text)
        except json.JSONDecodeError as error:
            snippet = stdout_text.strip()[:200]
            raise RuntimeError(
                "gallery-dl returned invalid JSON"
                f"{'; stdout was: ' + snippet if snippet else '; stdout was empty'}"
            ) from error
        if not isinstance(payload, list):
            raise RuntimeError("gallery-dl returned an unexpected response")
        try:
            return parse_gallery_payload(payload)
        except RuntimeError as error:
            if anonymous:
                raise RuntimeError(
                    f"{error} (no Instagram session cookies were provided;"
                    " set INSTAGRAM_COOKIES_B64)"
                ) from error
            raise


def _cookie_jar_from_environment(stack: contextlib.ExitStack):
    """Load Instagram cookies into a jar without ever logging secret values."""
    import http.cookiejar

    cookie_path = (os.environ.get("INSTAGRAM_COOKIES_FILE") or "").strip()
    if cookie_path:
        resolved = Path(cookie_path).expanduser().resolve()
        if not resolved.is_file():
            raise RuntimeError(f"INSTAGRAM_COOKIES_FILE does not exist: {resolved}")
        jar = http.cookiejar.MozillaCookieJar(str(resolved))
        jar.load(ignore_discard=True, ignore_expires=True)
        return jar

    encoded = (os.environ.get("INSTAGRAM_COOKIES_B64") or "").strip()
    if not encoded:
        return None

    try:
        cookie_bytes = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise RuntimeError("INSTAGRAM_COOKIES_B64 is not valid base64") from error
    if not cookie_bytes:
        raise RuntimeError("INSTAGRAM_COOKIES_B64 decoded to empty content")

    temporary = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="instagram-cookies-")))
    cookie_file = temporary / "cookies.txt"
    cookie_file.write_bytes(cookie_bytes)
    jar = http.cookiejar.MozillaCookieJar(str(cookie_file))
    try:
        jar.load(ignore_discard=True, ignore_expires=True)
    except Exception as error:
        raise RuntimeError("Instagram cookies could not be parsed") from error
    return jar


def _csrf_token_from_jar(jar) -> str:
    import secrets

    if jar is not None:
        for cookie in jar:
            if cookie.name == "csrftoken" and cookie.value:
                return cookie.value
    return secrets.token_hex(16)


def parse_rest_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """Map one Instagram REST feed item to the internal post shape.

    Returns None for items without usable media so callers can skip them.
    """
    if not isinstance(item, dict):
        return None
    code = str(item.get("code") or "")
    if not code:
        return None

    candidates: list[Any] = []
    image_versions = item.get("image_versions2") or {}
    if isinstance(image_versions, dict):
        raw_candidates = image_versions.get("candidates")
        if isinstance(raw_candidates, list):
            candidates = raw_candidates
    if not candidates and isinstance(item.get("carousel_media"), list):
        for child in item["carousel_media"]:
            if isinstance(child, dict):
                child_versions = child.get("image_versions2") or {}
                if isinstance(child_versions, dict) and isinstance(child_versions.get("candidates"), list):
                    candidates = child_versions["candidates"]
                    break
    image_url = ""
    for candidate in candidates:
        if isinstance(candidate, dict) and str(candidate.get("url") or "").startswith("http"):
            image_url = str(candidate["url"])
            break
    if not image_url:
        return None

    caption_value = item.get("caption")
    if isinstance(caption_value, dict):
        caption = str(caption_value.get("text") or "").strip()
    elif isinstance(caption_value, str):
        caption = caption_value.strip()
    else:
        caption = ""

    product_type = str(item.get("product_type") or "")
    media_type = item.get("media_type")
    # media_type: 1 = photo, 2 = video/reel, 8 = carousel. Mirrors the
    # previous gallery-dl mapping where video counts as reel.
    is_reel = product_type == "clips" or media_type == 2
    post_type = "reel" if is_reel else "post"
    post_url = (
        f"https://www.instagram.com/reel/{code}/"
        if is_reel
        else f"https://www.instagram.com/p/{code}/"
    )

    return {
        "id": code,
        "shortcode": code,
        "url": post_url,
        "caption": caption,
        "publishedAt": _iso_datetime(item.get("taken_at")),
        "likes": _integer(item.get("like_count")),
        "comments": _integer(item.get("comment_count")),
        "type": post_type,
        "sourceImage": image_url,
        "headers": {},
    }


def parse_rest_feed(data: Any) -> list[dict[str, Any]]:
    """Turn an Instagram REST feed response into up to POST_LIMIT posts."""
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        raise RuntimeError("Instagram returned no usable posts")
    posts: list[dict[str, Any]] = []
    for item in items:
        parsed = parse_rest_item(item)
        if parsed is not None:
            posts.append(parsed)
    if not posts:
        raise RuntimeError("Instagram returned no usable posts")
    ordered = sorted(posts, key=lambda post: post["publishedAt"], reverse=True)
    return ordered[:POST_LIMIT]


def extract_with_instagram_api() -> list[dict[str, Any]]:
    """Fetch the latest posts via a single in-process Instagram REST call.

    This is the Vercel-serverless-safe path: one HTTPS request with
    ``requests`` (already a dependency), no ``subprocess`` child interpreter,
    no gallery-dl import, no multi-second request-interval sleeps. Uses the
    pinned INSTAGRAM_USER_ID so no username -> ID lookup is needed.
    """
    user_id = instagram_user_id()
    if not user_id:
        raise RuntimeError("INSTAGRAM_USER_ID is not configured")

    with contextlib.ExitStack() as stack:
        jar = _cookie_jar_from_environment(stack)
        if jar is None:
            raise RuntimeError(
                "INSTAGRAM_COOKIES_B64/INSTAGRAM_COOKIES_FILE is not set;"
                " Instagram usually blocks anonymous automated fetches."
            )
        has_session = any(cookie.name == "sessionid" and cookie.value for cookie in jar)
        if not has_session:
            raise RuntimeError(
                "Instagram session cookie is missing;"
                " export fresh cookies and update INSTAGRAM_COOKIES_B64."
            )

        session = requests.Session()
        session.cookies.update({cookie.name: cookie.value for cookie in jar if cookie.value})
        session.headers.update({
            "Accept": "*/*",
            "User-Agent": _CHROME_UA,
            "X-CSRFToken": _csrf_token_from_jar(jar),
            "X-IG-App-ID": INSTAGRAM_API_APP_ID,
            "X-ASBD-ID": "129477",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": PROFILE_URL,
        })

        url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/"
        try:
            response = session.get(url, params={"count": 30}, timeout=INSTAGRAM_API_TIMEOUT)
        except requests.Timeout as error:
            raise RuntimeError("Instagram request timed out; Instagram may be throttling") from error
        except requests.RequestException as error:
            raise RuntimeError(f"Instagram request failed: {type(error).__name__}") from error

        if response.status_code == 401 or response.status_code == 403:
            raise RuntimeError(
                "Instagram rejected the session;"
                " export fresh cookies and update INSTAGRAM_COOKIES_B64."
            )
        if response.status_code == 404:
            raise RuntimeError("Instagram user could not be found")
        if response.status_code == 429:
            raise RuntimeError("Instagram is rate limiting; try again later")
        if response.status_code >= 400:
            raise RuntimeError(f"Instagram request failed with status {response.status_code}")
        try:
            data = response.json()
        except ValueError as error:
            raise RuntimeError("Instagram returned an unexpected response") from error
        return parse_rest_feed(data)


def extract_posts() -> list[dict[str, Any]]:
    """Serverless-safe entry point: direct API when ID is set, gallery-dl otherwise.

    Keeps local gallery-dl behavior intact while letting Vercel avoid the
    subprocess path that exceeds serverless timeouts.
    """
    if instagram_user_id():
        return extract_with_instagram_api()
    return extract_with_gallery_dl()


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
    if put_blob is None and not has_blob_credentials():
        status = blob_credential_status()
        raise RuntimeError(
            "Vercel Blob credentials are not configured;"
            " connect a Blob store (BLOB_READ_WRITE_TOKEN or BLOB_STORE_ID)"
            f" [readWriteToken={status['readWriteToken']},"
            f" storeId={status['storeId']}, oidcToken={status['oidcToken']}]"
        )
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
    if has_blob_credentials():
        try:
            return read_blob_feed(), "blob"
        except Exception as error:
            print(
                f"Instagram Blob read failed ({type(error).__name__}: {error});"
                " serving static fallback",
                file=sys.stderr,
            )
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
