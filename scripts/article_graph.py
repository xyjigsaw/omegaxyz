"""Build a language-independent article graph from normalized taxonomy."""
from collections import Counter, defaultdict
from datetime import date


def build_graph(entries):
    posts = sorted((e for e in entries if e["type"] == "post"),
                   key=lambda e: (e["date"], e["url"]), reverse=True)
    terms, members, keys = {}, defaultdict(list), []
    for i, post in enumerate(posts):
        assigned = set()
        for kind in ("categories", "tags"):
            for term in post.get(kind, []):
                key = (kind, term["slug"])
                terms[key] = term
                assigned.add(key)
        keys.append(sorted(assigned))
        for key in assigned:
            members[key].append(i)
    ordered = sorted(terms)
    ids = {key: i for i, key in enumerate(ordered)}
    dates = [date.fromisoformat(p["date"][:10]).toordinal() for p in posts]
    nodes = []
    for i, assigned in enumerate(keys):
        scores = Counter()
        for key in assigned:
            weight = 1 / len(members[key])
            for j in members[key]:
                if i != j:
                    scores[j] += weight
        # Equal overlap is common in long-running series. Prefer a nearby
        # publication date rather than connecting every note to the newest one.
        near = sorted(scores, key=lambda j: (-scores[j], abs(dates[i]-dates[j]), j))[:5]
        nodes.append({"terms": [ids[k] for k in sorted(assigned, key=lambda k: (len(members[k]), k))],
                      "near": near})
    return posts, [(k[0], terms[k], len(members[k])) for k in ordered], nodes
