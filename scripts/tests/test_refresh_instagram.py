import sys
import unittest
from unittest.mock import patch
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.instagram import _absolute_fallback_images  # noqa: E402
from api.instagram_cron import cron_authorization_status  # noqa: E402
from refresh_instagram import (  # noqa: E402
    POSTS_URL,
    _cookie_jar_from_environment,
    _instagrapi_device_seed,
    _safe_response_diagnosis,
    _sessionid_from_jar,
    extract_posts,
    extract_with_gallery_dl,
    extract_with_instagram_api,
    extract_with_instagrapi,
    instagram_target_url,
    instagram_user_id,
    parse_gallery_payload,
    parse_instagrapi_media,
    parse_rest_feed,
    parse_rest_item,
    publish_feed_to_blob,
)


class ParseGalleryPayloadTests(unittest.TestCase):
    def test_keeps_one_image_per_post_and_sorts_newest_first(self):
        payload = [
            [2, {"post_shortcode": "older"}],
            [3, "https://cdn.example/older-1.jpg", {
                "post_shortcode": "older",
                "post_url": "https://www.instagram.com/p/older/",
                "post_date": "2026-08-01 08:00:00",
                "description": "Older caption",
                "likes": 12,
                "comments": 0,
                "num": 1,
                "type": "post",
            }],
            [3, "https://cdn.example/older-2.jpg", {
                "post_shortcode": "older",
                "post_date": "2026-08-01 08:00:00",
                "num": 2,
            }],
            [3, "https://cdn.example/newer.jpg", {
                "post_shortcode": "newer",
                "post_url": "https://www.instagram.com/reel/newer/",
                "post_date": "2026-08-02T09:30:00Z",
                "description": "Newer caption",
                "like_count": "42",
                "comment_count": 3,
                "type": "reel",
            }],
        ]

        posts = parse_gallery_payload(payload)

        self.assertEqual([post["shortcode"] for post in posts], ["newer", "older"])
        self.assertEqual(posts[0]["publishedAt"], "2026-08-02T09:30:00Z")
        self.assertEqual(posts[0]["likes"], 42)
        self.assertEqual(posts[0]["comments"], 3)
        self.assertEqual(posts[0]["type"], "reel")
        self.assertEqual(posts[1]["sourceImage"], "https://cdn.example/older-1.jpg")
        self.assertEqual(posts[1]["comments"], 0)

    def test_surfaces_gallery_dl_errors(self):
        with self.assertRaisesRegex(RuntimeError, "rate limited"):
            parse_gallery_payload([[-1, {"message": "rate limited"}]])

    def test_publishes_one_private_blob_snapshot(self):
        calls = []
        posts = [{
            "id": "shortcode",
            "shortcode": "shortcode",
            "url": "https://www.instagram.com/p/shortcode/",
            "caption": "A live post",
            "publishedAt": "2026-08-31T09:10:25Z",
            "likes": 10,
            "comments": 0,
            "type": "post",
            "sourceImage": "https://cdn.example/post.jpg",
        }]

        def fake_put(path, body, **options):
            calls.append((path, body, options))

        feed = publish_feed_to_blob(posts, put_blob=fake_put)

        self.assertEqual(feed["posts"][0]["image"], "https://cdn.example/post.jpg")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "instagram/feed.json")
        self.assertEqual(calls[0][2]["access"], "private")
        self.assertTrue(calls[0][2]["overwrite"])
        self.assertIn(b'"shortcode":"shortcode"', calls[0][1])


class InstagramTargetUrlTests(unittest.TestCase):
    def test_falls_back_to_username_url_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(instagram_user_id())
            self.assertEqual(instagram_target_url(), POSTS_URL)

    def test_uses_id_url_when_configured(self):
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            self.assertEqual(instagram_user_id(), "64565332872")
            self.assertEqual(
                instagram_target_url(),
                "https://www.instagram.com/id:64565332872/posts/",
            )

    def test_strips_whitespace(self):
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "  64565332872  "}, clear=True):
            self.assertEqual(instagram_target_url(), "https://www.instagram.com/id:64565332872/posts/")

    def test_rejects_non_numeric_id(self):
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "bengaltigers.ccl"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "digits only"):
                instagram_target_url()

    def test_extract_passes_id_url_to_gallery_dl(self):
        captured = {}

        class Completed:
            returncode = 0
            stdout = "[]"
            stderr = ""

        def fake_run(command, **kwargs):
            captured["command"] = command
            return Completed()

        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            with patch("refresh_instagram.subprocess.run", side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError, "no usable Instagram posts"):
                    extract_with_gallery_dl()
        self.assertIn("https://www.instagram.com/id:64565332872/posts/", captured["command"])
        self.assertNotIn(POSTS_URL, captured["command"])

    def test_extract_falls_back_to_username_url(self):
        captured = {}

        class Completed:
            returncode = 0
            stdout = "[]"
            stderr = ""

        def fake_run(command, **kwargs):
            captured["command"] = command
            return Completed()

        with patch.dict("os.environ", {}, clear=True):
            with patch("refresh_instagram.subprocess.run", side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError, "no usable Instagram posts"):
                    extract_with_gallery_dl()
        self.assertIn(POSTS_URL, captured["command"])


class ParseRestFeedTests(unittest.TestCase):
    def _photo_item(self, code="Abc123", taken_at=1756680000):
        return {
            "pk": "123",
            "code": code,
            "taken_at": taken_at,
            "like_count": 10,
            "comment_count": 2,
            "caption": {"text": "Hello"},
            "media_type": 1,
            "product_type": "feed",
            "image_versions2": {"candidates": [{"url": "https://cdn.example/a.jpg"}]},
        }

    def test_photo_maps_to_post(self):
        post = parse_rest_item(self._photo_item())
        self.assertEqual(post["shortcode"], "Abc123")
        self.assertEqual(post["url"], "https://www.instagram.com/p/Abc123/")
        self.assertEqual(post["type"], "post")
        self.assertEqual(post["sourceImage"], "https://cdn.example/a.jpg")
        self.assertEqual(post["caption"], "Hello")
        self.assertEqual(post["likes"], 10)
        self.assertEqual(post["comments"], 2)
        self.assertTrue(post["publishedAt"].endswith("Z"))

    def test_clips_maps_to_reel(self):
        item = self._photo_item(code="Reel1")
        item["product_type"] = "clips"
        item["media_type"] = 2
        post = parse_rest_item(item)
        self.assertEqual(post["type"], "reel")
        self.assertEqual(post["url"], "https://www.instagram.com/reel/Reel1/")

    def test_video_maps_to_reel(self):
        item = self._photo_item(code="Vid1")
        item["media_type"] = 2
        item["product_type"] = "feed"
        post = parse_rest_item(item)
        self.assertEqual(post["type"], "reel")

    def test_skips_items_without_media(self):
        self.assertIsNone(parse_rest_item({"code": "X"}))
        self.assertIsNone(parse_rest_item({}))
        self.assertIsNone(parse_rest_item(None))

    def test_feed_sorts_newest_first_and_limits(self):
        from refresh_instagram import POST_LIMIT

        items = [self._photo_item(code=f"P{i}", taken_at=1756680000 + i) for i in range(POST_LIMIT + 3)]
        posts = parse_rest_feed({"items": items})
        self.assertEqual(len(posts), POST_LIMIT)
        self.assertEqual(posts[0]["shortcode"], f"P{POST_LIMIT + 2}")

    def test_feed_rejects_empty(self):
        with self.assertRaisesRegex(RuntimeError, "no usable posts"):
            parse_rest_feed({"items": []})
        with self.assertRaisesRegex(RuntimeError, "no usable posts"):
            parse_rest_feed({})


class ExtractWithInstagramApiTests(unittest.TestCase):
    def _photo_item(self, code="Abc123"):
        return {
            "pk": "123",
            "code": code,
            "taken_at": 1756680000,
            "like_count": 5,
            "comment_count": 1,
            "caption": {"text": "Hi"},
            "media_type": 1,
            "product_type": "feed",
            "image_versions2": {"candidates": [{"url": "https://cdn.example/a.jpg"}]},
        }

    def _fake_session(self, status=200, payload=None):
        from unittest.mock import MagicMock

        response = MagicMock()
        response.status_code = status
        response.json.return_value = payload if payload is not None else {"items": [self._photo_item()]}
        session = MagicMock()
        session.get.return_value = response
        return session

    def _cookie_jar(self):
        from types import SimpleNamespace

        return [
            SimpleNamespace(name="sessionid", value="sess"),
            SimpleNamespace(name="csrftoken", value="csrf"),
        ]

    def test_requires_user_id(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "INSTAGRAM_USER_ID"):
                extract_with_instagram_api()

    def test_requires_cookies(self):
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "INSTAGRAM_COOKIES"):
                extract_with_instagram_api()

    def test_success_single_request(self):
        import refresh_instagram

        session = self._fake_session()
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            with patch.object(refresh_instagram, "_cookie_jar_from_environment", return_value=self._cookie_jar()):
                with patch.object(refresh_instagram.requests, "Session", return_value=session):
                    posts = extract_with_instagram_api()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["shortcode"], "Abc123")
        # Single REST call, no pagination, bounded timeout.
        session.get.assert_called_once()
        _, kwargs = session.get.call_args
        self.assertEqual(kwargs.get("timeout"), 15)

    def test_rejected_session(self):
        import refresh_instagram

        session = self._fake_session(status=401)
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            with patch.object(refresh_instagram, "_cookie_jar_from_environment", return_value=self._cookie_jar()):
                with patch.object(refresh_instagram.requests, "Session", return_value=session):
                    with self.assertRaisesRegex(RuntimeError, "rejected the session"):
                        extract_with_instagram_api()

    def test_extract_posts_routes_to_instagrapi_when_id_set(self):
        import refresh_instagram

        sentinel = [{"id": "x"}]
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            with patch.object(refresh_instagram, "extract_with_instagrapi", return_value=sentinel) as iga:
                with patch.object(refresh_instagram, "extract_with_instagram_api") as api:
                    with patch.object(refresh_instagram, "extract_with_gallery_dl") as gallery:
                        self.assertEqual(extract_posts(), sentinel)
                        iga.assert_called_once()
                        api.assert_not_called()
                        gallery.assert_not_called()

    def test_extract_posts_falls_back_to_rest_when_instagrapi_fails(self):
        import refresh_instagram

        sentinel = [{"id": "x"}]
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
            with patch.object(
                refresh_instagram, "extract_with_instagrapi", side_effect=RuntimeError("challenge")
            ):
                with patch.object(refresh_instagram, "extract_with_instagram_api", return_value=sentinel) as api:
                    with patch.object(refresh_instagram, "extract_with_gallery_dl") as gallery:
                        self.assertEqual(extract_posts(), sentinel)
                        api.assert_called_once()
                        gallery.assert_not_called()

    def test_extract_posts_falls_back_to_gallery_dl(self):
        import refresh_instagram

        sentinel = [{"id": "x"}]
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(refresh_instagram, "extract_with_gallery_dl", return_value=sentinel) as gallery:
                self.assertEqual(extract_posts(), sentinel)
                gallery.assert_called_once()


class CookieJarParsingTests(unittest.TestCase):
    def _netscape_line(self, domain=".instagram.com", path="/", name="sessionid", value="sess", expires="9999999999"):
        return "\t".join([domain, "TRUE", path, "TRUE", expires, name, value])

    def _production_like_text(self):
        # Mirrors the reported production file: no magic header, 7 tab fields,
        # duplicate csrftoken/sessionid entries for .instagram.com.
        return "\n".join([
            self._netscape_line(path="/", name="csrftoken", value="csrf-a"),
            self._netscape_line(path="/", name="sessionid", value="sess-a"),
            self._netscape_line(path="/", name="csrftoken", value="csrf-b"),
            self._netscape_line(path="/", name="sessionid", value="sess-b"),
            "",
        ]) + "\n"

    def _jar_from_b64_text(self, text):
        import base64
        import contextlib

        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        with patch.dict("os.environ", {"INSTAGRAM_COOKIES_B64": encoded}, clear=True):
            with contextlib.ExitStack() as stack:
                return _cookie_jar_from_environment(stack)

    def test_headerless_duplicates_parse(self):
        jar = self._jar_from_b64_text(self._production_like_text())
        names = {cookie.name for cookie in jar}
        self.assertIn("sessionid", names)
        self.assertIn("csrftoken", names)
        session_values = [cookie.value for cookie in jar if cookie.name == "sessionid" and cookie.value]
        self.assertTrue(session_values)

    def test_magic_header_still_parses(self):
        text = "# Netscape HTTP Cookie File\n" + self._production_like_text()
        jar = self._jar_from_b64_text(text)
        self.assertIn("sessionid", {cookie.name for cookie in jar})

    def test_httponly_comments_and_malformed_lines_skipped(self):
        text = "\n".join([
            "# This is a comment",
            "",
            "not-a-cookie-line",
            "a\tb\tc",
            "#HttpOnly.instagram.com\tTRUE\t/\tTRUE\t9999999999\tsessionid\tsess-h",
            self._netscape_line(name="csrftoken", value="csrf-h"),
        ]) + "\n"
        jar = self._jar_from_b64_text(text)
        names = {cookie.name for cookie in jar}
        self.assertIn("sessionid", names)
        self.assertIn("csrftoken", names)

    def test_garbage_raises_parse_error(self):
        import contextlib

        import base64

        encoded = base64.b64encode(b"no cookies here\njust text\n").decode("ascii")
        with patch.dict("os.environ", {"INSTAGRAM_COOKIES_B64": encoded}, clear=True):
            with contextlib.ExitStack() as stack:
                with self.assertRaisesRegex(RuntimeError, "could not be parsed"):
                    _cookie_jar_from_environment(stack)

    def test_cookie_file_path_headerless_parses(self):
        import contextlib
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "cookies.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(self._production_like_text())
            with patch.dict("os.environ", {"INSTAGRAM_COOKIES_FILE": path}, clear=True):
                with contextlib.ExitStack() as stack:
                    jar = _cookie_jar_from_environment(stack)
        self.assertIn("sessionid", {cookie.name for cookie in jar})

    def test_extract_api_works_with_production_like_cookies(self):
        import base64
        import refresh_instagram

        encoded = base64.b64encode(self._production_like_text().encode("utf-8")).decode("ascii")

        def _photo_item(code="Abc123"):
            return {
                "pk": "123",
                "code": code,
                "taken_at": 1756680000,
                "like_count": 5,
                "comment_count": 1,
                "caption": {"text": "Hi"},
                "media_type": 1,
                "product_type": "feed",
                "image_versions2": {"candidates": [{"url": "https://cdn.example/a.jpg"}]},
            }

        from unittest.mock import MagicMock

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"items": [_photo_item()]}
        session = MagicMock()
        session.get.return_value = response

        with patch.dict(
            "os.environ",
            {"INSTAGRAM_USER_ID": "64565332872", "INSTAGRAM_COOKIES_B64": encoded},
            clear=True,
        ):
            with patch.object(refresh_instagram.requests, "Session", return_value=session):
                posts = extract_with_instagram_api()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["shortcode"], "Abc123")


class ResponseDiagnosisTests(unittest.TestCase):
    SECRET = "sess-fake-secret-9f8e7d"

    def _fake_jar(self):
        from types import SimpleNamespace

        return [
            SimpleNamespace(name="sessionid", value="sess"),
            SimpleNamespace(name="csrftoken", value="csrf"),
        ]

    def _response(self, status=200, url="https://www.instagram.com/api/v1/feed/user/64565332872/",
                  content_type="application/json", body=b"", json_data=None, json_raises=True):
        from unittest.mock import MagicMock

        response = MagicMock()
        response.status_code = status
        response.url = url
        response.headers = {"content-type": content_type}
        response.content = body
        response.text = body.decode("utf-8", errors="replace")
        if json_raises:
            response.json.side_effect = ValueError("No JSON object could be decoded")
        else:
            response.json.return_value = json_data
        return response

    def _run_extract(self, response):
        import refresh_instagram
        from unittest.mock import MagicMock

        session = MagicMock()
        session.get.return_value = response
        with patch.dict(
            "os.environ",
            {"INSTAGRAM_USER_ID": "64565332872", "INSTAGRAM_COOKIES_B64": "eA=="},
            clear=True,
        ):
            with patch.object(
                refresh_instagram, "_cookie_jar_from_environment", return_value=self._fake_jar()
            ):
                with patch.object(refresh_instagram.requests, "Session", return_value=session):
                    return extract_with_instagram_api()

    def test_html_login_page_reports_expired_session(self):
        body = (
            b"<html><form id='loginForm' action='/accounts/login/'>"
            b"Log in <input name='username_or_email'/></form></html>"
        )
        response = self._response(content_type="text/html; charset=utf-8", body=body)
        with self.assertRaisesRegex(RuntimeError, "requires login"):
            self._run_extract(response)

    def test_login_redirect_url_reports_expired_session(self):
        response = self._response(
            content_type="text/html",
            url="https://www.instagram.com/accounts/login/?next=/api/v1/feed/user/",
            body=b"<html>login</html>",
        )
        with self.assertRaisesRegex(RuntimeError, "requires login"):
            self._run_extract(response)

    def test_challenge_page_reports_verification(self):
        body = b"<html><h1>checkpoint required</h1><p>unusual activity, verify it was you</p></html>"
        response = self._response(content_type="text/html", body=body)
        with self.assertRaisesRegex(RuntimeError, "[Vv]erification|challenge"):
            self._run_extract(response)

    def test_generic_html_keeps_unexpected_response(self):
        response = self._response(content_type="text/html", body=b"<html><body>hello</body></html>")
        with self.assertRaisesRegex(RuntimeError, "unexpected response"):
            self._run_extract(response)

    def test_empty_body_keeps_unexpected_response(self):
        response = self._response(body=b"")
        with self.assertRaisesRegex(RuntimeError, "unexpected response"):
            self._run_extract(response)

    def test_json_list_keeps_unexpected_response(self):
        response = self._response(body=b"[1,2]", json_data=[1, 2], json_raises=False)
        with self.assertRaisesRegex(RuntimeError, "unexpected response"):
            self._run_extract(response)

    def test_fail_status_reports_rejected_request(self):
        payload = {"status": "fail", "message": "checkpoint_required"}
        response = self._response(body=b"{}", json_data=payload, json_raises=False)
        with self.assertRaisesRegex(RuntimeError, "rejected the request"):
            self._run_extract(response)

    def test_diagnosis_lists_keys_but_never_secrets(self):
        payload = {"items": [], "session_echo": self.SECRET}
        response = self._response(body=b'{"items":[]}', json_data=payload, json_raises=False)
        summary = _safe_response_diagnosis(response)
        self.assertIn("status 200", summary)
        self.assertIn("items", summary)
        self.assertNotIn(self.SECRET, summary)

    def test_error_message_never_contains_body_or_secrets(self):
        body = ("<html>login " + self.SECRET + "</html>").encode("utf-8")
        response = self._response(content_type="text/html", body=body)
        response.headers = {
            "content-type": "text/html",
            "set-cookie": f"sessionid={self.SECRET}; Domain=.instagram.com",
        }
        try:
            self._run_extract(response)
            self.fail("expected RuntimeError")
        except RuntimeError as error:
            self.assertNotIn(self.SECRET, str(error))
            self.assertIn("status 200", str(error))


class _FakeLoginRequired(Exception):
    pass


class _FakeChallengeRequired(Exception):
    pass


class _FakeClientThrottledError(Exception):
    pass


class InstagrapiTests(unittest.TestCase):
    SECRET = "sess-fake-secret-7c2e1a"

    def _photo_media(self, code="Abc123", taken_at=None):
        from datetime import datetime, timezone
        from types import SimpleNamespace

        return SimpleNamespace(
            code=code,
            taken_at=taken_at or datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc),
            media_type=1,
            product_type="feed",
            thumbnail_url="https://cdn.example/a.jpg",
            caption_text="Hello",
            like_count=10,
            comment_count=2,
        )

    def _fake_instagrapi(self, medias=None, login_result=True, login_error=None, medias_error=None):
        import sys
        import types

        calls = {}

        fake_exceptions = types.ModuleType("instagrapi.exceptions")
        fake_exceptions.LoginRequired = _FakeLoginRequired
        fake_exceptions.ClientLoginRequired = _FakeLoginRequired
        fake_exceptions.ChallengeRequired = _FakeChallengeRequired
        fake_exceptions.ClientThrottledError = _FakeClientThrottledError

        class FakeClient:
            def __init__(self, *args, **kwargs):
                calls["init"] = True

            def login_by_sessionid(self, sessionid):
                calls["sessionid"] = sessionid
                if login_error is not None:
                    raise login_error
                return login_result

            def user_medias(self, user_id, amount=0, sleep=0):
                calls["user_id"] = user_id
                calls["amount"] = amount
                if medias_error is not None:
                    raise medias_error
                return list(medias or [])

        fake_module = types.ModuleType("instagrapi")
        fake_module.Client = FakeClient
        fake_module.exceptions = fake_exceptions
        return fake_module, fake_exceptions, calls

    def _fake_jar(self, session_value="sess", domain=".instagram.com"):
        from types import SimpleNamespace

        return [
            SimpleNamespace(name="sessionid", value=session_value, domain=domain),
            SimpleNamespace(name="csrftoken", value="csrf", domain=domain),
        ]

    def _run_with_fake_module(self, fake_module, test_body):
        import sys

        real = sys.modules.get("instagrapi")
        real_exceptions = sys.modules.get("instagrapi.exceptions")
        sys.modules["instagrapi"] = fake_module
        sys.modules["instagrapi.exceptions"] = fake_module.exceptions
        try:
            return test_body()
        finally:
            if real is not None:
                sys.modules["instagrapi"] = real
            else:
                sys.modules.pop("instagrapi", None)
            if real_exceptions is not None:
                sys.modules["instagrapi.exceptions"] = real_exceptions
            else:
                sys.modules.pop("instagrapi.exceptions", None)

    def test_photo_media_maps_to_post(self):
        post = parse_instagrapi_media(self._photo_media())
        self.assertEqual(post["shortcode"], "Abc123")
        self.assertEqual(post["url"], "https://www.instagram.com/p/Abc123/")
        self.assertEqual(post["type"], "post")
        self.assertEqual(post["sourceImage"], "https://cdn.example/a.jpg")
        self.assertEqual(post["likes"], 10)
        self.assertTrue(post["publishedAt"].endswith("Z"))

    def test_clips_media_maps_to_reel(self):
        from types import SimpleNamespace

        base = self._photo_media(code="Reel1")
        base.product_type = "clips"
        base.media_type = 2
        post = parse_instagrapi_media(base)
        self.assertEqual(post["type"], "reel")
        self.assertEqual(post["url"], "https://www.instagram.com/reel/Reel1/")

    def test_media_without_usable_content_skipped(self):
        self.assertIsNone(parse_instagrapi_media(self._photo_media(code="")))
        no_thumb = self._photo_media()
        no_thumb.thumbnail_url = None
        self.assertIsNone(parse_instagrapi_media(no_thumb))
        self.assertIsNone(parse_instagrapi_media(None))

    def test_device_seed_stable_per_user(self):
        first = _instagrapi_device_seed("64565332872")
        second = _instagrapi_device_seed("64565332872")
        self.assertEqual(first, second)
        other = _instagrapi_device_seed("123")
        self.assertNotEqual(first["uuid"], other["uuid"])
        self.assertTrue(first["android_device_id"].startswith("android-"))

    def test_sessionid_prefers_instagram_domain(self):
        from types import SimpleNamespace

        jar = [
            SimpleNamespace(name="sessionid", value="other-site", domain=".example.com"),
            SimpleNamespace(name="sessionid", value="ig-site", domain=".instagram.com"),
        ]
        self.assertEqual(_sessionid_from_jar(jar), "ig-site")

    def test_extract_success_uses_sessionid_and_user_id(self):
        import refresh_instagram

        fake_module, _, calls = self._fake_instagrapi(medias=[self._photo_media()])

        def body():
            with patch.dict(
                "os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True
            ):
                with patch.object(
                    refresh_instagram, "_cookie_jar_from_environment",
                    return_value=self._fake_jar(session_value="sess-ok"),
                ):
                    return extract_with_instagrapi()

        posts = self._run_with_fake_module(fake_module, body)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["shortcode"], "Abc123")
        self.assertEqual(calls["sessionid"], "sess-ok")
        self.assertEqual(calls["user_id"], "64565332872")

    def test_login_required_reports_session_refresh(self):
        import refresh_instagram

        fake_module, fake_exceptions, _ = self._fake_instagrapi(
            login_error=_FakeLoginRequired("login_required")
        )

        def body():
            with patch.dict(
                "os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True
            ):
                with patch.object(
                    refresh_instagram, "_cookie_jar_from_environment",
                    return_value=self._fake_jar(),
                ):
                    with self.assertRaisesRegex(RuntimeError, "rejected the session"):
                        extract_with_instagrapi()

        self._run_with_fake_module(fake_module, body)

    def test_challenge_reports_verification(self):
        import refresh_instagram

        fake_module, fake_exceptions, _ = self._fake_instagrapi(
            medias_error=_FakeChallengeRequired("challenge")
        )

        def body():
            with patch.dict(
                "os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True
            ):
                with patch.object(
                    refresh_instagram, "_cookie_jar_from_environment",
                    return_value=self._fake_jar(),
                ):
                    with self.assertRaisesRegex(RuntimeError, "[Vv]erification|challenge"):
                        extract_with_instagrapi()

        self._run_with_fake_module(fake_module, body)

    def test_missing_library_reports_requirements(self):
        import sys

        import refresh_instagram

        real = sys.modules.get("instagrapi")
        sys.modules["instagrapi"] = None
        try:
            with patch.dict(
                "os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True
            ):
                with self.assertRaisesRegex(RuntimeError, "instagrapi is not installed"):
                    extract_with_instagrapi()
        finally:
            if real is not None:
                sys.modules["instagrapi"] = real
            else:
                sys.modules.pop("instagrapi", None)

    def test_error_never_contains_session_value(self):
        import refresh_instagram

        fake_module, fake_exceptions, _ = self._fake_instagrapi(
            medias_error=_FakeChallengeRequired("challenge")
        )

        def body():
            with patch.dict(
                "os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True
            ):
                with patch.object(
                    refresh_instagram, "_cookie_jar_from_environment",
                    return_value=self._fake_jar(session_value=self.SECRET),
                ):
                    try:
                        extract_with_instagrapi()
                        self.fail("expected RuntimeError")
                    except RuntimeError as error:
                        self.assertNotIn(self.SECRET, str(error))

        self._run_with_fake_module(fake_module, body)


class ApiTests(unittest.TestCase):
    def test_fallback_image_urls_become_absolute(self):
        feed = {"posts": [{"image": "/instagram/post.jpg"}]}
        result = _absolute_fallback_images(feed, "https://example.com")
        self.assertEqual(result["posts"][0]["image"], "https://example.com/instagram/post.jpg")
        self.assertEqual(feed["posts"][0]["image"], "/instagram/post.jpg")

    def test_cron_requires_secret_on_vercel(self):
        with patch.dict("os.environ", {"VERCEL": "1", "CRON_SECRET": "correct"}, clear=True):
            self.assertEqual(cron_authorization_status("Bearer wrong"), (False, "invalid authorization"))
            self.assertEqual(cron_authorization_status("Bearer correct"), (True, "authorized"))

        with patch.dict("os.environ", {"VERCEL": "1"}, clear=True):
            self.assertEqual(
                cron_authorization_status(None),
                (False, "CRON_SECRET is not configured"),
            )


if __name__ == "__main__":
    unittest.main()
