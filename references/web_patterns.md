# Web Design Patterns Reference

Best practices for the `/launch-website` skill  -  Phase 4 (Build) and Phase 6 (Competitive Improvements).

---

## Hero Section Patterns

### Benefit-led headlines (preferred)
Convert feature descriptions into outcome statements:

| [x] Feature-led | [ok] Benefit-led |
|---|---|
| "AI-powered writing tool" | "Write 10x faster with AI that knows your voice" |
| "Project management software" | "Ship projects on time, every time" |
| "Analytics dashboard" | "See exactly why users drop off  -  fix it in hours" |

### Hero structures that convert
1. **Eyebrow + H1 + subtitle + dual CTA + hero image**  -  most common SaaS pattern
2. **H1 + animated word swap + CTA**  -  tech/startup
3. **Split layout: copy left, product right**  -  product-led companies
4. **Full-bleed video background + centered copy**  -  lifestyle/brand

### CTA copy formulas
- "Start [benefit] free" -> "Start shipping faster free"
- "Get [product] free" -> standard, high conversion
- "Try [product] for [time]" -> reduces commitment fear
- "See [product] in action" -> for demo-first products
- Avoid: "Learn more", "Click here", "Submit"

---

## Section Ordering (Conversion-Optimized)

1. Nav (sticky)
2. Hero (H1 + primary CTA + hero image)
3. Social proof logos ("Trusted by X companies")  -  immediately after hero
4. Features / how it works
5. Testimonials / case studies
6. Pricing (if applicable)
7. FAQ
8. Final CTA banner
9. Footer

---

## Trust Signal Patterns

### By conversion stage
- **Top of funnel (hero area):** User/customer counts ("10,000+ teams"), logo cloud, star rating aggregate
- **Mid-funnel (features section):** Specific metrics ("reduces time by 40%"), certifications (SOC2, GDPR)
- **Bottom of funnel (near CTA):** Money-back guarantee, free trial, no credit card required

### Logo clouds
- Show 5-8 recognizable brand logos
- Grayscale by default, colorize on hover
- Label: "Trusted by teams at..." or "Used by 10,000+ companies"

---

## Responsive Design

### Breakpoint strategy (mobile-first)
```css
/* Base: mobile (< 640px) */
.grid { display: grid; grid-template-columns: 1fr; }

/* Small tablet */
@media (min-width: 640px) { ... }

/* Tablet */
@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop */
@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* Wide desktop */
@media (min-width: 1280px) { ... }
```

### Typography scaling
Use `clamp()` for fluid type:
```css
h1 { font-size: clamp(2rem, 5vw, 4rem); }
h2 { font-size: clamp(1.5rem, 3vw, 2.5rem); }
```

---

## Animation Best Practices

### Scroll reveals (always use Intersection Observer)
```js
const observer = new IntersectionObserver(
  entries => entries.forEach(e => e.isIntersecting && e.target.classList.add('visible')),
  { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
);
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

### Respect reduced-motion preference
```css
@media (prefers-reduced-motion: no-preference) {
  .reveal { opacity: 0; transform: translateY(24px); transition: opacity 0.6s, transform 0.6s; }
  .reveal.visible { opacity: 1; transform: none; }
}
```

### When to use GSAP
Only when you need:
- Synchronized multi-element timelines
- Scroll-triggered scrubbed animations (ScrollTrigger)
- Physics-based motion (Draggable, inertia)
- SVG morphing

Otherwise, CSS transitions + Intersection Observer is sufficient and lighter.

---

## Accessibility Checklist

- `<nav aria-label="Main navigation">`  -  distinguish multiple navs
- `<main>` wrapping the primary content
- `<section aria-labelledby="section-id">` for each section
- `<img alt="...">`  -  descriptive, not "image of..."
- Buttons have visible focus states: `:focus-visible { outline: 2px solid var(--color-primary); }`
- Color contrast: AA minimum 4.5:1 for body text, 3:1 for large text
- Mobile tap targets: minimum 44x44px
- Skip link: `<a class="sr-only" href="#main">Skip to content</a>`

---

## Color Usage Guidelines

### Hierarchy
- **Primary color**  -  main CTAs, active states, key highlights (use sparingly)
- **Secondary color**  -  eyebrow labels, badges, secondary accents
- **Neutral scale**  -  text (dark), borders (light), backgrounds (near-white)
- **Semantic**  -  success (#22c55e), warning (#f59e0b), error (#ef4444)

### Dark mode readiness
Use CSS custom properties for all color values so dark mode can be added later:
```css
:root { --color-bg: #ffffff; --color-text: #0f172a; }
@media (prefers-color-scheme: dark) {
  :root { --color-bg: #0f172a; --color-text: #f8fafc; }
}
```

---

## Pricing Section Patterns

### Most common SaaS pricing layouts
1. **3-column (Free / Pro / Enterprise)**  -  standard
2. **Toggle monthly/annual**  -  increases perceived value of annual
3. **Usage-based calculator**  -  for API/volume pricing
4. **"Contact us" for Enterprise**  -  avoids anchoring high numbers

### Pricing card anatomy
- Plan name + eyebrow label (e.g., "Most popular")
- Price + billing period
- Feature list with checkmarks (5-8 items)
- CTA button
- Social proof underneath ("Join 2,000+ teams on Pro")

---

## FAQ Pattern (Accessible)

Use native `<details>`/`<summary>` for zero-JS accordion:
```html
<details>
  <summary>Is there a free trial?</summary>
  <p>Yes, all plans include a 14-day free trial with no credit card required.</p>
</details>
```

Style open state:
```css
details[open] summary { color: var(--color-primary); }
details + details { border-top: 1px solid var(--color-border); }
```

---

## Image Prompt Writing Guide (for Kie AI)

Strong prompts include:
1. **Subject**  -  what the image shows
2. **Style**  -  photo, illustration, 3D render, flat icon
3. **Mood/tone**  -  professional, warm, energetic, minimal
4. **Color**  -  tie to brand palette (e.g., "purple accent tones")
5. **Composition**  -  wide shot, portrait, isometric, close-up
6. **Quality markers**  -  "photorealistic", "4K", "high-resolution", "sharp details"
7. **Lighting**  -  soft natural, studio, golden hour

**Examples:**
```
Hero (16:9):
"A diverse team of professionals collaborating around a large monitor showing a
project dashboard, modern open office, natural lighting from floor-to-ceiling
windows, shallow depth of field, photorealistic, 4K, warm neutral tones with
subtle purple accent in the UI"

Feature illustration (3:4):
"Minimal flat illustration of a rocket launching from a laptop screen, clean
white background, geometric shapes, indigo and violet color palette, modern
SaaS product style, no text"

Avatar (1:1):
"Professional headshot, confident woman in her 30s, business casual attire,
soft studio background, warm smile, sharp focus on face, photorealistic"
```

**Avoid:**
- Text in images (Kie AI handles text poorly)
- Very specific faces of real people
- Copyrighted brand logos or mascots
- Extremely complex scenes with many small details
