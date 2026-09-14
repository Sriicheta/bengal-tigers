import sys
import unittest
from unittest.mock import patch
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.instagram import _absolute_fallback_images  # noqa: E402
from api.instagram_cron import cron_authorization_status  # noqa: E402
from refresh_instagram import (  # noqa: E402
    POSTS_URL,
    extract_posts,
    extract_with_gallery_dl,
    extract_with_instagram_api,
    instagram_target_url,
    instagram_user_id,
    parse_gallery_payload,
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

    def test_extract_posts_routes_to_api_when_id_set(self):
        import refresh_instagram

        sentinel = [{"id": "x"}]
        with patch.dict("os.environ", {"INSTAGRAM_USER_ID": "64565332872"}, clear=True):
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
