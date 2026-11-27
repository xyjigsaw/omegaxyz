import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import build_site
from article_graph import build_graph


class GraphTest(unittest.TestCase):
    def test_new_category_and_rare_terms(self):
        def post(slug, day, cats, tags=()):
            return dict(type="post", url=slug + "/", date=f"2027-01-{day:02}",
                        categories=[{"slug": c} for c in cats], tags=[{"slug": t} for t in tags])
        old = [post("a", 1, ["common"], ["rare"]), post("b", 2, ["common"]),
               post("c", 3, ["common"]), post("alone", 4, [])]
        future = post("new", 5, ["new-category", "common"], ["rare", "rare"])
        posts, terms, nodes = build_graph(old + [future, {"type": "page"}])
        ids = {p["url"]: i for i, p in enumerate(posts)}
        self.assertEqual(len(posts), 5)
        self.assertEqual(nodes[ids["alone/"]]["near"], [])
        self.assertEqual(nodes[ids["a/"]]["near"][0], ids["new/"])
        self.assertEqual(nodes[ids["new/"]]["near"][0], ids["a/"])
        self.assertIn(("categories", {"slug": "new-category"}, 1), terms)
        self.assertIn(("tags", {"slug": "rare"}, 2), terms)
        self.assertEqual(build_graph(old + [future]), build_graph([future] + old[::-1]))

    def test_new_year_and_category_generate_both_languages(self):
        def entry(year, slug):
            t = {"slug": slug, "name": slug, "name_en": slug.upper()}
            return dict(type="post", url=f"{year}/note/", date=f"{year}-02-10",
                        categories=[t], tags=[], comments=[], title_en=slug, title_zh=slug,
                        excerpt_zh="", excerpt_en="")
        with TemporaryDirectory() as folder, patch.object(build_site, "OUT", Path(folder)):
            site = {"entries": [entry(2025, "old"), entry(2028, "new")]}
            for lang in ("zh", "en"):
                build_site.render_terms(site, lang)
                page = (Path(folder) / lang / "categories" / "index.html").read_text()
                self.assertIn('min="2025" max="2028" step="1" value="2028"', page)
                self.assertIn('data-peak="new" data-count="1" data-years="2028:1"', page)
                self.assertTrue((Path(folder) / lang / "category/new/index.html").is_file())


if __name__ == "__main__":
    unittest.main()
