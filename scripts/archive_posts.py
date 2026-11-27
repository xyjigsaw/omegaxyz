"""Archive incoming Markdown only when every destination is available."""
import os
from pathlib import Path


def is_post(path):
    return path.name.lower() not in {"example.md", "readme.md"} and not path.name.endswith(".en.md")


def archive_plan(posts):
    archive = posts / "archive"
    moves = []

    def add_if_present(src):
        dst = archive / src.name
        if dst.exists() or dst.is_symlink():
            raise ValueError(f"{dst} already exists; edit the archived file or choose a new filename")
        if src.is_file():
            moves.append((src, dst))

    for main in sorted(posts.glob("*.md")):
        if not is_post(main):
            continue
        add_if_present(main)
        # An old translation would otherwise attach itself to the new draft.
        add_if_present(main.with_suffix(".en.md"))
    for en in sorted(posts.glob("*.en.md")):
        main = en.with_name(en.name.removesuffix(".en.md") + ".md")
        if is_post(main) and not main.exists():
            if not (archive / main.name).is_file():
                raise ValueError(f"{en}: no matching primary manuscript {main.name}")
            add_if_present(en)
    return moves


def archive_posts(posts):
    moves = archive_plan(posts)
    if moves:
        (posts / "archive").mkdir(exist_ok=True)
    for src, dst in moves:
        os.link(src, dst)  # Atomic no-replace on the runner's checkout.
        src.unlink()


if __name__ == "__main__":
    archive_posts(Path(__file__).resolve().parents[1] / "content/posts")
