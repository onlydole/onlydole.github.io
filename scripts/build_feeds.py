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
import re
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
        if entry.get("brand_color") and not re.fullmatch(
            r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", entry["brand_color"]
        ):
            raise DataError(
                f"talk {slug!r} brand_color must be a 3- or 6-digit hex color"
            )
        if entry.get("youtube") and not re.fullmatch(
            r"[A-Za-z0-9_-]{11}", entry["youtube"]
        ):
            raise DataError(f"talk {slug!r} youtube must be an 11-character video id")
        if entry.get("youtube_thumb") not in (None, "maxresdefault", "sddefault", "hqdefault"):
            raise DataError(
                f"talk {slug!r} youtube_thumb must be maxresdefault, sddefault, or hqdefault"
            )
    entries.sort(key=lambda e: (e["date"], e["slug"]), reverse=True)
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
        thumb = entry.get("youtube_thumb", "maxresdefault")
        media = (
            f'<img src="https://img.youtube.com/vi/{entry["youtube"]}'
            f'/{thumb}.jpg" alt="{html.escape(_alt(entry), quote=True)}" '
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
    outputs: dict[Path, str] = {}
    index_path = REPO_ROOT / "index.html"
    for feed in FEEDS:
        entries = load_talks(REPO_ROOT / feed.data)
        outputs[REPO_ROOT / feed.out] = render_feed(entries, feed)
        if feed.name == "talks":
            outputs[index_path] = replace_region(
                index_path.read_text(encoding="utf-8"), render_timeline(entries)
            )
    return outputs


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
        # ElementTree therefore stays safe without a defusedxml dependency.
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
