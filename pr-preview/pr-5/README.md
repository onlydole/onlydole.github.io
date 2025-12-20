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
│   ├── workflows/deploy.yml      # Auto-deploy on push
│   └── CODEOWNERS
└── README.md
```

## License

All rights reserved.
