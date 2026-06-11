# Talks Feed Implementation Plan (Phase 1, website repo)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `data/talks.toml` the single source of truth that generates both the speaking timeline in `index.html` and a stable RSS 2.0 feed at `feeds/talks.xml`, with CI drift protection.

**Architecture:** A zero-dependency Python script reads TOML, validates it, and deterministically renders two committed artifacts, the feed XML and the timeline markup between HTML markers. Deploy workflows stay untouched because artifacts are committed. A new CI workflow runs the script in `--check` mode.

**Tech Stack:** Python 3.11+ standard library only (`tomllib`, `xml.etree`, `html`, `email.utils`, `difflib`). GitHub Actions for the check.

Spec. `docs/superpowers/specs/2026-06-11-talks-feed-design.md`. Work happens on the `talks-feed` branch, which already carries the spec.

**Sequencing principle.** Task 1 seeds the TOML with exactly the eight entries on the page today (current titles, current venues, research-verified dates) so Task 3 can prove the generator reproduces the existing page. Content upgrades and the eighteen new entries land in Task 6, after the machinery is proven.

---

### Task 1: Seed data/talks.toml with the current eight page entries

**Files:**
- Create: `data/talks.toml`

- [ ] **Step 1: Create the file with exactly this content**

```toml
# Source of truth for the speaking timeline and the talks RSS feed.
# Edit this file, run scripts/build_feeds.py, commit the results.
#
# Required fields. slug, title, venue, date, kind, url.
#   slug   permanent feed identity, never edit after a talk ships in the feed
#   kind   one of keynote, talk, panel, podcast (talk renders the Video badge)
#   date   native TOML date (no quotes)
# Exactly one preview style per entry.
#   youtube = "VIDEOID"                      YouTube thumbnail preview
#   image = "https://..."                    image preview (optional image_alt)
#   brand_text = "..." + brand_color = "#x"  colored box preview

[[talk]]
slug = "2025-11-missing-manual"
title = "The Missing Manual for Open Source Community Sustainability"
venue = "KubeCon + CloudNativeCon North America, Atlanta"
date = 2025-11-11
kind = "talk"
url = "https://youtu.be/FPQB7hQL4Vw"
youtube = "FPQB7hQL4Vw"

[[talk]]
slug = "2024-11-above-the-clouds"
title = "Above the Clouds. Mountainous Achievements with End Users"
venue = "KubeCon + CloudNativeCon North America, Salt Lake City"
date = 2024-11-14
kind = "keynote"
url = "https://www.youtube.com/watch?v=TnYupUh6OIg"
youtube = "TnYupUh6OIg"

[[talk]]
slug = "2024-09-pytorch-cognition"
title = "PyTorch Conference 2024"
venue = "PyTorch Conference, San Francisco"
date = 2024-09-18
kind = "keynote"
url = "https://www.youtube.com/watch?v=MWmOeXI17Kg"
youtube = "MWmOeXI17Kg"

[[talk]]
slug = "2023-11-windy-city-whirlwind"
title = "Windy City Whirlwind. Stirring Up the Cloud Native Ecosystem"
venue = "KubeCon + CloudNativeCon North America, Chicago"
date = 2023-11-07
kind = "keynote"
url = "https://www.youtube.com/watch?v=6mwuXLxwYTg"
youtube = "6mwuXLxwYTg"

[[talk]]
slug = "2023-11-blueprint-banter"
title = "Blueprint Banter. Cloud Native Conversations by the Fireside"
venue = "KubeCon + CloudNativeCon North America, Chicago"
date = 2023-11-07
kind = "panel"
url = "https://youtu.be/yVyMveT6RCA"
youtube = "yVyMveT6RCA"

[[talk]]
slug = "2022-09-ship-it-69"
title = "The Cloud Native Ecosystem"
venue = "Ship It! Podcast, Episode 69"
date = 2022-09-08
kind = "podcast"
url = "https://changelog.com/shipit/69"
image = "https://cdn.changelog.com/uploads/covers/ship-it-original.png"
image_alt = "Ship It! Podcast"

[[talk]]
slug = "2021-02-fosdem-governance"
title = "Layered Governance for Infrastructure with Kubernetes, OPA, and Terraform"
venue = "FOSDEM 2021"
date = 2021-02-06
kind = "talk"
url = "https://archive.fosdem.org/2021/schedule/event/kubernetes_layered_governance/"
brand_text = "FOSDEM '21"
brand_color = "#4a286a"

[[talk]]
slug = "2020-08-kubernetes-podcast-118"
title = "Kubernetes 1.19 Release"
venue = "Kubernetes Podcast from Google, Episode 118"
date = 2020-08-25
kind = "podcast"
url = "https://kubernetespodcast.com/episode/118-kubernetes-1.19/"
brand_text = "Kubernetes Podcast"
brand_color = "#326ce5"
```

Note the Blueprint Banter entry was a panel on the page already and the 2023 page order (Windy City above Blueprint Banter) is preserved by the slug tiebreak (`w` sorts after `b` descending). Dates come from the 2026-06-11 research pass (sched.com, changelog.com, FOSDEM archive, kubernetespodcast.com). The PyTorch title stays at the page's current generic label until Task 6 so Task 3 can diff cleanly.

That is eight entries, matching the page today. The KubeFM entry and all researched additions arrive in Task 6.

- [ ] **Step 2: Verify the TOML parses**

Run: `python3 -c "import tomllib,pathlib; d=tomllib.loads(pathlib.Path('data/talks.toml').read_text()); print(len(d['talk']))"`
Expected: `8`
If the local python3 is older than 3.11 use `python3.12` or `uv run python` for every python invocation in this plan.

- [ ] **Step 3: Commit**

```bash
git add data/talks.toml
git commit -m "Add talks data file seeded from the current timeline"
```

---

### Task 2: Create scripts/build_feeds.py

**Files:**
- Create: `scripts/build_feeds.py`

- [ ] **Step 1: Create the script with exactly this content**

```python
#!/usr/bin/env python3
"""Generate RSS feeds and the speaking timeline from data/*.toml.

data/talks.toml is the single source of truth. Outputs are committed:
feeds/talks.xml and the markup between <!-- talks:start --> and
<!-- talks:end --> in index.html. Run with no arguments to regenerate,
or with --check to verify the committed output matches the data (CI).

Output is deterministic. Same data in, byte-identical files out.

Adding a feed later: add a TOML file under data/, append a Feed to
FEEDS, and (only if it needs a page section) add a renderer.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):  # tomllib arrived in 3.11
    sys.exit("scripts/build_feeds.py requires Python 3.11+")

import argparse
import difflib
import html
import tomllib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE = "https://onlydole.dev"
KINDS = ("keynote", "talk", "panel", "podcast")
BADGES = {"keynote": "Keynote", "talk": "Video", "panel": "Panel", "podcast": "Podcast"}
TALKS_START = "<!-- talks:start -->"
TALKS_END = "<!-- talks:end -->"

PLAY_VIDEO = (
    '<svg viewBox="0 0 68 48" aria-hidden="true"><path d="M66.52,7.74c-0.78-2.93'
    "-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55C3.97,2.33,2.27,"
    "4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5."
    "41,5.42,6.19C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3."
    '26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z" fill="#212121"'
    ' fill-opacity="0.8"/><path d="M 45,24 27,14 27,34" fill="#fff"/></svg>'
)
PLAY_AUDIO = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 '
    '4-1.79 4-4V7h4V3h-6z"/></svg>'
)


class DataError(Exception):
    """The data file or page markers are invalid."""


@dataclass(frozen=True)
class Feed:
    name: str
    data: str
    out: str
    title: str
    description: str
    page_link: str


FEEDS = [
    Feed(
        name="talks",
        data="data/talks.toml",
        out="feeds/talks.xml",
        title="Taylor Dolezal · Talks",
        description=(
            "Talks, keynotes, panels, and podcast appearances by Taylor Dolezal."
        ),
        page_link=f"{SITE}/#speaking",
    ),
]


def load_talks(path: Path) -> list[dict]:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise DataError(f"{path.name}: {exc}") from exc
    entries = raw.get("talk")
    if not isinstance(entries, list) or not entries:
        raise DataError(f"{path.name} must contain at least one [[talk]] table")
    slugs: set[str] = set()
    for entry in entries:
        slug = entry.get("slug") or "?"
        for field in ("slug", "title", "venue", "date", "kind", "url"):
            if not entry.get(field):
                raise DataError(f"talk {slug!r} is missing {field!r}")
        if not isinstance(entry["date"], date) or isinstance(entry["date"], datetime):
            raise DataError(f"talk {slug!r} date must be a bare TOML date")
        if entry["kind"] not in KINDS:
            raise DataError(f"talk {slug!r} kind must be one of {', '.join(KINDS)}")
        if entry["slug"] in slugs:
            raise DataError(f"duplicate slug {slug!r}")
        slugs.add(entry["slug"])
        previews = [k for k in ("youtube", "image", "brand_text") if entry.get(k)]
        if len(previews) != 1:
            raise DataError(
                f"talk {slug!r} needs exactly one preview style "
                f"(youtube, image, or brand_text), found {previews or 'none'}"
            )
        if entry.get("brand_text") and not entry.get("brand_color"):
            raise DataError(f"talk {slug!r} has brand_text but no brand_color")
    entries.sort(key=lambda e: (e["date"].isoformat(), e["slug"]), reverse=True)
    return entries


def rfc822(d: date) -> str:
    """Noon UTC keeps the displayed date correct in nearly every timezone."""
    return format_datetime(datetime(d.year, d.month, d.day, 12, tzinfo=timezone.utc))


def render_feed(entries: list[dict], feed: Feed) -> str:
    rss = ElementTree.Element(
        "rss", {"version": "2.0", "xmlns:atom": "http://www.w3.org/2005/Atom"}
    )
    channel = ElementTree.SubElement(rss, "channel")
    ElementTree.SubElement(channel, "title").text = feed.title
    ElementTree.SubElement(channel, "link").text = feed.page_link
    ElementTree.SubElement(channel, "description").text = feed.description
    ElementTree.SubElement(
        channel,
        "atom:link",
        {"href": f"{SITE}/{feed.out}", "rel": "self", "type": "application/rss+xml"},
    )
    ElementTree.SubElement(channel, "language").text = "en-us"
    ElementTree.SubElement(channel, "lastBuildDate").text = rfc822(entries[0]["date"])
    for entry in entries:
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = entry["title"]
        ElementTree.SubElement(item, "link").text = entry["url"]
        ElementTree.SubElement(item, "description").text = entry["venue"]
        ElementTree.SubElement(item, "category").text = entry["kind"]
        ElementTree.SubElement(item, "pubDate").text = rfc822(entry["date"])
        guid = ElementTree.SubElement(item, "guid", {"isPermaLink": "false"})
        guid.text = f"{SITE}/talks/{entry['slug']}"
    ElementTree.indent(rss)
    body = ElementTree.tostring(rss, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{body}\n'


def _alt(entry: dict) -> str:
    return entry.get("image_alt") or f"{entry['title']}, {entry['venue']}"


def _preview_lines(entry: dict) -> list[str]:
    url = html.escape(entry["url"], quote=True)
    audio = entry["kind"] == "podcast"
    icon = PLAY_AUDIO if audio else PLAY_VIDEO
    icon_class = "play-icon play-icon-audio" if audio else "play-icon"
    if entry.get("youtube"):
        opening = (
            f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
            'class="talk-video-preview">'
        )
        media = (
            f'<img src="https://img.youtube.com/vi/{entry["youtube"]}'
            f'/maxresdefault.jpg" alt="{html.escape(_alt(entry), quote=True)}" '
            'loading="lazy" />'
        )
    elif entry.get("image"):
        opening = (
            f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
            'class="talk-video-preview talk-preview-podcast">'
        )
        media = (
            f'<img src="{html.escape(entry["image"], quote=True)}" '
            f'alt="{html.escape(_alt(entry), quote=True)}" loading="lazy" />'
        )
    else:
        opening = (
            f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
            'class="talk-video-preview talk-preview-branded" '
            f'style="--brand-color: {entry["brand_color"]};">'
        )
        media = (
            '<span class="preview-brand-text">'
            f'{html.escape(entry["brand_text"], quote=False)}</span>'
        )
    pad = " " * 32
    return [
        f"{pad}{opening}",
        f"{pad}    {media}",
        f'{pad}    <span class="{icon_class}">',
        f"{pad}        {icon}",
        f"{pad}    </span>",
        f"{pad}</a>",
    ]


def _talk_lines(entry: dict) -> list[str]:
    title = html.escape(entry["title"], quote=False)
    venue = html.escape(entry["venue"], quote=False)
    url = html.escape(entry["url"], quote=True)
    label = BADGES[entry["kind"]]
    pad = " " * 28
    return [
        f'{pad}<div class="timeline-talk has-video">',
        f'{pad}    <div class="talk-content">',
        f'{pad}        <a href="{url}" target="_blank" rel="noopener noreferrer" class="talk-title">',
        f"{pad}            {title}",
        f"{pad}        </a>",
        f'{pad}        <div class="talk-venue">{venue}</div>',
        f'{pad}        <span class="talk-type talk-type-{label.lower()}">{label}</span>',
        f"{pad}    </div>",
        *_preview_lines(entry),
        f"{pad}</div>",
    ]


def render_timeline(entries: list[dict]) -> str:
    pad = " " * 20
    lines = [f'{pad}<div class="timeline-line"></div>']
    year = None
    for entry in entries:
        if entry["date"].year != year:
            if year is not None:
                lines += [f"{pad}    </div>", f"{pad}</div>"]
            year = entry["date"].year
            lines += [
                "",
                f"{pad}<!-- {year} -->",
                f'{pad}<div class="timeline-year-group" data-year="{year}">',
                f'{pad}    <div class="timeline-year-marker">',
                f'{pad}        <span class="timeline-year">{year}</span>',
                f'{pad}        <div class="timeline-dot"></div>',
                f"{pad}    </div>",
                f'{pad}    <div class="timeline-talks">',
            ]
        lines += _talk_lines(entry)
    lines += [f"{pad}    </div>", f"{pad}</div>"]
    return "\n".join(lines) + "\n"


def replace_region(content: str, block: str) -> str:
    try:
        start = content.index(TALKS_START) + len(TALKS_START)
        end = content.index(TALKS_END)
    except ValueError as exc:
        raise DataError(
            f"index.html is missing the {TALKS_START} / {TALKS_END} markers"
        ) from exc
    if end < start:
        raise DataError("talks markers are out of order in index.html")
    return content[:start] + "\n" + block + " " * 20 + content[end:]


def build() -> dict[Path, str]:
    """Render every output in memory. Nothing is written here."""
    talks_feed = FEEDS[0]
    talks = load_talks(REPO_ROOT / talks_feed.data)
    index_path = REPO_ROOT / "index.html"
    return {
        REPO_ROOT / talks_feed.out: render_feed(talks, talks_feed),
        index_path: replace_region(
            index_path.read_text(encoding="utf-8"), render_timeline(talks)
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed output matches the data, write nothing",
    )
    args = parser.parse_args(argv)
    try:
        outputs = build()
    except DataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    stale = []
    for path, wanted in outputs.items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == wanted:
            continue
        if args.check:
            stale.append(path)
            rel = path.relative_to(REPO_ROOT)
            sys.stdout.writelines(
                difflib.unified_diff(
                    current.splitlines(keepends=True),
                    wanted.splitlines(keepends=True),
                    f"{rel} (committed)",
                    f"{rel} (regenerated)",
                )
            )
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(wanted, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO_ROOT)}")
    if args.check:
        if stale:
            print(
                "error: generated files are stale, run scripts/build_feeds.py",
                file=sys.stderr,
            )
            return 1
        # Stale check passed, so each file is byte-identical to generator
        # output, which never emits a DOCTYPE. The guard plus stdlib
        # ElementTree therefore stays safe without a defusedxml dependency,
        # matching the pattern in onlydole/onlydole's parse_goodreads.
        for feed in FEEDS:
            text = (REPO_ROOT / feed.out).read_text(encoding="utf-8")
            lowered = text.lower()
            if "<!doctype" in lowered or "<!entity" in lowered:
                print(
                    f"error: {feed.out} contains DTD or entity declarations",
                    file=sys.stderr,
                )
                return 1
            ElementTree.fromstring(text)
        print("feeds and timeline are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Make it executable and verify the no-markers guard fires**

Run: `chmod +x scripts/build_feeds.py && python3 scripts/build_feeds.py; echo "exit=$?"`
Expected: `error: index.html is missing the <!-- talks:start --> / <!-- talks:end --> markers` and `exit=2`. Nothing is written because build renders everything in memory before any write.

- [ ] **Step 3: Verify validation rejects bad data**

Run:
```bash
python3 - <<'EOF'
import pathlib, subprocess, sys, tempfile, shutil
sys.path.insert(0, "scripts")
import build_feeds

cases = {
    "missing field": '[[talk]]\nslug="x"\ntitle="t"\nvenue="v"\ndate=2026-01-01\nkind="talk"\n',
    "bad kind": '[[talk]]\nslug="x"\ntitle="t"\nvenue="v"\ndate=2026-01-01\nkind="webinar"\nurl="https://x"\nyoutube="y"\n',
    "two previews": '[[talk]]\nslug="x"\ntitle="t"\nvenue="v"\ndate=2026-01-01\nkind="talk"\nurl="https://x"\nyoutube="y"\nimage="https://i"\n',
    "string date": '[[talk]]\nslug="x"\ntitle="t"\nvenue="v"\ndate="2026-01-01"\nkind="talk"\nurl="https://x"\nyoutube="y"\n',
    "dup slug": '[[talk]]\nslug="x"\ntitle="t"\nvenue="v"\ndate=2026-01-01\nkind="talk"\nurl="https://x"\nyoutube="y"\n[[talk]]\nslug="x"\ntitle="t2"\nvenue="v"\ndate=2026-01-02\nkind="talk"\nurl="https://x2"\nyoutube="y2"\n',
}
for name, body in cases.items():
    p = pathlib.Path(tempfile.mkdtemp()) / "talks.toml"
    p.write_text(body)
    try:
        build_feeds.load_talks(p)
        print(f"FAIL {name}: no error raised")
    except build_feeds.DataError as exc:
        print(f"ok   {name}: {exc}")
    shutil.rmtree(p.parent)
EOF
```
Expected: five `ok` lines, no `FAIL` lines.

- [ ] **Step 4: Commit**

```bash
git add scripts/build_feeds.py
git commit -m "Add zero-dependency feed and timeline generator"
```

---

### Task 3: Add markers to index.html and prove faithful regeneration

**Files:**
- Modify: `index.html:413-414` (start marker) and `index.html:594-595` (end marker)
- Create: `feeds/talks.xml` (written by the script)

- [ ] **Step 1: Insert the start marker**

Edit `index.html`, replace

```html
                <div class="timeline">
                    <div class="timeline-line"></div>
```

with

```html
                <div class="timeline">
                    <!-- talks:start -->
                    <div class="timeline-line"></div>
```

- [ ] **Step 2: Insert the end marker**

Edit `index.html`, replace (this is the close of the 2020 year group followed by the close of the timeline div, just before the speaking section ends)

```html
                    </div>
                </div>

            </div>
        </section>

        <section id="writing">
```

with

```html
                    </div>
                    <!-- talks:end -->
                </div>

            </div>
        </section>

        <section id="writing">
```

- [ ] **Step 3: Run the generator**

Run: `python3 scripts/build_feeds.py`
Expected output:
```
wrote feeds/talks.xml
wrote index.html
```

- [ ] **Step 4: Verify the page diff is only what we expect**

Run: `git diff index.html`
Expected. The only changes are the two marker comments and normalized img `alt` text on the five YouTube thumbnail entries (alt becomes `Title, Venue`, while Ship It keeps its alt via `image_alt`). Every other byte of the timeline survives, same year groups, same talk markup, same order, same SVGs. If anything else changed (indentation, attribute order, missing entries), stop and fix `_talk_lines` / `render_timeline` until the diff is clean.

- [ ] **Step 5: Verify determinism and check mode**

Run: `python3 scripts/build_feeds.py && git status --porcelain && python3 scripts/build_feeds.py --check; echo "exit=$?"`
Expected. Second run writes nothing new (no `wrote` lines repeated for changed files is fine, but `git status` shows the same dirty set, nothing further mutates), `--check` prints `feeds and timeline are up to date` and `exit=0`.

- [ ] **Step 6: Verify check mode catches drift**

Run: `sed -i '' 's/Kubernetes 1.19 Release/DRIFT/' data/talks.toml && python3 scripts/build_feeds.py --check; echo "exit=$?"; git checkout data/talks.toml`
Expected: a unified diff mentioning DRIFT, the stale error line, and `exit=1`. The checkout restores the data file.

- [ ] **Step 7: Inspect the feed and validate it parses**

Run: `python3 -c "from xml.etree import ElementTree; t=ElementTree.parse('feeds/talks.xml'); items=t.findall('.//item'); print(len(items)); print(items[0].findtext('title')); print(items[0].findtext('guid')); print(items[0].findtext('pubDate'))"`
Expected:
```
8
The Missing Manual for Open Source Community Sustainability
https://onlydole.dev/talks/2025-11-missing-manual
Tue, 11 Nov 2025 12:00:00 +0000
```

- [ ] **Step 8: Open the page locally and eyeball the timeline**

Run: `open index.html`
Expected: the speaking timeline looks exactly as before.

- [ ] **Step 9: Commit**

```bash
git add index.html feeds/talks.xml
git commit -m "Generate the speaking timeline and talks feed from data"
```

---

### Task 4: Feed autodiscovery and a visible RSS link

**Files:**
- Modify: `index.html:47` (head) and `index.html:407-411` (speaking intro)

- [ ] **Step 1: Add the autodiscovery tag**

Edit `index.html`, replace

```html
        <link rel="apple-touch-icon" href="favicon.png" />
```

with

```html
        <link rel="apple-touch-icon" href="favicon.png" />
        <link
            rel="alternate"
            type="application/rss+xml"
            title="Taylor Dolezal · Talks"
            href="https://onlydole.dev/feeds/talks.xml"
        />
```

- [ ] **Step 2: Add the visible link**

Edit `index.html`, replace

```html
                    <a href="https://fantastical.app/onlydole/schedule" target="_blank" rel="noopener noreferrer">Schedule a call</a> to discuss keynotes, panels, and workshops.
```

with

```html
                    <a href="https://fantastical.app/onlydole/schedule" target="_blank" rel="noopener noreferrer">Schedule a call</a> to discuss keynotes, panels, and workshops, or
                    <a href="/feeds/talks.xml">subscribe to new talks via RSS</a>.
```

- [ ] **Step 3: Verify the check still passes (both edits sit outside the markers)**

Run: `python3 scripts/build_feeds.py --check; echo "exit=$?"`
Expected: `feeds and timeline are up to date`, `exit=0`.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Link the talks feed via autodiscovery and the speaking intro"
```

---

### Task 5: CI drift check

**Files:**
- Create: `.github/workflows/feeds.yml`

- [ ] **Step 1: Create the workflow with exactly this content**

```yaml
name: Feeds

on:
  pull_request:
  push:
    branches: ["main"]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Verify generated feeds and timeline match data
        run: python scripts/build_feeds.py --check
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/feeds.yml
git commit -m "Check generated feeds against data in CI"
```

---

### Task 6: Full content, the research-backed talk list

**Files:**
- Modify: `data/talks.toml` (append eighteen entries, upgrade one title)
- Modify (generated): `index.html`, `feeds/talks.xml`

Provenance for every date below is the 2026-06-11 Exa research pass, verified against sched.com schedules, official episode pages, and the FOSDEM archive. Three entries carry a date caveat for Taylor, marked with comments.

- [ ] **Step 1: Upgrade the PyTorch entry title in data/talks.toml**

Replace

```toml
title = "PyTorch Conference 2024"
```

with

```toml
title = "From Containers to Cognition. Conducting the AI Orchestra"
```

- [ ] **Step 2: Append the eighteen new entries to data/talks.toml**

```toml
[[talk]]
slug = "2025-11-kubefm-contributions"
title = "Navigating Contributions and Community Health in Kubernetes"
venue = "KubeFM podcast"
date = 2025-11-03
kind = "podcast"
url = "https://kube.fm/navigating-contributions-community-taylor"
brand_text = "KubeFM"
brand_color = "#0e7490"

[[talk]]
slug = "2025-03-open-source-ready"
title = "The Whirlwind Pace of AI"
venue = "Open Source Ready, Episode 10"
date = 2025-03-27
kind = "podcast"
url = "https://www.heavybit.com/library/podcasts/open-source-ready/ep-10-the-whirlwind-pace-of-ai-with-taylor-dolezal"
brand_text = "Open Source Ready"
brand_color = "#111827"

[[talk]]
slug = "2025-01-kube-cuddle"
title = "Taylor Dolezal on Kube Cuddle"
venue = "Kube Cuddle, Episode 25"
date = 2025-01-15
kind = "podcast"
url = "https://kubecuddle.transistor.fm/episodes/taylor-dolezal"
brand_text = "Kube Cuddle"
brand_color = "#7c3aed"

[[talk]]
slug = "2024-12-iac-podcast"
title = "CNCF Projects and Open Source Evolution"
venue = "The IaC Podcast"
date = 2024-12-10
kind = "podcast"
url = "https://www.theiacpodcast.com/episode/cncf-projects-and-open-source-evolution-with-taylor-dolezal"
brand_text = "The IaC Podcast"
brand_color = "#4338ca"

[[talk]]
slug = "2024-03-paris-wasm-panel"
title = "Revolutionizing Cloud Native Architectures with WebAssembly"
venue = "KubeCon + CloudNativeCon Europe, Paris"
date = 2024-03-21
kind = "panel"
url = "https://www.youtube.com/watch?v=tu8a-GefJL8"
youtube = "tu8a-GefJL8"

[[talk]]
slug = "2024-03-paris-keynote"
title = "Hip, Hip, Beret! No Cap, Just Cloud Native Facts"
venue = "KubeCon + CloudNativeCon Europe, Paris"
date = 2024-03-21
kind = "keynote"
url = "https://www.youtube.com/watch?v=MICHGBAe8gc"
youtube = "MICHGBAe8gc"

[[talk]]
slug = "2024-03-cloud-native-now"
title = "The Kubernetes Ecosystem"
venue = "Cloud Native Now, EP7"
date = 2024-03-18
kind = "podcast"
url = "https://cloudnativenowpodcast.podbean.com/e/the-kubernetes-ecosystem-with-cncfs-taylor-dolezal/"
brand_text = "Cloud Native Now"
brand_color = "#0284c7"

[[talk]]
slug = "2023-10-new-stack-kubecon"
title = "What Will Be Hot at KubeCon? Platform Engineering, of Course"
venue = "The New Stack Makers"
date = 2023-10-31
kind = "podcast"
url = "https://thenewstack.io/what-will-be-hot-at-kubecon-platform-engineering-of-course/"
brand_text = "The New Stack"
brand_color = "#ec0090"

[[talk]]
slug = "2023-04-openobservability"
title = "Live from KubeCon. Insider Insights with CNCF's Head of Ecosystem"
venue = "OpenObservability Talks"
date = 2023-04-20
kind = "podcast"
url = "https://www.youtube.com/watch?v=a9D5p0SaKL8"
youtube = "a9D5p0SaKL8"

[[talk]]
slug = "2023-04-cappucci-know"
title = "Cappucci-Know. Percolating EU End User Insights in the Cloud Native Café"
venue = "KubeCon + CloudNativeCon Europe, Amsterdam"
date = 2023-04-19
kind = "panel"
url = "https://www.youtube.com/watch?v=4xYH36akGSE"
youtube = "4xYH36akGSE"

[[talk]]
slug = "2023-04-amsterdam-keynote"
title = "Tulips, Terabytes, and Transformations. Blooming Innovations in the Cloud Native Garden"
venue = "KubeCon + CloudNativeCon Europe, Amsterdam"
date = 2023-04-19
kind = "keynote"
url = "https://www.youtube.com/watch?v=-hJAoeV3U3o"
youtube = "-hJAoeV3U3o"

[[talk]]
slug = "2022-06-oss-summit-end-users"
title = "Wandering in the Wonders of the End User Community"
venue = "Open Source Summit North America, Austin"
date = 2022-06-23
kind = "keynote"
url = "https://ossna2022.sched.com/event/11Qje/keynote-wandering-in-the-wonders-of-the-end-user-community-taylor-dolezal-head-of-ecosystem-cloud-native-computing-foundation"
brand_text = "OSS Summit NA"
brand_color = "#00836e"

[[talk]]
slug = "2022-06-platformcon"
title = "Navigating an Infinite Landscape"
venue = "PlatformCon 2022"
date = 2022-06-10
kind = "keynote"
url = "https://www.youtube.com/watch?v=-kmSQRsTOxs"
youtube = "-kmSQRsTOxs"

# Editorial title. The segment ran inside the opening keynote (from 44:22),
# so it has no standalone session title. Adjust freely.
[[talk]]
slug = "2022-05-valencia-end-user"
title = "End User Ecosystem Update"
venue = "KubeCon + CloudNativeCon Europe, Valencia"
date = 2022-05-18
kind = "keynote"
url = "https://www.youtube.com/watch?v=XqEflGXlErA&t=2662s"
youtube = "XqEflGXlErA"

[[talk]]
slug = "2021-12-enterpriseng"
title = "Crafting Kubernetes with Functions. EKS and the CDK for Terraform"
venue = "EnterpriseNG 2021"
date = 2021-12-03
kind = "talk"
url = "https://enterprise.ng-conf.org/session/crafting-kubernetes-with-functions/"
brand_text = "EnterpriseNG"
brand_color = "#dd0031"

# Session day within the Nov 29 to Dec 3 window is unverified.
# Taylor, correct the date if you remember the day.
[[talk]]
slug = "2021-11-reinvent-cdktf"
title = "Optimizing AWS Workflows with the CDK for Terraform"
venue = "AWS re:Invent 2021, Las Vegas"
date = 2021-11-29
kind = "talk"
url = "https://www.youtube.com/watch?v=7SluZSZntKA"
youtube = "7SluZSZntKA"

[[talk]]
slug = "2021-02-hashitalks-governance"
title = "Layered Governance for Your Infrastructure with Kubernetes, OPA, and Terraform"
venue = "HashiTalks 2021"
date = 2021-02-17
kind = "talk"
url = "https://www.hashicorp.com/resources/layered-governance-for-your-infrastructure-with-kubernetes-opa-and-terraform"
brand_text = "HashiTalks '21"
brand_color = "#000000"

# Dash 2020 ran Aug 11 to 12, exact workshop day unverified.
[[talk]]
slug = "2020-08-dash-datadog"
title = "From Provisioning to Production. Automating Observability Principles with Terraform"
venue = "Dash by Datadog 2020"
date = 2020-08-11
kind = "talk"
url = "https://speakerdeck.com/ksatirli/from-provisioning-to-production"
brand_text = "Dash 2020"
brand_color = "#632ca6"
```

- [ ] **Step 3: Regenerate and verify counts**

Run: `python3 scripts/build_feeds.py && python3 -c "from xml.etree import ElementTree; print(len(ElementTree.parse('feeds/talks.xml').findall('.//item')))"`
Expected: `26`

- [ ] **Step 4: Verify ordering and year groups**

Run: `python3 -c "
from xml.etree import ElementTree
items = ElementTree.parse('feeds/talks.xml').findall('.//item')
dates = [i.findtext('pubDate') for i in items]
print(dates[0]); print(dates[-1])
" && grep -c 'timeline-year-group' index.html`
Expected: first pubDate is the 2025-11-11 talk, last is the 2020-08-11 workshop, and `6` year groups (2025, 2024, 2023, 2022, 2021, 2020).

- [ ] **Step 5: Eyeball the page**

Run: `open index.html`
Check every YouTube thumbnail renders (some older videos may lack `maxresdefault.jpg` and show a gray placeholder). For any gray thumbnail, switch that entry from `youtube = "ID"` to `image = "https://img.youtube.com/vi/ID/hqdefault.jpg"` with an `image_alt`, regenerate, and re-check. Check the brand boxes read well in both themes.

- [ ] **Step 6: Commit**

```bash
git add data/talks.toml index.html feeds/talks.xml
git commit -m "Add researched notable appearances to the talks data"
```

---

### Task 7: README and spec touch-up

**Files:**
- Modify: `README.md` (stack note, new section, structure tree)
- Modify: `docs/superpowers/specs/2026-06-11-talks-feed-design.md` (alt text note)

- [ ] **Step 1: Update README.md**

In the Stack list, replace

```markdown
A zero-framework static site built with pure HTML and CSS.
```

with

```markdown
A zero-framework static site built with pure HTML and CSS. Talks data is
generated into the page and an RSS feed by one stdlib-only Python script.
```

After the Local Development section, add

```markdown
## Talks data and feeds

`data/talks.toml` is the single source of truth for speaking appearances.
Editing it and running

```bash
python3 scripts/build_feeds.py
```

regenerates `feeds/talks.xml` and the timeline section of `index.html`
(between the `talks:start` and `talks:end` markers). Commit all three
files together. CI runs the script with `--check` and fails on drift.

The feed lives at [onlydole.dev/feeds/talks.xml](https://onlydole.dev/feeds/talks.xml).
Adding another feed later means adding a TOML file under `data/` and a
`Feed` entry to the registry in `scripts/build_feeds.py`.
```

In the Structure tree, replace

```markdown
├── index.html                    # Single-page site
├── styles.css                    # All styles (~1,200 lines)
```

with

```markdown
├── index.html                    # Single-page site
├── styles.css                    # All styles (~1,200 lines)
├── data/talks.toml               # Talks source of truth
├── scripts/build_feeds.py        # Regenerates feed + timeline
├── feeds/talks.xml               # Generated talks RSS feed
```

- [ ] **Step 2: Amend the spec's byte-for-byte line**

In `docs/superpowers/specs/2026-06-11-talks-feed-design.md`, replace

```markdown
- Timeline content between the markers becomes generated. Existing entries reproduce byte for byte, new entries use the existing preview styles
```

with

```markdown
- Timeline content between the markers becomes generated. Existing entries reproduce byte for byte except img alt text, which normalizes to "Title, Venue" (the hand-written alts were inconsistent). New entries use the existing preview styles
```

- [ ] **Step 3: Verify check still passes and commit**

```bash
python3 scripts/build_feeds.py --check
git add README.md docs/superpowers/specs/2026-06-11-talks-feed-design.md
git commit -m "Document the talks data workflow"
```

---

### Task 8: Open the PR and verify it end to end

- [ ] **Step 1: Push and open the PR**

```bash
git push -u origin talks-feed
gh pr create --title "Make talks data the source of truth, add an RSS feed" --body-file /tmp/talks-feed-pr-body.md
```

The body file is written first with this content (adjust the preview URL after the preview comment appears). It must list every researched entry with its source link, the three flagged caveats (Valencia editorial title, re:Invent date window, Dash date window), the two corrections (Salt Lake City date, PyTorch title), and a QA checklist (timeline renders identically, thumbnails load, feed validates, RSS link visible).

- [ ] **Step 2: Watch CI**

Run: `gh pr checks --watch`
Expected: the Feeds check and the PR Preview deploy both pass.

- [ ] **Step 3: Verify the deployed preview**

Fetch `https://onlydole.github.io/pr-preview/pr-<N>/` and `https://onlydole.github.io/pr-preview/pr-<N>/feeds/talks.xml`. Confirm the page renders, the feed serves as XML, and spot-check thumbnails with a browser tool. Optionally validate the feed with the W3C validator by URL.

- [ ] **Step 4: Stop**

Report to Taylor with the PR link, the preview link, the flagged items, and wait for review. Do not merge.

---

## Phase 2 pointer

Phase 2 (profile repo consumption) gets its own plan at `~/oss/onlydole/docs/superpowers/plans/2026-06-11-talks-feed-consumer.md`, written once this PR's `feeds/talks.xml` exists to freeze into the test fixture. Its shape is fixed by the spec. parse_talks and fetch_talks mirroring the Goodreads pair, fixture-driven TDD, retire `data/talks.yaml`, loader, tests, PyYAML if unused, and the dead `data/**` workflow trigger.
