# ui-ux-designer

A Claude skill that recreates and improves websites from scratch — with AI-generated images, competitive research, and production-ready code.

## What It Does

Invoke `/recreate-website <URL>` and the skill will:

1. **Analyze** the source site (structure, colors, fonts, images, content)
2. **Plan** the right tech stack (static HTML or React)
3. **Generate images** via Kie AI + host permanently on imgbb
4. **Rebuild** the site with semantic HTML5, CSS custom properties, and vanilla JS
5. **Research** 5 competitors and analyze their design/UX patterns
6. **Improve** the rebuilt site using competitive insights
7. **Deliver** production-ready files + full README

## Usage

```
/recreate-website https://example.com
/recreate-website ./local-export.html ./my-output-dir
```

## Prerequisites

```bash
export KIE_AI_API_KEY=your_key    # https://kie.ai
export IMGBB_API_KEY=your_key     # https://api.imgbb.com
```

## Structure

```
ui-ux-designer/
├── SKILL.md                         Main skill instructions (7 phases)
├── scripts/
│   ├── analyze_site.py              Phase 1: Fetch + parse source site
│   ├── generate_images.py           Phase 3: Kie AI + imgbb pipeline
│   ├── upload_imgbb.py              Standalone imgbb uploader
│   ├── competitive_research.py      Phase 5: Compile competitor analysis
│   └── build_site.py                Phase 4: Scaffold output files
├── references/
│   ├── schemas.md                   JSON schemas for all data files
│   └── web_patterns.md              Design patterns, CTA formulas, accessibility
└── assets/templates/
    ├── image_tasks_template.json    Starter template for image generation tasks
    └── competitors_template.json   Starter template for competitor data
```

## Key Principles

- **Never copy verbatim** — recreate and improve, don't clone
- **Preserve brand identity** — keep colors, name, logo style intact
- **No Lorem Ipsum** — all content must be real or improved
- **imgbb for permanence** — Kie AI URLs expire; always upload to imgbb
- **Minimal deps** — CDN over npm unless React is genuinely needed

## Installation

Copy the `ui-ux-designer/` folder into your Claude skills directory, or install the `.skill` package if provided.

---

Built for [Claude Code](https://claude.ai/claude-code) and [Cowork](https://claude.ai).
