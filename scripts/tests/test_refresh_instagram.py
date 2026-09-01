import sys
import unittest
from unittest.mock import patch
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.instagram import _absolute_fallback_images  # noqa: E402
from api.instagram_cron import cron_authorization_status  # noqa: E402
from refresh_instagram import parse_gallery_payload, publish_feed_to_blob  # noqa: E402


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
