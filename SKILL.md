---
name: ui-ux-designer
description: >
  Recreates, redesigns, and improves websites from scratch using modern web technologies.
  Use this skill whenever the user wants to: clone or recreate an existing website, rebuild
  a site with improved UX/UI, analyze and improve web design, regenerate site images with AI,
  perform competitive web analysis, or produce production-ready HTML/CSS/JS. Trigger on
  /recreate-website, "clone this site", "rebuild my website", "recreate this URL",
  "improve this site's design", or any request involving taking an existing site and
  producing a better version of it.
---

# UI/UX Designer — `/recreate-website`

## Overview

Recreates an entire website from scratch using modern web technologies, improves it with competitive research, generates AI images via Kie AI, hosts them on imgbb, and delivers production-ready code.

**Important:** Do NOT copy the site as-is. Recreate the structure and content with meaningful improvements — better design, stronger copy, superior UX patterns.

## Usage

```
/recreate-website <URL or path/to/file.html> [output-dir]
```

- No arg provided → ask the user for a URL or HTML file path
- Output dir defaults to `./recreated-site`

## Prerequisites

Two environment variables must be set before starting:

| Variable | Purpose | Where to get it |
|---|---|---|
| `KIE_AI_API_KEY` | Image generation via Kie AI (flux-kontext-pro) | https://kie.ai |
| `IMGBB_API_KEY` | Permanent image hosting | https://api.imgbb.com |

Check for these at the start:
```bash
echo "KIE_AI: ${KIE_AI_API_KEY:+SET}" && echo "IMGBB: ${IMGBB_API_KEY:+SET}"
```
If either is missing, inform the user and ask them to set the variable(s) before proceeding.

---

## Execution — 7 Phases

Work through each phase in order. Use `scripts/` helpers where noted. Update the user on progress between phases.

---

### Phase 1 — Analyze the Source Website

**Goal:** Deeply understand what the site is doing so you can recreate and improve it.

Use `scripts/analyze_site.py` to fetch and parse. If it fails (JS-heavy SPA, paywalled, login-gated), ask the user to provide an HTML export.

Extract and document:

1. **Structure**: page sections (hero, features, pricing, testimonials, footer, etc.), HTML hierarchy, grid/flex layout patterns, responsive breakpoints used
2. **Visual design**: exact hex color palette (use a color extractor), typography (font families, sizes, weights, line heights), spacing rhythm, shadow depths, border radii, glassmorphism/gradient usage
3. **Animations**: scroll reveals, hover states, sticky nav behavior, carousels, modals, GSAP/AOS detection
4. **Images**: every image with URL, inferred dimensions, purpose (hero, avatar, icon, background), visual style (photo, illustration, icon), aspect ratio
5. **Content**: all headings (H1–H4), body copy, CTAs (text + placement), forms (fields, labels), nav structure, footer links
6. **Sub-pages**: crawl up to 5 pages linked from the main navigation

Save findings to `<output-dir>/analysis/site_analysis.json` using the schema in `references/schemas.md`.

---

### Phase 2 — Plan the Tech Stack

Choose based on complexity observed in Phase 1:

| Site type | Stack |
|---|---|
| Static/marketing | HTML5 + CSS custom props + Tailwind CDN + vanilla JS |
| Component-heavy / interactive | React + Vite |
| Minimal animation | CSS transitions + Intersection Observer API |
| Complex animation timelines | GSAP (CDN) |

Document the rationale in `README.md`. Prefer CDN over build tooling unless React is genuinely warranted — keep it simple and dependency-light.

---

### Phase 3 — Regenerate Images with Kie AI + imgbb

Use `scripts/generate_images.py`. For every image identified in Phase 1:

1. Write a detailed generation prompt covering: subject, style, mood, dominant colors (from site palette), composition, aspect ratio, lighting
2. Call Kie AI `flux-kontext-pro` model
3. Poll for completion (max 60 attempts, 5s apart)
4. Upload result to imgbb for permanent hosting
5. Record in `assets/images/manifest.json`

**Aspect ratio mapping:**

| Image type | Ratio |
|---|---|
| Hero / banner | 16:9 |
| Square thumbnails / avatars | 1:1 |
| Portrait cards | 3:4 |
| Wide cinematic | 21:9 |
| Tall mobile backgrounds | 9:16 |

**On failure:** use a CSS gradient placeholder styled to match the site's palette. Save the prompt to `assets/images/pending-generation.md` for manual retry.

---

### Phase 4 — Rebuild the Website

Output structure:

```
<output-dir>/
├── index.html
├── assets/
│   ├── css/styles.css
│   ├── js/main.js
│   └── images/
│       ├── manifest.json
│       └── pending-generation.md
├── pages/
│   └── (additional pages if crawled)
└── README.md
```

**Code standards:**
- Semantic HTML5 with descriptive `alt` text and proper ARIA labels
- CSS custom properties (variables) for all colors, typography, and spacing
- Mobile-first responsive with breakpoints: 640px / 768px / 1024px / 1280px
- All animations respect `prefers-reduced-motion: reduce`
- Vanilla JS for interactions; GSAP only for complex multi-step timelines
- No Lorem Ipsum — use actual content, improved where noted in Phase 6
- Minimal external dependencies — CDN only

Build section by section. Start with the full HTML skeleton, then fill in CSS, then JS. Write the complete file; don't truncate.

---

### Phase 5 — Competitive Research

Use `scripts/competitive_research.py`.

1. Identify the site's industry/niche from the analysis
2. Web-search for 5 direct competitors (use WebSearch tool)
3. Fetch each competitor's homepage (use WebFetch tool)
4. Analyze across: design patterns, UX patterns, messaging/positioning angles, unique differentiators, trust signals, CTA strategies
5. Output a structured comparison table to `analysis/competitive_analysis.md`

Format:

```markdown
| Competitor | Design Pattern | CTA Strategy | Trust Signals | Unique Angle |
|---|---|---|---|---|
| ...        | ...            | ...          | ...           | ...          |
```

---

### Phase 6 — Apply Competitive Improvements

Use insights from Phase 5 to upgrade the recreated site. Document every change:

> **Change:** Rewrote hero headline from "Welcome to X" → "Get Y in Z minutes"
> **Why:** 4 of 5 competitors lead with a specific benefit/outcome; this outperforms vague brand welcomes

Apply improvements in these areas (only where the research justifies it):

- **Hero headline**: rewrite to lead with the strongest benefit or outcome
- **CTA copy**: make action-oriented, specific, and urgency-aware ("Start free" > "Learn more")
- **CTA placement**: add above-fold CTA if competitors do; move secondary CTAs per patterns
- **Trust signals**: add testimonials, star ratings, client logos, certifications if 3+ competitors use them
- **Layout/whitespace**: apply superior spacing rhythm or section ordering if observed
- **Missing proven sections**: add "How it works", comparison table, FAQ, social proof — only if research shows it's standard in this industry

**Key constraint:** Preserve the original brand identity (name, color palette, logo style). Only improve — don't rebrand.

---

### Phase 7 — Final Output

Ensure all files are written. Then generate `README.md`:

```markdown
# [Site Name] — Recreated

## Overview
[1-paragraph description of what the site does and what was recreated]

## Tech Stack
[Stack chosen + rationale]

## Running Locally
[Simple instructions: open index.html or run npm dev]

## Image Manifest
[Summary of generated vs. pending images]

## Competitive Analysis Summary
[3-5 key insights from research]

## Improvements Applied
[Bulleted list: what changed and why]

## Manual Steps Needed
[Any pending-generation images, any paywalled pages not crawled, etc.]
```

Print a summary to the user:
- ✅ Images generated: N / Total
- 🔍 Competitors analyzed: N
- ✨ Top improvements applied
- ⚠️ Manual steps needed (if any)

---

## Key Constraints

- **Do not copy verbatim.** Recreate structure and content; rewrite copy to be better.
- **No Lorem Ipsum.** Every piece of text should be real or improved content.
- **Preserve brand identity.** Colors, name, logo style are untouched. Improve everything else.
- **Minimal deps.** CDN > npm install unless React is genuinely warranted.
- **imgbb = permanent.** Kie AI result URLs expire after 14 days; always upload to imgbb.
- **Paywalled pages.** If a page requires login, skip it and note it in manual steps.

---

## Helper Scripts

Read each script before using to understand its flags:

| Script | Purpose |
|---|---|
| `scripts/analyze_site.py` | Fetch, parse, and extract site structure/design/content |
| `scripts/generate_images.py` | Generate images via Kie AI flux-kontext-pro |
| `scripts/upload_imgbb.py` | Upload image to imgbb and return permanent URL |
| `scripts/competitive_research.py` | Compile competitor analysis from fetched pages |
| `scripts/build_site.py` | Scaffold the output directory and file structure |

For full schema reference, see `references/schemas.md`.
For web design patterns and best practices, see `references/web_patterns.md`.
