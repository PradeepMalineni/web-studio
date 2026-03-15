#!/usr/bin/env python3
"""
analyze_site.py — Phase 1 of /recreate-website

Fetches a URL or reads a local HTML file, extracts structure, design tokens,
content, images, and animations. Saves a JSON analysis to the output directory.

Usage:
    python analyze_site.py <url_or_file> <output_dir>

Output:
    <output_dir>/analysis/site_analysis.json
"""

import sys
import os
import json
import re
import time
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# HTML Parser
# ──────────────────────────────────────────────────────────────────────────────

class SiteParser(HTMLParser):
    """Lightweight HTML parser that collects structure and content signals."""

    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
        self.headings = []
        self.nav_items = []
        self.cta_buttons = []
        self.forms = []
        self.current_tags = []
        self.inline_styles = []
        self.class_names = []
        self.colors_found = set()
        self.fonts_found = set()
        self.current_form = None
        self._text_buffer = ""
        self._current_heading_level = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tags.append(tag)

        # Collect class names for design pattern analysis
        if "class" in attrs_dict:
            for cls in attrs_dict["class"].split():
                self.class_names.append(cls)

        # Collect inline styles for color/font extraction
        if "style" in attrs_dict:
            style = attrs_dict["style"]
            self.inline_styles.append(style)
            self._extract_style_tokens(style)

        # Images
        if tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            width = attrs_dict.get("width", "")
            height = attrs_dict.get("height", "")
            if src and not src.startswith("data:"):
                self.images.append({
                    "src": src,
                    "alt": alt,
                    "width": width,
                    "height": height,
                    "purpose": self._infer_image_purpose(src, alt, self.current_tags),
                })

        # Links (for sub-page crawling)
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
                self.links.append(href)

        # Headings
        if tag in ("h1", "h2", "h3", "h4"):
            self._current_heading_level = tag
            self._text_buffer = ""

        # Navigation
        if tag == "nav":
            self.nav_items.append({"type": "nav_block", "items": []})

        # Buttons / CTAs
        if tag in ("button", "a") and "class" in attrs_dict:
            cls = attrs_dict["class"].lower()
            if any(x in cls for x in ["btn", "button", "cta", "call-to-action"]):
                self._text_buffer = ""

        # Forms
        if tag == "form":
            self.current_form = {"action": attrs_dict.get("action", ""), "fields": []}
        if tag == "input" and self.current_form is not None:
            self.current_form["fields"].append({
                "type": attrs_dict.get("type", "text"),
                "name": attrs_dict.get("name", ""),
                "placeholder": attrs_dict.get("placeholder", ""),
            })

    def handle_endtag(self, tag):
        if self.current_tags and self.current_tags[-1] == tag:
            self.current_tags.pop()

        if tag in ("h1", "h2", "h3", "h4") and self._current_heading_level == tag:
            text = self._text_buffer.strip()
            if text:
                self.headings.append({"level": tag, "text": text})
            self._current_heading_level = None
            self._text_buffer = ""

        if tag == "form" and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None

    def handle_data(self, data):
        if self._current_heading_level:
            self._text_buffer += data

    def _extract_style_tokens(self, style: str):
        """Pull hex colors and font-family names from inline style strings."""
        # Hex colors
        for match in re.findall(r"#([0-9a-fA-F]{3,8})\b", style):
            self.colors_found.add(f"#{match}")
        # RGB/RGBA
        for match in re.findall(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", style):
            r, g, b = match
            self.colors_found.add(f"#{int(r):02x}{int(g):02x}{int(b):02x}")
        # font-family
        for match in re.findall(r"font-family:\s*([^;]+)", style, re.IGNORECASE):
            self.fonts_found.add(match.strip().strip("'\""))

    def _infer_image_purpose(self, src: str, alt: str, tag_stack: list) -> str:
        """Guess the purpose of an image from context clues."""
        src_lower = src.lower()
        alt_lower = alt.lower()
        combined = src_lower + " " + alt_lower

        if any(x in combined for x in ["hero", "banner", "header", "cover"]):
            return "hero"
        if any(x in combined for x in ["logo", "brand"]):
            return "logo"
        if any(x in combined for x in ["avatar", "profile", "team", "person", "author"]):
            return "avatar"
        if any(x in combined for x in ["icon", "ico"]):
            return "icon"
        if any(x in combined for x in ["bg", "background"]):
            return "background"
        if any(x in combined for x in ["feature", "product", "screenshot"]):
            return "feature"
        if any(x in combined for x in ["testimonial", "review", "client"]):
            return "testimonial"
        # Fall back to position heuristic
        if "section" in tag_stack[:3]:
            return "section-image"
        return "content"


# ──────────────────────────────────────────────────────────────────────────────
# CSS / Style-sheet analyzer
# ──────────────────────────────────────────────────────────────────────────────

def extract_from_css(css_text: str) -> dict:
    """Extract colors, fonts, breakpoints, and animation hints from CSS."""
    result = {
        "colors": set(),
        "fonts": set(),
        "breakpoints": set(),
        "animations": [],
        "custom_properties": {},
    }

    # Hex colors
    for m in re.findall(r"#([0-9a-fA-F]{3,8})\b", css_text):
        result["colors"].add(f"#{m}")

    # RGB / RGBA
    for m in re.findall(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", css_text):
        r, g, b = m
        result["colors"].add(f"#{int(r):02x}{int(g):02x}{int(b):02x}")

    # font-family
    for m in re.findall(r"font-family:\s*([^;{}]+)", css_text, re.IGNORECASE):
        for f in m.split(","):
            result["fonts"].add(f.strip().strip("'\""))

    # Media query breakpoints
    for m in re.findall(r"@media[^{]+\((?:max|min)-width:\s*(\d+)px\)", css_text):
        result["breakpoints"].add(int(m))

    # CSS custom properties
    for m in re.findall(r"(-{2}[\w-]+):\s*([^;}\n]+)", css_text):
        key, value = m
        result["custom_properties"][key.strip()] = value.strip()

    # Animation / keyframe hints
    if "@keyframes" in css_text:
        for m in re.findall(r"@keyframes\s+([\w-]+)", css_text):
            result["animations"].append(m)

    result["colors"] = list(result["colors"])
    result["fonts"] = list(result["fonts"])
    result["breakpoints"] = sorted(result["breakpoints"])
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Fetcher
# ──────────────────────────────────────────────────────────────────────────────

def fetch_html(source: str) -> tuple[str, str]:
    """
    Returns (html_content, base_url).
    source is either a URL or a local file path.
    """
    if source.startswith("http://") or source.startswith("https://"):
        req = urllib.request.Request(
            source,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        return html, source
    else:
        path = Path(source)
        html = path.read_text(encoding="utf-8", errors="replace")
        return html, path.as_uri()


def resolve_url(base: str, href: str) -> str | None:
    """Resolve a relative URL against a base URL."""
    try:
        return urllib.parse.urljoin(base, href)
    except Exception:
        return None


def crawl_subpages(base_url: str, links: list[str], max_pages: int = 5) -> list[dict]:
    """Fetch up to max_pages sub-pages reachable from the collected links."""
    parsed_base = urllib.parse.urlparse(base_url)
    same_origin = lambda u: urllib.parse.urlparse(u).netloc == parsed_base.netloc

    visited = {base_url}
    pages = []
    queue = []

    for link in links:
        resolved = resolve_url(base_url, link)
        if resolved and same_origin(resolved) and resolved not in visited:
            queue.append(resolved)
            visited.add(resolved)

    for url in queue[:max_pages]:
        try:
            html, _ = fetch_html(url)
            pages.append({"url": url, "html_length": len(html)})
            time.sleep(0.5)  # polite crawl delay
        except Exception as e:
            pages.append({"url": url, "error": str(e)})

    return pages


# ──────────────────────────────────────────────────────────────────────────────
# Library / framework detection
# ──────────────────────────────────────────────────────────────────────────────

def detect_libraries(html: str) -> list[str]:
    detected = []
    checks = [
        ("React", r"react(?:\.min)?\.js|__reactFiber|ReactDOM"),
        ("Vue", r"vue(?:\.min)?\.js|v-bind|v-model"),
        ("Angular", r"angular(?:\.min)?\.js|ng-app|ng-controller"),
        ("GSAP", r"gsap(?:\.min)?\.js|TweenMax|TweenLite"),
        ("AOS", r"aos\.js|data-aos="),
        ("jQuery", r"jquery(?:\.min)?\.js|\$\(document\)"),
        ("Bootstrap", r"bootstrap(?:\.min)?\.css|class=\"[^\"]*\bcol-(?:sm|md|lg|xl)\b"),
        ("Tailwind", r"tailwindcss|class=\"[^\"]*\b(?:flex|grid|text-|bg-|p-|m-)\b"),
        ("Framer Motion", r"framer-motion"),
        ("Swiper", r"swiper(?:\.min)?\.js|class=\"swiper"),
        ("Lottie", r"lottie(?:\.min)?\.js"),
    ]
    for name, pattern in checks:
        if re.search(pattern, html, re.IGNORECASE):
            detected.append(name)
    return detected


# ──────────────────────────────────────────────────────────────────────────────
# Section detector
# ──────────────────────────────────────────────────────────────────────────────

def detect_sections(html: str) -> list[str]:
    """Identify common page section types from HTML patterns."""
    sections = []
    patterns = [
        ("hero", r'id="hero"|class="[^"]*hero|<section[^>]+hero'),
        ("features", r'id="features"|class="[^"]*feature|<section[^>]+feature'),
        ("pricing", r'id="pricing"|class="[^"]*pric|<section[^>]+pric'),
        ("testimonials", r'id="testimonials"|class="[^"]*testimon|<section[^>]+testimon'),
        ("faq", r'id="faq"|class="[^"]*faq|<section[^>]+faq'),
        ("contact", r'id="contact"|class="[^"]*contact|<section[^>]+contact'),
        ("about", r'id="about"|class="[^"]*about|<section[^>]+about'),
        ("team", r'id="team"|class="[^"]*team|<section[^>]+team'),
        ("portfolio", r'id="portfolio"|class="[^"]*portfolio|work|<section[^>]+work'),
        ("blog", r'id="blog"|class="[^"]*blog|<section[^>]+blog'),
        ("cta-banner", r'class="[^"]*cta|class="[^"]*call-to-action'),
        ("footer", r"<footer"),
        ("header/nav", r"<header|<nav"),
    ]
    for name, pattern in patterns:
        if re.search(pattern, html, re.IGNORECASE):
            sections.append(name)
    return sections


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def analyze(source: str, output_dir: str):
    print(f"[analyze_site] Fetching: {source}")
    html, base_url = fetch_html(source)
    print(f"[analyze_site] Fetched {len(html):,} chars")

    # Parse HTML
    parser = SiteParser()
    parser.feed(html)

    # Extract from embedded <style> blocks
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    css_analysis = extract_from_css("\n".join(style_blocks))

    # Merge colors
    all_colors = list(set(list(parser.colors_found) + css_analysis["colors"]))
    all_fonts = list(set(list(parser.fonts_found) + css_analysis["fonts"]))

    # Libraries
    libraries = detect_libraries(html)

    # Sections
    sections = detect_sections(html)

    # Crawl sub-pages
    print(f"[analyze_site] Found {len(parser.links)} links, crawling up to 5 sub-pages...")
    subpages = crawl_subpages(base_url, parser.links, max_pages=5)

    # Assemble analysis
    analysis = {
        "source": source,
        "base_url": base_url,
        "html_length": len(html),
        "structure": {
            "sections_detected": sections,
            "libraries_detected": libraries,
            "has_animations": bool(css_analysis["animations"] or "GSAP" in libraries or "AOS" in libraries),
            "animation_names": css_analysis["animations"],
        },
        "visual_design": {
            "colors": all_colors[:30],  # top 30
            "fonts": all_fonts,
            "breakpoints": css_analysis["breakpoints"],
            "css_custom_properties": css_analysis["custom_properties"],
        },
        "content": {
            "headings": parser.headings,
            "cta_buttons": parser.cta_buttons,
            "forms": parser.forms,
            "nav_links": list(set(parser.links))[:20],
        },
        "images": parser.images,
        "subpages_crawled": subpages,
        "class_name_sample": list(set(parser.class_names))[:50],
    }

    # Save
    out_path = Path(output_dir) / "analysis" / "site_analysis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False))
    print(f"[analyze_site] Saved analysis → {out_path}")

    # Print summary
    print(f"\n── Analysis Summary ──────────────────────────────────")
    print(f"  Sections:    {', '.join(sections) or 'none detected'}")
    print(f"  Libraries:   {', '.join(libraries) or 'none detected'}")
    print(f"  Colors:      {len(all_colors)} extracted")
    print(f"  Fonts:       {', '.join(all_fonts[:5]) or 'none'}")
    print(f"  Images:      {len(parser.images)}")
    print(f"  Headings:    {len(parser.headings)}")
    print(f"  Breakpoints: {css_analysis['breakpoints']}")
    print(f"  Sub-pages:   {len(subpages)}")
    print(f"──────────────────────────────────────────────────────\n")

    return analysis


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze_site.py <url_or_file> <output_dir>")
        sys.exit(1)
    analyze(sys.argv[1], sys.argv[2])
