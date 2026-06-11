# Talks feed design

Date 2026-06-11. Approved by Taylor before implementation.

## Goal

Make onlydole.dev the single source of truth for talks and appearances, expose that content as a stable RSS feed, and have the GitHub profile repo (onlydole/onlydole) consume the feed instead of its local `data/talks.yaml`. Two phases, two PRs, one per repo.

## Decisions made

| Topic | Decision |
|---|---|
| Source of truth | One structured data file drives both the page timeline and the feed |
| Data format | TOML at `data/talks.toml`, read with stdlib `tomllib`, zero dependencies |
| Generation | `scripts/build_feeds.py` regenerates feed XML and the timeline HTML, output committed to git |
| Drift protection | New CI workflow runs the script in `--check` mode on PRs and main pushes |
| Deploy | Untouched. Committed artifacts deploy as-is, PR previews serve them for QA |
| Feed format | RSS 2.0 at `/feeds/talks.xml`, venue in description, kind in category, stable slug-based guid |
| Content | Union of current site entries, the KubeFM entry from talks.yaml, and Exa-researched notable appearances, curated in PR review |
| Conflicts | The site wins. Atlanta talk keeps its YouTube link over the YAML's sched.com link |
| Extensibility | Feed registry in the script. A future feed is one TOML file plus one registry entry. Only talks ships now |
| Phase 2 consumer | `fetch_talks` and `parse_talks` mirror the Goodreads pair, DTO shape unchanged from `load_talks` |
| Phase 2 retirement | Delete `load_talks`, its tests, `data/talks.yaml`, unused helpers, and the dead `data/**` workflow trigger |

## Part 1, the website

### Data file

`data/talks.toml` holds one `[[talk]]` table per appearance. Dates in the examples below are illustrative, every real entry ships with a research-verified date.

```toml
[[talk]]
slug = "2025-11-missing-manual"        # permanent feed identity, never edit after merge
title = "The Missing Manual for Open Source Community Sustainability"
venue = "KubeCon + CloudNativeCon North America, Atlanta"
date = 2025-11-11                       # native TOML date
kind = "talk"                           # keynote | talk | panel | podcast
url = "https://youtu.be/FPQB7hQL4Vw"
youtube = "FPQB7hQL4Vw"                 # preview style 1, YouTube thumbnail

[[talk]]
slug = "2022-08-ship-it-69"
title = "The Cloud Native Ecosystem"
venue = "Ship It! Podcast, Episode 69"
date = 2022-08-24
kind = "podcast"
url = "https://changelog.com/shipit/69"
image = "https://cdn.changelog.com/uploads/covers/ship-it-original.png"   # preview style 2
image_alt = "Ship It! Podcast"

[[talk]]
slug = "2021-02-fosdem-governance"
title = "Layered Governance for Infrastructure with Kubernetes, OPA, and Terraform"
venue = "FOSDEM 2021"
date = 2021-02-07
kind = "talk"
url = "https://archive.fosdem.org/2021/schedule/event/kubernetes_layered_governance/"
brand_text = "FOSDEM '21"               # preview style 3, branded color box
brand_color = "#4a286a"
```

Validation rules, enforced by the generator with a clear error and nonzero exit.

- slug, title, venue, date, kind, url are required
- slugs are unique
- kind is one of keynote, talk, panel, podcast
- exactly one preview style per entry (youtube, image, or brand_text with brand_color)
- date is a native TOML date, not a string

Badge labels derive from kind. keynote renders Keynote, panel renders Panel, podcast renders Podcast, talk renders Video, matching the page today.

### Generator

`scripts/build_feeds.py`, Python 3.11 or newer, standard library only (`tomllib`, `xml.etree`, `html`, `email.utils`, `datetime`, `difflib`).

- Loads and validates `data/talks.toml`
- Writes `feeds/talks.xml`
- Regenerates the timeline markup between `<!-- talks:start -->` and `<!-- talks:end -->` markers in `index.html`. The markers sit just inside `<div class="timeline">` and the generated region spans everything within it, including the `timeline-line` div. Markup reproduces the current hand-written structure exactly (year groups newest first, talks within a year newest first, ties broken by slug)
- `--check` rebuilds in memory, diffs against disk, exits 1 with a unified diff on drift
- Deterministic output. Same data in, byte-identical files out, no run timestamps

### Feed format

RSS 2.0 with the atom namespace for the self link.

| RSS element | Content |
|---|---|
| channel title | Taylor Dolezal · Talks |
| channel link | `https://onlydole.dev/#speaking` |
| channel description | Talks, keynotes, panels, and podcast appearances by Taylor Dolezal |
| channel `atom:link` | `href="https://onlydole.dev/feeds/talks.xml" rel="self" type="application/rss+xml"` |
| channel language | en-us |
| channel lastBuildDate | pubDate of the newest item, deterministic |
| item title | talk title, nothing else |
| item link | talk url |
| item description | venue, exactly |
| item category | kind |
| item pubDate | talk date at 12:00:00 +0000, RFC 822 (noon keeps the displayed date correct in nearly every subscriber timezone) |
| item guid | `https://onlydole.dev/talks/<slug>` with `isPermaLink="false"` |

All entries are included, newest first. The consumer caps at three itself.

### Page changes

- Autodiscovery tag in head. `<link rel="alternate" type="application/rss+xml" title="Taylor Dolezal · Talks" href="/feeds/talks.xml">`
- Visible "Subscribe via RSS" link added to the speaking intro paragraph beside the existing scheduling link
- Timeline content between the markers becomes generated. Existing entries reproduce byte for byte, new entries use the existing preview styles
- Nothing else on the page moves

### CI

New workflow `.github/workflows/feeds.yml` on pull_request and push to main. Sets up Python, runs `python scripts/build_feeds.py --check`. The check also re-parses the generated XML for well-formedness. Deploy and preview workflows stay untouched.

### Extensibility

The script defines a registry mapping feed name to data file, channel metadata, and output path. Adding an events or projects feed later is one new TOML file plus one registry entry. A combined everything feed is a registry entry that unions sources sorted by date. None of that ships now. README gains a short section documenting the data file, the script, and the feed URL.

## Content plan

The data file is seeded from three sources.

1. The nine entries on the site today
2. The KubeFM podcast entry from the profile repo's talks.yaml (2025-11-03)
3. Notable appearances surfaced by Exa research across 2017 to 2026

The notability bar. Keynotes and talks at major conferences, appearances on well-known podcasts, significant panels and fireside chats. No meetups, webinars, or minor interviews. Every researched entry carries an exact date and canonical link verified against primary sources, cited in the PR description, and Taylor prunes the list during PR review.

Known consequences. Six current site entries need exact dates the page never showed (research verifies them). The On Stage tile's 2024 keynote line will read slightly differently after cutover because the site's title drops the "Keynote" prefix the YAML had.

## Part 2, the profile repo

### New source functions in generator/sources.py

```python
TALKS_FEED = "https://onlydole.dev/feeds/talks.xml"
```

`parse_talks(feed_text: str) -> list[dict]` mirrors `parse_goodreads`.

- Rejects any document containing `<!doctype` or `<!entity` (lowercased check) before parsing, closing XXE and entity-expansion classes without a defusedxml dependency
- Parses with `ElementTree.fromstring`, wrapping `ParseError` in `SourceError`
- Per item, extracts title, link, description as venue, category as kind defaulting to talk, and pubDate parsed with `email.utils.parsedate_to_datetime` into ISO `YYYY-MM-DD`
- Skips items missing title, link, venue, or a parsable date
- Sorts by date descending, caps at three, raises `SourceError` when nothing usable remains

`fetch_talks() -> list[dict]` mirrors `fetch_goodreads`. httpx.get with a 30 second timeout, follow_redirects, the shared `USER_AGENT` header, `httpx.HTTPError` wrapped in `SourceError`.

The returned dict shape is exactly what `load_talks` returns today, `{"title", "venue", "date", "url", "kind"}`, so the `data-cache.json` "stage" entry stays compatible, last-good fallback covers the cutover, and tile rendering code is untouched.

### build.py change

The stage fetcher becomes `"stage": lambda: sources.fetch_talks()`. Nothing else changes. Failure isolation via the existing try/except and cache fallback is automatic.

### Retirement

In the same PR, matching how `data/reading.yaml` was retired.

- Delete `load_talks` and its tests
- Delete `data/talks.yaml`
- Delete `_load_yaml` if nothing else uses it
- Drop PyYAML from generator dependencies if it loses its last consumer
- Remove the `data/**` path trigger from build-profile.yml since `data/` disappears

### Failure isolation

| Failure | Behavior |
|---|---|
| Feed HTTP error or timeout | `SourceError`, tile serves last-good cached entries |
| Feed unparsable or DTD detected | `SourceError`, tile serves last-good cached entries |
| Feed empty or all items invalid | `SourceError`, tile serves last-good cached entries |
| Everything down | Whole tile at last-good, build exits 0 |

## Testing

Phase 1. The `--check` CI job is the regression net. Acceptance verified on the PR preview, timeline renders identically for existing entries, feed serves and parses.

Phase 2, TDD with pytest.

- New fixture `tests/fixtures/talks.xml` generated by the phase 1 script, so the fixture is the real wire format
- Parser tests written first. Field extraction against the fixture, three-item cap and descending order, doctype rejection raises, garbage raises, empty feed raises, items missing fields are skipped
- `test_build.py` monkeypatching switches from `load_talks` to `fetch_talks`, stage failure isolation stays covered
- Suite green via `uv run --project generator pytest tests/ -v`, lint clean via `ruff check generator tests`
- No new dependencies, no secrets, no third-party services

## Process and sequencing

1. Phase 1 PR on this repo. Implement, regenerate, verify on the PR preview, CI green, stop for Taylor's review
2. Phase 2 PR on onlydole/onlydole. Branch and PR only, never push to main (signed commits required there). CI green, then work the bot reviews. Verify each finding against the code, fix real ones, decline false ones with evidence, resolve all threads without posting replies. Stop for Taylor's visual QA
3. Merge order. Phase 1 merges and deploys before phase 2 merges, since the daily profile build fetches the live feed

## Acceptance criteria

1. `feeds/talks.xml` is valid, stable RSS 2.0 served from onlydole.dev, linked via autodiscovery and a visible page link
2. Regenerating with unchanged data produces zero diff, and CI fails on any drift between data and generated files
3. The speaking timeline renders identically for existing entries and gains only the approved new ones
4. Adding a future feed requires only a data file and a registry entry
5. The profile repo builds the On Stage tile from the live feed with rendering code untouched, and serves last-good content when the feed is unreachable
6. `data/talks.yaml` and its loader are gone, suite green, ruff clean, no new dependencies
