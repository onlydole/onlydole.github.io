# onlydole.github.io

Personal website for [Taylor Dolezal](https://onlydole.dev) — Head of OSS at [Dosu](https://dosu.dev).

## Stack

A zero-framework static site built with pure HTML and CSS.

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

## Structure

```
.
├── index.html                    # Single-page site
├── styles.css                    # All styles (~1,200 lines)
├── favicon.svg / favicon.png     # Favicon with fallback
├── taylor-web.jpg / .webp        # Hero image
├── images/                       # Book covers and logos
│   ├── terraform-cookbook.*
│   ├── dosu-logo.png
│   └── ... (other book covers)
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml            # Auto-deploy on push
│   │   ├── pr-preview.yml        # PR preview deployments
│   │   ├── validate.yml          # HTML/CSS validation
│   │   └── lighthouse.yml        # Performance audits
│   ├── copilot-instructions.md   # GitHub Copilot config
│   └── CODEOWNERS
├── AGENTS.md                     # AI assistant baseline spec
├── CLAUDE.md                     # Claude Code instructions
├── WARP.md                       # Warp AI instructions
└── README.md
```

## AI Assistant Support

This repository includes configuration files for AI coding assistants:

| File | Purpose |
|------|---------|
| [AGENTS.md](./AGENTS.md) | Baseline specification for all AI assistants |
| [CLAUDE.md](./CLAUDE.md) | Claude Code specific instructions |
| [WARP.md](./WARP.md) | Warp terminal AI instructions |
| [.github/copilot-instructions.md](./.github/copilot-instructions.md) | GitHub Copilot configuration |

AI assistants should read `AGENTS.md` first for project context, then their tool-specific file for additional guidance.

## License

All rights reserved.
