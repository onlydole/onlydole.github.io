# GitHub Copilot Instructions

> **GitHub Copilot-specific guidelines for this repository.**
> Extends the baseline specification in [AGENTS.md](../AGENTS.md).

## Project Context

This is a **static portfolio website** for Taylor Dolezal (onlydole.dev). The site uses pure HTML and CSS with no JavaScript frameworks or build tools.

## Code Generation Guidelines

### HTML Patterns

When generating HTML for this project:

```html
<!-- Use semantic elements -->
<section id="section-name" class="section">
  <div class="container">
    <h2 class="section-title">Title</h2>
    <!-- Content -->
  </div>
</section>

<!-- Use picture elements for images -->
<picture>
  <source srcset="images/name.webp" type="image/webp">
  <img src="images/name.jpg" alt="Descriptive alt text" loading="lazy">
</picture>

<!-- Include accessibility attributes -->
<button aria-label="Open menu" aria-expanded="false">
  <span class="hamburger"></span>
</button>

<!-- Use proper link patterns -->
<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  Link Text
</a>
```

### CSS Patterns

When generating CSS for this project:

```css
/* Use CSS custom properties for colors */
.element {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

/* Use accent color for interactive elements */
.button, .link:hover {
  color: var(--accent);
}

/* Mobile-first responsive design */
.element {
  padding: 1rem;
}

@media (min-width: 640px) {
  .element {
    padding: 2rem;
  }
}

@media (min-width: 1100px) {
  .element {
    padding: 3rem;
  }
}

/* Use transitions for interactivity */
.interactive {
  transition: all 0.3s ease;
}
```

### Available CSS Variables

```css
:root {
  --bg-primary: #0f0f0f;
  --bg-secondary: #161616;
  --text-primary: #e8e6e3;
  --text-secondary: #a8a5a0;
  --accent: #d4675a;
  --border: #2a2a2a;
}
```

### Typography Classes

- `.section-title` - Section headings (Instrument Serif)
- `.subtitle` - Subheadings
- Body text uses Outfit font family

## Do NOT Generate

- JavaScript code (site is JS-free except analytics)
- Import statements or module syntax
- npm/package.json related code
- Build tool configurations (webpack, vite, etc.)
- React, Vue, or other framework code
- Node.js server code
- Multiple HTML pages (single-page site)

## Do Generate

- Semantic HTML5 markup
- CSS using custom properties
- Accessible markup with ARIA attributes
- Responsive CSS with media queries
- CSS animations and transitions
- Picture elements with WebP/JPEG sources

## File Structure Awareness

| File | Purpose |
|------|---------|
| `index.html` | All page content |
| `styles.css` | All styling |
| `images/` | Image assets |
| `.github/workflows/` | CI/CD |

## Completion Preferences

When completing code in this project:

1. **Prefer CSS over JS**: Use CSS for animations, transitions, and interactivity
2. **Use existing variables**: Reference `var(--name)` for colors
3. **Follow existing patterns**: Match the style of surrounding code
4. **Include accessibility**: Add `aria-*` attributes where appropriate
5. **Lazy load images**: Add `loading="lazy"` to images below the fold
6. **Use kebab-case**: For CSS classes and file names

## Section Patterns

### Timeline Item (Speaking Section)

```html
<div class="timeline-item">
  <div class="timeline-dot"></div>
  <div class="timeline-content">
    <div class="timeline-meta">
      <span class="timeline-event">Event Name</span>
      <span class="timeline-date">Month Year</span>
    </div>
    <h3>
      <a href="URL" target="_blank" rel="noopener noreferrer">
        Talk Title
      </a>
    </h3>
    <span class="talk-type keynote">Keynote</span>
  </div>
</div>
```

### Work Item

```html
<div class="work-item">
  <div class="work-meta">
    <span class="work-company">Company</span>
    <span class="work-date">Year</span>
  </div>
  <h3>Project Title</h3>
  <p>Description of the work and impact.</p>
</div>
```

### Book Card

```html
<div class="book-card">
  <picture>
    <source srcset="images/book.webp" type="image/webp">
    <img src="images/book.jpg" alt="Book Title cover" loading="lazy">
  </picture>
  <div class="book-info">
    <h3>Book Title</h3>
    <p class="publisher">Publisher, Year</p>
  </div>
</div>
```

## Testing Reminders

After generating code, verify:

- [ ] HTML validates without errors
- [ ] CSS selectors are specific enough
- [ ] Colors use CSS variables
- [ ] Images have alt text
- [ ] Links have proper attributes
- [ ] Responsive at all breakpoints
