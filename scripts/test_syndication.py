"""Content-only exports and stable feed identity across publishing cycles."""
import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET
from urllib.parse import urljoin

import build_site as site
import syndication as s


class Syndication(unittest.TestCase):
    def test_legacy_body(self):
        body = s.markdown_body(r'''First paragraph

Second paragraph with \(x_{ij}\).
<table><tr><th>A</th></tr><tr><td>Data</td></tr></table>
<img alt="Plot" src="../../pic.png"><a href="?t=x&amp;n=2#eq">Equation</a>
<pre lang="python">code = "```"<br/>print(code)</pre>
<img class="ql-img-inline-formula" alt="\frac{a_b}{c}" src="old.svg">
<script>trackingSecret()</script><p class="post-footer">Site footer</p>''', "https://site.test/zh/post/")
        for piece in ("First paragraph\n\nSecond", r"\(x_{ij}\)", "![Plot](https://site.test/pic.png)",
                      "https://site.test/zh/post/?t=x&n=2#eq", '| Data |', 'Code'.lower() + ' = "```"\nprint(code)',
                      "````python", r"$\frac{a_b}{c}$"):
            self.assertIn(piece, body)
        self.assertNotIn("trackingSecret", body)
        self.assertNotIn("Site footer", body)

    def test_native_format(self):
        src = '## H\n\n$E_{i}$ and [read](other/)\n\n`[example](other/)`\n\n~~~js\n[demo](other/)\n~~~'
        body = s.authored_markdown(src, lambda v: urljoin("https://site.test/a/", v))
        self.assertEqual(body, src.replace("[read](other/)", "[read](https://site.test/a/other/)"))

    def test_publishing_lifecycle(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            posts = root / "posts"
            posts.mkdir()
            db = root / "source.json"
            db.write_text('{"entries":[]}')
            primary = posts / "new.md"
            primary.write_text("---\ntitle: 标题\ntitle_en: English\ndate: 2020-01-01\n---\nZH body")
            english = posts / "new.en.md"
            english.write_text("Original EN")
            with patch.multiple(site, ROOT=root, POSTS_DIR=posts, DATA=db, EXTRA_ENTRIES=root/"extra.json", OUT=root/"docs"), \
                    patch.object(site, "fetch_giscus_comment_counts", return_value={}), patch.dict(site.os.environ, WRITE_FEED_STATE="1"):
                def build():
                    site.main()
                    return json.loads((root/"data/feed-state.json").read_text())
                first = build()
                self.assertEqual(build(), first)
                english.write_text("Updated EN")
                (posts/"policy.md").write_text("---\ntitle: Policy\ndate: 2018-02-02\ntype: page\nurl: my-page/\n---\nPage body")
                second = build()
                self.assertEqual(first["zh/2020/01/01/new/"], second["zh/2020/01/01/new/"])
                self.assertLess(first["en/2020/01/01/new/"][1], second["en/2020/01/01/new/"][1])
                self.assertGreater(second["zh/my-page/"][1], first["zh/2020/01/01/new/"][1])
                for lang in ("zh", "en"):
                    folder = root/"docs"/lang
                    self.assertTrue((folder/"my-page/index.md").is_file())
                    self.assertIn("Updated EN" if lang == "en" else "ZH body", (folder/"2020/01/01/new/index.md").read_text())
                    links = [e.text for e in ET.parse(folder/"rss.xml").findall("./channel/item/link")]
                    ids = [e.text for e in ET.parse(folder/"atom.xml").findall("./{*}entry/{*}id")]
                    self.assertEqual(links, ids)
                    self.assertEqual(len(set(ids)), 2)
                with patch.object(site, "fetch_giscus_comment_counts", return_value={"my-page/": 99}):
                    self.assertEqual(build(), second)
                (posts/"policy.md").unlink()
                self.assertNotIn("zh/my-page/", build())
                self.assertFalse((root/"docs/zh/my-page/index.md").exists())


if __name__ == "__main__":
    unittest.main()
