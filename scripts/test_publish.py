"""Regression checks for preparing and publishing bilingual drafts."""
import io
import json
import unittest
from contextlib import ExitStack, redirect_stdout
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import build_site as site
from archive_posts import archive_posts


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.append(dict(attrs).get("href"))


class Publishing(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.root = Path(stack.enter_context(TemporaryDirectory()))
        self.posts = self.root / "content/posts"
        self.posts.mkdir(parents=True)
        self.out = self.root / "docs"
        for name, value in {"ROOT": self.root, "POSTS_DIR": self.posts, "OUT": self.out,
                            "EXTRA_ENTRIES": self.root / "extra.json", "DATA": self.root / "site.json"}.items():
            stack.enter_context(patch.object(site, name, value))
        stack.enter_context(patch.object(site, "fetch_giscus_comment_counts", return_value={}))
        stack.enter_context(redirect_stdout(io.StringIO()))
        site.DATA.write_text('{"entries":[]}')

    def draft(self, name, body):
        p = self.posts / name
        p.parent.mkdir(exist_ok=True)
        p.write_text(body, encoding="utf-8")
        return p

    def test_invalid_primary_leaves_last_build_in_place(self):
        self.out.mkdir()
        stamp = self.out / "index.html"
        stamp.write_text("previous site")
        for filename in ("new.md", "archive/old.md"):
            for header, field in (("date: 2026-01-01", "title"), ("title: Post", "date"),
                                  ('title: "  "\ndate: 2026-01-01', "title"),
                                  ("title: Post\ndate: # required", "date"),
                                  ("title: Post\ndate: 2026-02-30", "date")):
                with self.subTest(filename=filename, field=field):
                    p = self.draft(filename, f"---\n{header}\n---\nbody")
                    with self.assertRaisesRegex(ValueError, f"{p.name}: .*{field}"):
                        site.main()
                    self.assertEqual(stamp.read_text(), "previous site")
                    p.unlink()
        site.EXTRA_ENTRIES.write_text(json.dumps([{"title_zh": "Title", "date": ""}]))
        with self.assertRaisesRegex(ValueError, "extra.json.*date"):
            site.main()
        self.assertEqual(stamp.read_text(), "previous site")

    def test_archive_batch_rejects_either_collision_before_moving_anything(self):
        self.draft("a-first.md", "intact")
        self.draft("z-last.md", "incoming")
        for name in ("z-last.md", "z-last.en.md"):
            dst = self.draft("archive/" + name, "original")
            with self.assertRaisesRegex(ValueError, name):
                site.load_markdown_entries()
            with self.assertRaisesRegex(ValueError, name):
                archive_posts(self.posts)
            self.assertEqual(dst.read_text(), "original")
            self.assertEqual((self.posts / "z-last.md").read_text(), "incoming")
            self.assertEqual((self.posts / "a-first.md").read_text(), "intact")
            self.assertFalse((self.posts / "archive/a-first.md").exists())
            dst.unlink()

    def test_local_links_and_bilingual_archive_round_trip(self):
        urls = ["/zh/policy/", "/en/policy/index.html?one=1&two=2#privacy",
                "https://omegaxyz.com/zh/policy/index.html", "#privacy", "?a=1&b=2",
                "/not-a-published-page/", "/assets/site.css", "https://example.org/x"]
        links = "\n\n".join(f"[Link]({url})" for url in urls)
        self.draft("post.md", "---\ntitle_zh: Article\ndate: 2026-01-01\n---\n" + links)
        self.draft("post.en.md", "Translation\n\n" + links)
        self.draft("policy.md", "---\ntitle: Policy\ndate: 2026-01-01\ntype: page\nurl: policy/\n---\nPolicy body")
        self.draft("example.md", "template")
        self.draft("README.md", "instructions")
        site.main()
        def pages():
            result = []
            for lang in ("zh", "en"):
                page = self.out / lang / "2026/01/01/post/index.html"
                result.append(page.read_bytes())
                a = Links()
                a.feed(result[-1].decode())
                for url in urls:
                    self.assertIn(url, a.hrefs)
                translation = "Translation" in result[-1].decode()
                self.assertEqual(translation, lang == "en")
                self.assertIn("Policy body", (self.out / lang / "policy/index.html").read_text())
                self.assertFalse((self.out / "not-a-published-page").exists())
                self.assertTrue((self.out / "assets/site.css").is_file())
            return result
        before = pages()
        archive_posts(self.posts)
        self.assertEqual({p.name for p in self.posts.glob("*.md")}, {"example.md", "README.md"})
        self.assertEqual({p.name for p in (self.posts / "archive").iterdir()}, {"post.md", "post.en.md", "policy.md"})
        site.main()
        self.assertEqual(pages(), before)

    def test_later_translation_cannot_overwrite_existing_translation(self):
        self.draft("archive/article.md", "---\ntitle: Test\ndate: 2026-01-01\n---\nOriginal")
        self.draft("article.en.md", "First translation")
        self.assertIn("First translation", site.load_markdown_entries()[0]["content_en"])
        archive_posts(self.posts)
        self.draft("article.en.md", "Duplicate")
        with self.assertRaisesRegex(ValueError, "article.en.md already exists"):
            archive_posts(self.posts)
        self.assertEqual((self.posts / "archive/article.en.md").read_text(), "First translation")

    def test_explicit_redirect_cannot_replace_a_real_page(self):
        page = self.out / "zh/policy/index.html"
        page.parent.mkdir(parents=True)
        page.write_text("existing policy")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            site.render_redirect("zh/policy/", "zh/search/")
        self.assertEqual(page.read_text(), "existing policy")
        for _ in range(2):
            site.render_redirect("old-policy/", "zh/policy/")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            site.render_redirect("old-policy/", "en/policy/")

    def test_known_wordpress_links_still_migrate(self):
        current = self.out / "en/article/index.html"
        mapping = {"old/": {"zh": "zh/old/", "en": "en/old/"}}
        self.assertEqual(site.rewrite_url("/old/?sort=date#comment-19", "en", current, mapping),
                         "../old/index.html?sort=date#comment-19")
        self.assertEqual(site.rewrite_url("/wp-content/uploads/2017/a.jpg?w=42", "en", current, mapping),
                         site.CDN + "/2017/a.jpg?w=42")


if __name__ == "__main__":
    unittest.main()
