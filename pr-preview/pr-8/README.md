# onlydole.github.io

Personal website for [Taylor Dolezal](https://onlydole.dev) — Head of OSS at [Dosu](https://dosu.dev).

## Stack

A zero-framework static site built with pure HTML and CSS. Talks data is
generated into the page and an RSS feed by one stdlib-only Python script.

- **Fonts**: Instrument Serif (display) + Outfit (body) via Google Fonts
- **Analytics**: Cloudflare Web Analytics
- **Hosting**: GitHub Pages
- **Deployment**: Automatic via GitHub Actions on push to `main`

## Features

- **Dark theme** with accent color (`#d4675a`)
- **Interactive speaking timeline** with expandable year groups and video previews
- **Responsive design** with mobile hamburger navigation
- **Performance optimized**: WebP images with fallbacks, lazy loading, font preloading
- **Glassmorphism header** with backdrop blur

## Sections

1. **About** — Professional background and credentials
2. **Work** — Featured projects and initiatives
3. **Speaking** — Timeline of keynotes, panels, and podcasts with embedded video thumbnails
4. **Writing** — Authored books and technical reviewer credits
5. **Connect** — Social links and scheduling

## Local Development

Open `index.html` in a browser. No build step required.

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

## Structure

```
.
├── index.html                    # Single-page site
├── styles.css                    # All styles (~1,200 lines)
├── data/talks.toml               # Talks source of truth
├── scripts/build_feeds.py        # Regenerates feed + timeline
├── feeds/talks.xml               # Generated talks RSS feed
├── favicon.svg / favicon.png     # Favicon with fallback
├── taylor-web.jpg / .webp        # Hero image
├── images/                       # Book covers and logos
│   ├── terraform-cookbook.*
│   ├── dosu-logo.png
│   └── ... (other book covers)
├── .github/
│   ├── workflows/deploy.yml      # Auto-deploy on push
│   └── CODEOWNERS
└── README.md
```

## License

All rights reserved.
