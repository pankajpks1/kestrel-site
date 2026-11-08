#!/usr/bin/env python3
"""Build the help docs: tools/docs/<page>.html → docs/<page>/index.html, plus docs/index.html.

Each source file starts with two comment lines, then the page body:
    <!-- title: Segment limits -->
    <!-- summary: Why a table stops at 3,000 rows, and how to see the rest. -->
Run from anywhere:  python3 tools/build_docs.py
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "docs"
OUT = ROOT / "docs"

# The sidebar, in reading order: (group, [page, …]).
NAV = [
    ("Reports", ["measurements", "segment-limits", "custom-buckets", "list-properties"]),
    ("Data", ["lexicon", "custom-events", "custom-properties", "saved-metrics", "lookup-tables", "cohorts"]),
    ("Boards", ["board-templates", "value-moment", "public-boards"]),
    ("Project settings", ["project-settings", "sessions"]),
]

BIRD = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true"><path d="M16 7h.01"/><path d="M3.4 18H12a8 8 0 0 0 8-8V7a4 4 '
    '0 0 0-7.28-2.3L2 20"/><path d="m20 7 2 .5-2 .5"/><path d="M10 18v3"/><path d="M14 17.75V21"/><path d="M7 '
    '18a6 6 0 0 0 3.84-10.61"/></svg>'
)


def read(page: str) -> tuple[str, str, str]:
    text = (SRC / f"{page}.html").read_text()
    title = re.search(r"<!-- title: (.+?) -->", text).group(1)
    summary = re.search(r"<!-- summary: (.+?) -->", text).group(1)
    body = re.sub(r"^\s*<!-- (title|summary): .+? -->\n", "", text, flags=re.M).strip()
    return title, summary, body


def layout(title: str, summary: str, body: str, current: str | None) -> str:
    nav = []
    for group, pages in NAV:
        items = "".join(
            f'<li><a href="/docs/{p}/"{' aria-current="page"' if p == current else ""}>{html.escape(read(p)[0])}</a></li>'
            for p in pages
        )
        nav.append(f"<h4>{html.escape(group)}</h4><ul>{items}</ul>")
    page_title = "Kestrel Help Docs" if current is None else f"{title} — Kestrel Help Docs"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(summary)}">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header>
    <div class="wrap wide">
      <a class="brand" href="/">{BIRD} Kestrel</a>
      <nav><a href="/docs/">Help Docs</a><a href="mailto:pankaj@rivero.co.in">Contact</a></nav>
    </div>
  </header>
  <main>
    <div class="wrap wide docs">
      <aside>{"".join(nav)}</aside>
      <article>
        <h1>{html.escape(title)}</h1>
        <p class="lead">{html.escape(summary)}</p>
{body}
      </article>
    </div>
  </main>
  <footer>
    <div class="wrap wide">
      <a href="https://rivero.co.in/privacy/">Privacy Policy</a><a href="https://rivero.co.in/terms/">Terms of Service</a>
      <p>Kestrel is a product of <a href="https://rivero.co.in/">Rivero</a>. © 2026 Rivero</p>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    pages = [p for _, ps in NAV for p in ps]
    on_disk = sorted(f.stem for f in SRC.glob("*.html"))
    assert sorted(pages) == on_disk, f"NAV and tools/docs differ: {sorted(set(pages) ^ set(on_disk))}"
    for p in pages:
        title, summary, body = read(p)
        out = OUT / p / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(title, summary, body, p))
    cards = "".join(
        f'<h2>{html.escape(group)}</h2><ul class="toc">'
        + "".join(f'<li><a href="/docs/{p}/">{html.escape(read(p)[0])}</a> — {html.escape(read(p)[1])}</li>' for p in ps)
        + "</ul>"
        for group, ps in NAV
    )
    (OUT / "index.html").write_text(
        layout("Help Docs", "How Kestrel's reports, data tools, boards and settings work.", cards, None)
    )
    print(f"built {len(pages)} pages + index")


if __name__ == "__main__":
    main()
