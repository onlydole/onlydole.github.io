# Warp AI Instructions

> **Warp terminal AI-specific guidelines for this repository.**
> Extends the baseline specification in [AGENTS.md](./AGENTS.md).

## Project Summary

Static portfolio site for Taylor Dolezal at onlydole.dev.

| Aspect | Details |
|--------|---------|
| Type | Static HTML/CSS site |
| Build | None (no npm, no frameworks) |
| Files | `index.html`, `styles.css`, `images/` |
| Hosting | GitHub Pages |
| Deploy | Auto on push to main |

## Quick Commands

### Development

```bash
# Start local server
python3 -m http.server 8000
# or
npx serve .

# Open in browser
open http://localhost:8000
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/description

# Push and create PR
git push -u origin feature/description
gh pr create --fill

# Check PR preview URL
echo "https://onlydole.dev/pr-preview/pr-$(gh pr view --json number -q .number)/"
```

### Validation

```bash
# Validate HTML
npx html-validate index.html

# Check links
npx linkinator index.html

# Lighthouse audit
npx lighthouse https://onlydole.dev --output html --output-path report.html

# Image optimization check
du -sh images/*
```

### Image Processing

```bash
# Convert to WebP (requires cwebp)
cwebp -q 80 input.jpg -o output.webp

# Resize image (requires ImageMagick)
convert input.jpg -resize 800x600 output.jpg

# Optimize JPEG (requires jpegoptim)
jpegoptim --max=85 --strip-all image.jpg
```

## File Locations

| Content Type | File | Section ID |
|--------------|------|------------|
| Navigation | `index.html` | `nav` |
| Hero/Header | `index.html` | `hero` |
| About | `index.html` | `about` |
| Work/Projects | `index.html` | `work` |
| Speaking | `index.html` | `speaking` |
| Writing | `index.html` | `writing` |
| Contact | `index.html` | `connect` |
| All Styles | `styles.css` | N/A |

## Terminal Tasks

### Find Content

```bash
# Find section in HTML
grep -n 'id="speaking"' index.html

# Find CSS class
grep -n '.timeline-item' styles.css

# Count sections
grep -c '<section' index.html
```

### Check Site Health

```bash
# File sizes
ls -lh index.html styles.css

# Image inventory
ls -lh images/

# Total size
du -sh .

# Git status
git status --short
```

### Deployment Status

```bash
# Check recent workflows
gh run list --limit 5

# View deploy logs
gh run view --log

# Check PR preview status
gh pr checks
```

## Warp-Specific Tips

### Blocks to Use

When editing this site, useful Warp blocks:

1. **File Preview**: Use to quickly view HTML/CSS structure
2. **Git Diff**: Review changes before committing
3. **Workflow Output**: Monitor GitHub Actions deployments

### AI Prompts That Work Well

- "Show me the CSS for the timeline section"
- "Find where speaking engagements are listed"
- "What's the color scheme defined in styles.css"
- "Generate a command to optimize all images in images/"

### Workflows to Save

Consider saving these as Warp workflows:

1. **Local Preview**: Start server and open browser
2. **PR Flow**: Branch, push, create PR, get preview URL
3. **Validate**: Run HTML validation and link check
4. **Deploy Check**: View recent GitHub Actions runs

## Constraints Reminder

- No npm packages in the project (use npx for tools)
- No JavaScript files to add
- Single HTML file only
- Dark theme with coral accent (#d4675a)
- All images need WebP + JPEG versions

## Common Patterns

### Adding Images

```bash
# 1. Add both formats to images/
cp ~/Downloads/new-image.jpg images/
cwebp -q 80 images/new-image.jpg -o images/new-image.webp

# 2. Use in HTML with picture element
cat << 'EOF'
<picture>
  <source srcset="images/new-image.webp" type="image/webp">
  <img src="images/new-image.jpg" alt="Description" loading="lazy">
</picture>
EOF
```

### Quick Edits

```bash
# Open files in editor
code index.html styles.css

# Or use vim for quick changes
vim index.html +'/id="speaking"'
```

## Troubleshooting Commands

```bash
# Clear git cache if needed
git rm -r --cached .
git add .

# Reset to last commit
git checkout -- .

# Check remote status
git remote -v
git fetch origin

# View GitHub Pages status
gh api repos/:owner/:repo/pages
```

## Resources

- [AGENTS.md](./AGENTS.md) - Full project specification
- [GitHub Repo](https://github.com/onlydole/onlydole.github.io)
- [Live Site](https://onlydole.dev)
- [PR Previews](https://onlydole.dev/pr-preview/) - For open PRs
