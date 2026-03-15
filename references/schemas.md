# Data Schemas

Reference for all JSON structures used by the `/launch-website` skill.

---

## site_analysis.json

Output of `scripts/analyze_site.py`. Saved to `<output-dir>/analysis/site_analysis.json`.

```json
{
  "source": "https://example.com",
  "base_url": "https://example.com",
  "html_length": 42000,

  "structure": {
    "sections_detected": ["hero", "features", "pricing", "testimonials", "faq", "footer"],
    "libraries_detected": ["React", "GSAP", "Tailwind"],
    "has_animations": true,
    "animation_names": ["fadeIn", "slideUp"]
  },

  "visual_design": {
    "colors": ["#0f172a", "#6366f1", "#f59e0b", "#ffffff", "#64748b"],
    "fonts": ["Inter", "Poppins", "system-ui"],
    "breakpoints": [640, 768, 1024, 1280],
    "css_custom_properties": {
      "--color-primary": "#6366f1",
      "--radius": "0.5rem"
    }
  },

  "content": {
    "headings": [
      { "level": "h1", "text": "Build faster, ship more" },
      { "level": "h2", "text": "Features" }
    ],
    "cta_buttons": ["Get started free", "See demo"],
    "forms": [
      {
        "action": "/subscribe",
        "fields": [
          { "type": "email", "name": "email", "placeholder": "Enter your email" }
        ]
      }
    ],
    "nav_links": ["/features", "/pricing", "/blog", "/about"]
  },

  "images": [
    {
      "src": "https://example.com/hero.jpg",
      "alt": "Product dashboard screenshot",
      "width": "1280",
      "height": "720",
      "purpose": "hero"
    }
  ],

  "subpages_crawled": [
    { "url": "https://example.com/features", "html_length": 18000 },
    { "url": "https://example.com/pricing", "html_length": 12000 }
  ],

  "class_name_sample": ["container", "hero", "btn", "btn-primary"]
}
```

---

## image_tasks.json

Input to `scripts/generate_images.py`. A list of image generation tasks.

```json
[
  {
    "id": "hero-main",
    "prompt": "A sleek SaaS dashboard interface showing project analytics, dark mode, purple accent colors, modern minimal UI, high-resolution product screenshot style, 4K quality",
    "aspect_ratio": "16:9",
    "purpose": "hero"
  },
  {
    "id": "feature-collaboration",
    "prompt": "Two professionals collaborating on a laptop in a bright modern office, soft natural lighting, photorealistic, warm tones",
    "aspect_ratio": "3:4",
    "purpose": "feature"
  },
  {
    "id": "avatar-sarah",
    "prompt": "Professional headshot of a confident woman in her 30s, business casual, neutral studio background, warm smile",
    "aspect_ratio": "1:1",
    "purpose": "avatar"
  }
]
```

**Aspect ratio quick reference:**

| `purpose` value | Recommended ratio |
|---|---|
| `hero`, `banner` | `16:9` |
| `avatar`, `thumbnail` | `1:1` |
| `portrait`, `card` | `3:4` |
| `cinematic`, `wide` | `21:9` |
| `background`, `mobile-bg` | `9:16` |

---

## manifest.json

Output of `scripts/generate_images.py`. Saved to `<output-dir>/assets/images/manifest.json`.

```json
[
  {
    "id": "hero-main",
    "purpose": "hero",
    "aspect_ratio": "16:9",
    "prompt": "A sleek SaaS dashboard...",
    "kie_task_id": "task_abc123",
    "imgbb_url": "https://i.ibb.co/abc123/hero-main.jpg",
    "status": "generated"
  },
  {
    "id": "feature-collab",
    "purpose": "feature",
    "aspect_ratio": "3:4",
    "prompt": "Two professionals...",
    "status": "failed",
    "error": "Kie AI timeout after 60 polls",
    "placeholder_css": "background: linear-gradient(135deg, #f5f7fa, #c3cfe2); width: 100%; height: 100%;"
  }
]
```

---

## competitors.json

Input to `scripts/competitive_research.py`. Gathered manually via WebSearch + WebFetch.

```json
{
  "industry": "SaaS / Project Management",
  "site_name": "AcmePM",
  "competitors": [
    {
      "name": "Linear",
      "url": "https://linear.app",
      "headline": "The issue tracker you'll enjoy using",
      "cta_primary": "Start for free",
      "cta_secondary": "Book a demo",
      "trust_signals": ["10,000+ teams", "G2 Leader", "SOC 2 Type II"],
      "design_style": "minimalist dark",
      "sections": ["hero", "features", "testimonials", "pricing", "faq"],
      "unique_angle": "Speed and keyboard-first workflow",
      "notes": "Very strong on developer audience, GitHub integration front and center"
    },
    {
      "name": "Notion",
      "url": "https://notion.so",
      "headline": "Your wiki, docs, & projects. Together.",
      "cta_primary": "Get Notion free",
      "cta_secondary": null,
      "trust_signals": ["Used by 30M+ people", "4.7 stars on G2"],
      "design_style": "minimal light with illustration",
      "sections": ["hero", "features", "social-proof", "cta"],
      "unique_angle": "All-in-one workspace for teams",
      "notes": "Leans heavily into network effects and templates library"
    }
  ]
}
```

---

## competitive_analysis.md (output)

Produced by `scripts/competitive_research.py`. Human-readable Markdown comparison table plus improvement recommendations. Saved to `<output-dir>/analysis/competitive_analysis.md`.

Contents:
1. Competitor comparison table (headline, CTA, trust signals, sections, design style, unique angle)
2. Key patterns & insights section (CTA strategy, trust signal frequency, universal sections)
3. Improvement recommendations (specific changes + reasoning)
