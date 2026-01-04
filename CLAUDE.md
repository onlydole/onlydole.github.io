# Claude Code Instructions

> **Claude-specific guidelines for this repository.**
> Extends the baseline specification in [AGENTS.md](./AGENTS.md).

## Quick Reference

This is Taylor Dolezal's static portfolio site. Key facts:

- **No build tools**: Pure HTML/CSS, no npm or frameworks
- **Single file architecture**: `index.html` + `styles.css`
- **GitHub Pages hosting**: Auto-deploys from main branch
- **PR previews**: Available at `onlydole.dev/pr-preview/pr-{number}/`

## Working with This Codebase

### Before Making Changes

1. Read [AGENTS.md](./AGENTS.md) for complete project context
2. Use the Explore agent to understand the current structure
3. Check `index.html` for content changes, `styles.css` for styling

### File Editing Approach

Since this is a single-page site with two main files:

- **Content changes**: Edit `index.html` directly
- **Style changes**: Edit `styles.css` directly
- **Images**: Add to `images/` directory with WebP + JPEG formats

### When Adding New Sections

1. Follow the existing section pattern in `index.html`:
   ```html
   <section id="section-name" class="section">
     <div class="container">
       <h2 class="section-title">Section Title</h2>
       <!-- Content -->
     </div>
   </section>
   ```

2. Add corresponding styles to `styles.css` in the appropriate section

3. Update navigation if the section should be linked

### Common Operations

#### Add a Speaking Engagement

Look for the Speaking section timeline in `index.html`. Add new entries following the existing pattern with:
- Event title and link
- Event name, date, and type badge
- Thumbnail image (for videos) or branded preview card

#### Add a Publication

Find the Writing section and add within the appropriate category (authored-books or reviewed-books).

#### Update Professional Info

Modify the About section's credential cards or work-item entries.

## Claude-Specific Behaviors

### Do

- Use the Task tool with Explore agent for understanding structure
- Make surgical edits to specific sections
- Validate HTML structure after edits
- Suggest WebP image optimizations
- Check for accessibility compliance
- Test responsive breakpoints mentally when editing CSS

### Don't

- Create new HTML files (single-page only)
- Suggest JavaScript solutions (CSS-first approach)
- Introduce dependencies or build tools
- Modify CI/CD workflows without explicit request
- Change the color scheme or typography without approval

### Response Style

When discussing this project:
- Reference specific line numbers when suggesting edits
- Provide complete HTML/CSS snippets ready to paste
- Explain accessibility implications of changes
- Note responsive design considerations

## Development Workflow

### Testing Changes

1. Edit files locally
2. Push to a feature branch
3. Open PR to trigger preview deployment
4. Review at `onlydole.dev/pr-preview/pr-{number}/`
5. Merge to main for production deployment

### Validation Commands

```bash
# Validate HTML
npx html-validate index.html

# Check for broken links
npx linkinator index.html --skip "^(?!http)"

# Run Lighthouse audit
npx lighthouse https://onlydole.dev --output html
```

Note: These commands require npx but don't add dependencies to the project.

## Image Handling

When adding images:

1. Provide both WebP and JPEG versions
2. Use descriptive filenames in kebab-case
3. Optimize images (aim for < 100KB each)
4. Use `<picture>` element with fallbacks:
   ```html
   <picture>
     <source srcset="images/name.webp" type="image/webp">
     <img src="images/name.jpg" alt="Description" loading="lazy">
   </picture>
   ```

## Troubleshooting

### PR Preview Not Showing

- Check if PR is from a fork (previews disabled for security)
- Verify PR is to the main branch
- Wait a few minutes for deployment

### Styles Not Applying

- Check CSS selector specificity
- Verify responsive breakpoint order
- Clear browser cache

### Images Not Loading

- Confirm files exist in `images/` directory
- Check file extensions match (case-sensitive)
- Verify path is relative from root

## Project Context

Taylor Dolezal is Head of Open Source Software at Dosu, previously at CNCF and HashiCorp. This site showcases:

- Cloud native and Kubernetes expertise
- Speaking engagements at major conferences
- Published books and technical reviews
- Open source leadership and contributions

Keep this context in mind when suggesting content or structural changes.
