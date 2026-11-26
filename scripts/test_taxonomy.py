"""Exercise the publication path without touching the real site or fetching data."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock

import build_site as site


class Attributes(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append(dict(attrs))

    def values(self, name):
        return [a[name] for a in self.nodes if name in a]


class PublishedTaxonomy(TestCase):
    def test_new_reused_renamed_and_retired_categories(self):
        with TemporaryDirectory() as tmp, mock.patch.object(site, "OUT", Path(tmp) / "docs"):
            def article(slug, day, cats, tags="", kind="post"):
                path = Path(tmp) / (slug + ".md")
                path.write_text(f"---\ntitle: {slug}\ndate: 2026-11-{day:02d}\n"
                                f"type: {kind}\ncategories: [{cats}]\ntags: [{tags}]\n---\nA note.")
                return site.markdown_file_to_entry(path)

            old = article("original", 1, "计算|compute|Computing")
            new = article("first", 2, "新方向|new-field|New Research, compute, new-field",
                          "同名标签|new-field|Separate Tag")
            again = article("second", 3, "new-field, 计算方法|compute|Computing Methods")
            page = article("info", 4, "page-only", kind="page")

            def check(entries, expected):
                entries = deepcopy(entries)
                site.normalize_taxonomy(entries)
                data = {"entries": entries, "summary": site.build_summary(entries)}
                self.assertEqual(data["summary"]["posts"], len(entries) - 1)
                for lang in ("zh", "en"):
                    home = Attributes(site.render_home(data, lang))
                    self.assertEqual(home.values("data-peaks"), [",".join(
                        map(str, sorted(expected.values(), reverse=True)))])
                    self.assertEqual(len(home.values("data-topic-item")), len(expected))
                    site.render_terms(data, lang)
                    site.render_archive(data, lang)
                    catalog = Attributes(site.path_to_file(f"{lang}/categories/").read_text())

                    peaks = [(a["data-peak"], int(a["data-count"])) for a in catalog.nodes if "data-peak" in a]
                    self.assertCountEqual(peaks, expected.items())
                    archive = Attributes(site.path_to_file(f"{lang}/archive/").read_text())
                    filters = [a["data-archive-term"] for a in archive.nodes if a.get("data-archive-kind") == "category"]
                    self.assertCountEqual(filters, expected)
                    for slug, count in expected.items():
                        listing = site.path_to_file(site.term_path("category", slug, lang)).read_text()
                        self.assertEqual(len(Attributes(listing).values("data-archive-item")), count)
                    self.assertTrue(site.path_to_file(site.term_path("category", "page-only", lang)).is_file())

            check([old, page], {"compute": 1})
            check([old, new, again, page], {"compute": 3, "new-field": 2})
            for lang, labels in (("zh", ("计算方法", "新方向", "同名标签")),
                                 ("en", ("Computing Methods", "New Research", "Separate Tag"))):
                for (kind, slug), label in zip((("category", "compute"), ("category", "new-field"),
                                                ("tag", "new-field")), labels):
                    self.assertIn(f"<h1>{label}</h1>", site.path_to_file(site.term_path(kind, slug, lang)).read_text())
            check([old, page], {"compute": 1})
            many = [f"field-{i:02}" for i in range(33)]
            check([article("wide", 5, ", ".join(many)), page], dict.fromkeys(many, 1))


if __name__ == "__main__":
    main()
