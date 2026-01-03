# AI Agent Guidelines

> **Baseline specification for all AI assistants working on this repository.**
> Tool-specific files (CLAUDE.md, WARP.md, .github/copilot-instructions.md) extend these guidelines.

## Project Overview

This is **Taylor Dolezal's personal portfolio website** at [onlydole.dev](https://onlydole.dev). It showcases professional experience, speaking engagements, publications, and open source contributions.

### Tech Stack

- **Pure Static Site**: No frameworks, no build tools, no dependencies
- **HTML5**: Semantic markup in `index.html` (~1,100 lines)
- **CSS3**: Custom properties, animations, responsive design in `styles.css` (~1,200 lines)
- **Hosting**: GitHub Pages with custom domain
- **CI/CD**: GitHub Actions for deployment and PR previews

### Key Constraints

1. **Zero Dependencies**: Do not introduce npm, build tools, or frameworks
2. **No JavaScript**: Site functions without JS (only Cloudflare Analytics)
3. **Single Page**: All content lives in `index.html`
4. **Dark Theme Only**: Color scheme uses `#0f0f0f` background with coral accent `#d4675a`

## Repository Structure

```
/
├── index.html              # Main site content
├── styles.css              # All styling
├── images/                 # Image assets (WebP + JPEG fallbacks)
├── favicon.svg             # Vector favicon
├── favicon.png             # PNG fallback
├── CNAME                   # Custom domain (onlydole.dev)
├── robots.txt              # Search engine directives
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml      # Auto-deploy to GitHub Pages
│   │   └── pr-preview.yml  # PR preview deployments
│   └── CODEOWNERS          # Code ownership
└── AI Spec Files
    ├── AGENTS.md           # This file (baseline)
    ├── CLAUDE.md           # Claude Code specific
    └── WARP.md             # Warp AI specific
```

## Code Style Guidelines

### HTML

- Use semantic HTML5 elements (`<section>`, `<article>`, `<nav>`, etc.)
- Include proper accessibility attributes (`aria-label`, `aria-hidden`)
- Use `<picture>` elements with WebP primary and JPEG fallback
- Add `loading="lazy"` to images below the fold
- Maintain proper heading hierarchy (h1 → h2 → h3)
- Use Open Graph and Twitter Card meta tags for social sharing

### CSS

- Use CSS custom properties for theming (defined in `:root`)
- Follow mobile-first responsive design
- Use kebab-case for class names
- Organize styles by section with clear comments
- Prefer CSS transitions over JavaScript animations
- Use `clamp()` for fluid typography where appropriate

### File Naming

- Use kebab-case for all files
- Images: `{name}.webp` with `.jpg` fallback
- Keep filenames descriptive but concise

## Design System

### Colors

```css
--bg-primary: #0f0f0f;
--bg-secondary: #161616;
--text-primary: #e8e6e3;
--text-secondary: #a8a5a0;
--accent: #d4675a;
--border: #2a2a2a;
```

### Typography

- **Display**: Instrument Serif (headings, hero text)
- **Body**: Outfit (paragraphs, navigation)

### Responsive Breakpoints

- Mobile: < 640px
- Tablet: 640px - 1100px
- Desktop: > 1100px

## Content Sections

1. **Navigation**: Glassmorphic fixed header with hamburger menu (mobile)
2. **Hero**: Name, title, CTAs, hero image with glitch effect
3. **About**: Professional background, credential cards
4. **Work**: Major projects and initiatives
5. **Speaking**: Interactive timeline with embedded media previews
6. **Writing**: Authored books, blog, technical reviewer credits
7. **Connect**: Social links and scheduling
8. **Footer**: Motto, copyright

## Common Tasks

### Adding a New Speaking Engagement

1. Add entry to the appropriate year group in the Speaking section
2. Include: title, event name, date, type (keynote/panel/video/podcast)
3. For videos: add YouTube thumbnail with play button overlay
4. For podcasts: add podcast artwork with audio icon

### Adding a New Publication

1. Add to Writing section with proper category (Authored/Reviewed)
2. Include: title, publisher, year, cover image (WebP + JPEG)
3. Link to purchase/read page

### Updating Work Experience

1. Modify About section credential cards
2. Update Work section if new major project

## Performance Requirements

- Maintain Lighthouse score > 90 for all categories
- Use WebP images with JPEG fallbacks
- Lazy load images below the fold
- Preload critical fonts
- Keep total page weight under 2MB

## Accessibility Requirements

- Maintain WCAG 2.1 AA compliance
- Ensure sufficient color contrast (4.5:1 minimum)
- Provide alt text for all images
- Support keyboard navigation
- Include focus states for interactive elements

## Testing Checklist

Before submitting changes:

- [ ] Validate HTML (no errors)
- [ ] Test responsive layout (mobile, tablet, desktop)
- [ ] Verify all links work
- [ ] Check images load with WebP and fallback
- [ ] Test navigation menu on mobile
- [ ] Verify timeline interactions work
- [ ] Check accessibility with screen reader
- [ ] Run Lighthouse audit

## Git Workflow

- Branch naming: `feature/description` or `fix/description`
- Write clear, descriptive commit messages
- Use PR previews to test changes before merging
- Squash merge to main for clean history

## What NOT to Do

- Do not add npm/node dependencies
- Do not introduce JavaScript frameworks
- Do not add build steps or tooling
- Do not change the color scheme without approval
- Do not modify the CNAME file
- Do not add tracking beyond Cloudflare Analytics
- Do not create multiple HTML pages (keep single-page design)

## Contact

- **Owner**: Taylor Dolezal (@onlydole)
- **GitHub**: [onlydole/onlydole.github.io](https://github.com/onlydole/onlydole.github.io)
