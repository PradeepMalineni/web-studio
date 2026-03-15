#!/usr/bin/env python3
"""
competitive_research.py — Phase 5 of /recreate-website

Compiles competitive analysis from previously fetched competitor pages.
Takes a JSON input of competitor data (url, industry, fetched HTML snippets)
and produces a structured comparison table in Markdown.

NOTE: This script processes data you've already gathered via WebSearch + WebFetch.
It does NOT make external requests. Feed it the data from your research phase.

Usage:
    python competitive_research.py <competitors.json> <output_dir>

Input JSON format:
    {
      "industry": "SaaS / Project Management",
      "site_name": "AcmeTool",
      "competitors": [
        {
          "name": "Competitor A",
          "url": "https://competitor-a.com",
          "headline": "The hero H1 text",
          "cta_primary": "Primary CTA button text",
          "cta_secondary": "Secondary CTA if any",
          "trust_signals": ["500k users", "G2 rating 4.8", "SOC2 certified"],
          "design_style": "minimalist | bold | corporate | playful | dark | light",
          "sections": ["hero", "features", "pricing", "testimonials", "faq"],
          "unique_angle": "One sentence on what makes them different",
          "notes": "Any other notes"
        }
      ]
    }

Output:
    <output_dir>/analysis/competitive_analysis.md
"""

import sys
import json
from pathlib import Path
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────────────
# Analysis helpers
# ──────────────────────────────────────────────────────────────────────────────

def most_common(items: list) -> str | None:
    if not items:
        return None
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return max(counts, key=counts.get)


def percent(count: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{round(count / total * 100)}%"


def extract_insights(competitors: list[dict]) -> dict:
    """Derive patterns from the competitor data."""
    total = len(competitors)
    if total == 0:
        return {}

    # CTA patterns
    cta_texts = [c.get("cta_primary", "") for c in competitors if c.get("cta_primary")]
    action_words = ["start", "try", "get", "sign up", "join", "build", "launch", "create"]
    action_ctas = [c for c in cta_texts if any(w in c.lower() for w in action_words)]

    # Trust signal frequency
    all_trust = []
    for c in competitors:
        all_trust.extend(c.get("trust_signals", []))
    trust_types = {
        "user_count": sum(1 for t in all_trust if any(x in t.lower() for x in ["user", "customer", "team", "company"])),
        "ratings": sum(1 for t in all_trust if any(x in t.lower() for x in ["rating", "star", "review", "score"])),
        "certifications": sum(1 for t in all_trust if any(x in t.lower() for x in ["certified", "complian", "soc", "iso", "gdpr"])),
        "press": sum(1 for t in all_trust if any(x in t.lower() for x in ["featured", "as seen", "press", "award"])),
    }

    # Section frequency
    all_sections = []
    for c in competitors:
        all_sections.extend(c.get("sections", []))
    section_counts = {}
    for s in all_sections:
        section_counts[s] = section_counts.get(s, 0) + 1
    universal_sections = [s for s, cnt in section_counts.items() if cnt >= total * 0.6]

    # Design style
    styles = [c.get("design_style", "") for c in competitors if c.get("design_style")]
    dominant_style = most_common(styles)

    return {
        "total_competitors": total,
        "action_oriented_ctas": f"{len(action_ctas)}/{total} use action-oriented CTA copy",
        "trust_signals": trust_types,
        "universal_sections": universal_sections,
        "dominant_design_style": dominant_style,
        "cta_examples": cta_texts[:5],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Markdown generator
# ──────────────────────────────────────────────────────────────────────────────

def build_markdown(data: dict) -> str:
    industry = data.get("industry", "Unknown")
    site_name = data.get("site_name", "Target Site")
    competitors = data.get("competitors", [])
    insights = extract_insights(competitors)

    lines = [
        f"# Competitive Analysis — {site_name}",
        f"",
        f"**Industry:** {industry}  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  ",
        f"**Competitors analyzed:** {len(competitors)}",
        "",
        "---",
        "",
        "## Competitor Comparison Table",
        "",
        "| Competitor | Headline Angle | Primary CTA | Trust Signals | Sections | Design Style | Unique Angle |",
        "|---|---|---|---|---|---|---|",
    ]

    for c in competitors:
        trust = ", ".join(c.get("trust_signals", [])[:2]) or "—"
        sections = ", ".join(c.get("sections", [])[:4]) or "—"
        lines.append(
            f"| [{c.get('name', '?')}]({c.get('url', '#')}) "
            f"| {c.get('headline', '—')[:60]} "
            f"| {c.get('cta_primary', '—')} "
            f"| {trust} "
            f"| {sections} "
            f"| {c.get('design_style', '—')} "
            f"| {c.get('unique_angle', '—')[:80]} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Key Patterns & Insights",
        "",
        f"### CTA Strategy",
        f"- {insights.get('action_oriented_ctas', 'N/A')}",
        f"- Most common examples: {', '.join(insights.get('cta_examples', []))}" if insights.get('cta_examples') else "",
        "",
        f"### Trust Signals (frequency across competitors)",
        f"- User/customer count: {insights.get('trust_signals', {}).get('user_count', 0)}/{insights.get('total_competitors', 0)} competitors",
        f"- Ratings/reviews: {insights.get('trust_signals', {}).get('ratings', 0)}/{insights.get('total_competitors', 0)} competitors",
        f"- Certifications: {insights.get('trust_signals', {}).get('certifications', 0)}/{insights.get('total_competitors', 0)} competitors",
        f"- Press/awards: {insights.get('trust_signals', {}).get('press', 0)}/{insights.get('total_competitors', 0)} competitors",
        "",
        f"### Universal Sections (used by 60%+ of competitors)",
        f"- {', '.join(insights.get('universal_sections', [])) or 'No universal sections identified'}",
        "",
        f"### Dominant Design Style",
        f"- {insights.get('dominant_design_style', 'Mixed')}",
        "",
        "---",
        "",
        "## Improvement Recommendations",
        "",
        "Based on the analysis above, apply the following improvements to the recreated site:",
        "",
    ]

    # Generate specific recommendations
    recs = []
    trust = insights.get("trust_signals", {})
    total = insights.get("total_competitors", 1)

    if trust.get("user_count", 0) >= total * 0.6:
        recs.append("**Add social proof metric** — Show user count, customer count, or companies using the product. Used by majority of competitors.")
    if trust.get("ratings", 0) >= total * 0.5:
        recs.append("**Add review/rating widget** — Link to G2, Capterra, or Trustpilot reviews. Used by majority of competitors.")
    if "faq" in insights.get("universal_sections", []):
        recs.append("**Add FAQ section** — Present in majority of competitor sites; reduces support burden and improves conversion.")
    if "testimonials" in insights.get("universal_sections", []):
        recs.append("**Add testimonials** — Social proof through quotes and avatars is standard in this industry.")
    if not recs:
        recs.append("**Strengthen benefit-led headline** — Lead with a specific outcome, not a feature or brand name.")
        recs.append("**Improve CTA specificity** — Replace vague CTAs like 'Learn more' with action-oriented copy like 'Start free today'.")

    for r in recs:
        lines.append(f"- {r}")

    lines += ["", "---", "", "_Generated by ui-ux-designer /recreate-website skill_", ""]
    return "\n".join(l for l in lines if l is not None)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def analyze(input_file: str, output_dir: str):
    data = json.loads(Path(input_file).read_text())
    md = build_markdown(data)

    out_path = Path(output_dir) / "analysis" / "competitive_analysis.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"[competitive_research] Saved → {out_path}")

    # Also print insights to stdout
    insights = extract_insights(data.get("competitors", []))
    print(f"\n── Competitive Insights ──────────────────────────────")
    for k, v in insights.items():
        print(f"  {k}: {v}")
    print(f"──────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python competitive_research.py <competitors.json> <output_dir>")
        sys.exit(1)
    analyze(sys.argv[1], sys.argv[2])
