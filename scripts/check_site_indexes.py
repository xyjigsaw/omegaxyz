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
        if tag == "link" and attrs.get("rel") == "alternate":
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
        for row in rows:
            path = row["url"]
            assert path.startswith(f"/{lang}/") and SITE_URL + path in urls, path
    robots = RobotFileParser()
    robots.parse((OUT / "robots.txt").read_text(encoding="utf-8").splitlines())
    assert robots.can_fetch("Baiduspider", "/zh/") and robots.can_fetch("Googlebot", "/en/")
    assert not robots.can_fetch("GPTBot", "/zh/")
    assert SITE_URL + "/sitemap.xml" in (robots.site_maps() or [])
    print(f"Verified {len(urls)} canonical pages, bilingual search indexes and origin robots.txt")


if __name__ == "__main__":
    main()
