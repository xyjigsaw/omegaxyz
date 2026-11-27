"""Check the published URLs and search metadata before deploying Pages."""
import json
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

from build_site import OUT, SITE_URL


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = self.description = ""
        self.alternates = {}
        self.redirect = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content")
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.redirect = True
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "link" and attrs.get("rel") == "alternate" and attrs.get("hreflang"):
            self.alternates[attrs.get("hreflang")] = attrs.get("href")


def main():
    locations = [e.text for e in ElementTree.parse(OUT / "sitemap.xml").iterfind(".//{*}loc")]
    urls = set(locations)
    assert urls and len(urls) == len(locations), "Empty or duplicated sitemap"
    for url in urls:
        path = urlsplit(url).path
        assert path.startswith(("/en/", "/zh/")) and url == SITE_URL + path, url
        file = OUT / unquote(path.strip("/")) / "index.html"
        head = Head()
        head.feed(file.read_text(encoding="utf-8").partition("</head>")[0])
        assert head.canonical == url and not head.redirect, url
        assert head.description and head.description.strip() != "OmegaXYZ", url
        assert head.alternates == {lang: SITE_URL + "/" + lang + "/" + path[4:] for lang in ("zh", "en")}, url
        assert set(head.alternates.values()) <= urls, url
    for lang in ("zh", "en"):
        rows = json.loads((OUT / lang / "search-index.json").read_text(encoding="utf-8"))
        assert rows, lang
        documents = set()
        for row in rows:
            path = row["url"]
            assert path.startswith(f"/{lang}/") and SITE_URL + path in urls, path
            if row.get("markdown"):
                assert row["markdown"] == path + "index.md"
                folder = OUT / unquote(path.strip("/"))
                md = (folder / "index.md").read_text(encoding="utf-8")
                assert md.startswith("# ") and f"<{SITE_URL}{path}>" in md
                page = (folder / "index.html").read_text(encoding="utf-8")
                assert page.count("data-md-copy") == 2 and 'type="text/markdown" href="index.md"' in page, path
                documents.add(SITE_URL + path)
        rss = ElementTree.parse(OUT / lang / "rss.xml")
        atom = ElementTree.parse(OUT / lang / "atom.xml")
        guids = [node.text for node in rss.findall("./channel/item/guid")]
        ids = [node.text for node in atom.findall("./{*}entry/{*}id")]
        assert guids == ids and len(set(ids)) == len(ids) == min(50, len(documents))
        assert set(ids) <= documents
        graph_dir = OUT / lang / "article-graph"
        graph_file, = graph_dir.glob("graph-*.json")
        assert graph_file.name in (graph_dir / "index.html").read_text(encoding="utf-8")
        graph = json.loads(graph_file.read_text(encoding="utf-8"))
        nodes, terms = graph["nodes"], graph["terms"]
        expected = {row["url"] for row in rows if row["kind"] == "post"}
        assert len(nodes) == len(expected) and {n["url"] for n in nodes} == expected
        counts = [0] * len(terms)
        for i, n in enumerate(nodes):
            for t in set(n["terms"]):
                counts[t] += 1
            assert len(n["near"]) <= 5 and i not in n["near"]
            assert all(set(n["terms"]).intersection(nodes[j]["terms"]) for j in n["near"])
        assert counts == [t["count"] for t in terms], "Graph topic counts do not match posts"
    robots = RobotFileParser()
    robots.parse((OUT / "robots.txt").read_text(encoding="utf-8").splitlines())
    assert robots.can_fetch("Baiduspider", "/zh/") and robots.can_fetch("Googlebot", "/en/")
    assert not robots.can_fetch("GPTBot", "/zh/")
    assert SITE_URL + "/sitemap.xml" in (robots.site_maps() or [])
    print(f"Verified {len(urls)} canonical pages, bilingual search indexes and origin robots.txt")


if __name__ == "__main__":
    main()
