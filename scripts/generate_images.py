#!/usr/bin/env python3
"""
generate_images.py  -  Phase 3 of /launch-website

Generates images via Kie AI (flux-kontext-pro model), polls for completion,
then uploads each result to imgbb for permanent hosting.

Usage:
    python generate_images.py <manifest_input_json> <output_dir>

Input JSON format (list of image tasks):
    [
      {
        "id": "hero-1",
        "prompt": "Detailed generation prompt...",
        "aspect_ratio": "16:9",
        "purpose": "hero"
      },
      ...
    ]

Environment variables required:
    KIE_AI_API_KEY    -  from https://kie.ai
    IMGBB_API_KEY     -  from https://api.imgbb.com

Output:
    <output_dir>/assets/images/manifest.json    -  updated with imgbb URLs
    <output_dir>/assets/images/pending-generation.md   -  failed prompts
"""

import sys
import os
import json
import time
import base64
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------

KIE_API_BASE = "https://api.kie.ai/api/v1"
KIE_POLL_INTERVAL = 5   # seconds between polls
KIE_MAX_POLLS = 60      # 5 minutes max

ASPECT_RATIO_MAP = {
    "hero": "16:9",
    "banner": "16:9",
    "avatar": "1:1",
    "square": "1:1",
    "thumbnail": "1:1",
    "portrait": "3:4",
    "card": "3:4",
    "cinematic": "21:9",
    "wide": "21:9",
    "mobile-bg": "9:16",
    "background": "9:16",
}

IMGBB_API_BASE = "https://api.imgbb.com/1/upload"


# ------------------------------------------------------------------------------
# Kie AI
# ------------------------------------------------------------------------------

def kie_generate(prompt: str, aspect_ratio: str, api_key: str) -> str:
    """
    Submit a generation request to Kie AI.
    Returns the task_id.
    """
    payload = json.dumps({
        "model": "flux-kontext-pro",
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": "jpeg",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{KIE_API_BASE}/image/generate",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    if data.get("code") != 200:
        raise RuntimeError(f"Kie AI generate error: {data}")

    task_id = data["data"]["task_id"]
    print(f"  [kie] Submitted task: {task_id}")
    return task_id


def kie_poll(task_id: str, api_key: str) -> str:
    """
    Poll until the Kie AI task completes.
    Returns the image URL.
    """
    url = f"{KIE_API_BASE}/image/task/{task_id}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
    )

    for attempt in range(KIE_MAX_POLLS):
        time.sleep(KIE_POLL_INTERVAL)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())

        status = data.get("data", {}).get("status", "")
        print(f"  [kie] Poll {attempt + 1}/{KIE_MAX_POLLS}  -  status: {status}")

        if status == "completed":
            image_url = data["data"]["output"][0]["url"]
            print(f"  [kie] Complete -> {image_url}")
            return image_url

        if status in ("failed", "error"):
            raise RuntimeError(f"Kie AI task failed: {data}")

    raise TimeoutError(f"Kie AI task {task_id} did not complete after {KIE_MAX_POLLS} polls")


# ------------------------------------------------------------------------------
# imgbb uploader
# ------------------------------------------------------------------------------

def imgbb_upload_from_url(image_url: str, name: str, api_key: str) -> str:
    """
    Download image from image_url, upload to imgbb, return permanent URL.
    imgbb free tier stores images permanently by default.
    """
    # Download the image bytes
    print(f"  [imgbb] Downloading image...")
    with urllib.request.urlopen(image_url, timeout=30) as resp:
        image_bytes = resp.read()

    # Base64-encode
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Upload to imgbb
    data = urllib.parse.urlencode({
        "key": api_key,
        "image": image_b64,
        "name": name,
    }).encode("utf-8")

    req = urllib.request.Request(IMGBB_API_BASE, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())

    if not result.get("success"):
        raise RuntimeError(f"imgbb upload failed: {result}")

    permanent_url = result["data"]["url"]
    print(f"  [imgbb] Permanent URL -> {permanent_url}")
    return permanent_url


# ------------------------------------------------------------------------------
# Gradient placeholder
# ------------------------------------------------------------------------------

def css_gradient_placeholder(purpose: str, colors: list[str] | None = None) -> str:
    """Generate a CSS gradient that can stand in for a failed image."""
    fallback_colors = {
        "hero": ("linear-gradient", "#1a1a2e", "#16213e", "#0f3460"),
        "avatar": ("radial-gradient", "#e0e0e0", "#bdbdbd"),
        "feature": ("linear-gradient", "#f5f7fa", "#c3cfe2"),
        "background": ("linear-gradient", "#0f0c29", "#302b63", "#24243e"),
        "icon": ("linear-gradient", "#f093fb", "#f5576c"),
        "testimonial": ("linear-gradient", "#a8edea", "#fed6e3"),
    }
    grad_type, *grad_colors = fallback_colors.get(purpose, ("linear-gradient", "#667eea", "#764ba2"))
    if colors and len(colors) >= 2:
        grad_colors = colors[:3]
    stops = ", ".join(grad_colors)
    return f"background: {grad_type}(135deg, {stops}); width: 100%; height: 100%;"


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def generate_all(tasks_file: str, output_dir: str):
    kie_key = os.environ.get("KIE_AI_API_KEY", "")
    imgbb_key = os.environ.get("IMGBB_API_KEY", "")

    if not kie_key:
        print("[ERROR] KIE_AI_API_KEY environment variable not set.")
        sys.exit(1)
    if not imgbb_key:
        print("[ERROR] IMGBB_API_KEY environment variable not set.")
        sys.exit(1)

    tasks = json.loads(Path(tasks_file).read_text())
    out_images = Path(output_dir) / "assets" / "images"
    out_images.mkdir(parents=True, exist_ok=True)

    manifest = []
    pending = []

    for i, task in enumerate(tasks):
        task_id_str = task.get("id", f"image-{i}")
        prompt = task.get("prompt", "")
        purpose = task.get("purpose", "content")
        ratio = task.get("aspect_ratio") or ASPECT_RATIO_MAP.get(purpose, "16:9")

        print(f"\n[{i+1}/{len(tasks)}] Generating: {task_id_str}")
        print(f"  Purpose: {purpose} | Ratio: {ratio}")
        print(f"  Prompt: {prompt[:100]}...")

        try:
            kie_task_id = kie_generate(prompt, ratio, kie_key)
            image_url = kie_poll(kie_task_id, kie_key)
            permanent_url = imgbb_upload_from_url(image_url, task_id_str, imgbb_key)

            manifest.append({
                "id": task_id_str,
                "purpose": purpose,
                "aspect_ratio": ratio,
                "prompt": prompt,
                "kie_task_id": kie_task_id,
                "imgbb_url": permanent_url,
                "status": "generated",
            })

        except Exception as e:
            print(f"  [FAIL] {e}")
            placeholder_css = css_gradient_placeholder(purpose)
            manifest.append({
                "id": task_id_str,
                "purpose": purpose,
                "aspect_ratio": ratio,
                "prompt": prompt,
                "status": "failed",
                "error": str(e),
                "placeholder_css": placeholder_css,
            })
            pending.append({
                "id": task_id_str,
                "prompt": prompt,
                "error": str(e),
            })

    # Save manifest
    manifest_path = out_images / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n[generate_images] Manifest saved -> {manifest_path}")

    # Save pending
    if pending:
        lines = ["# Pending Image Generation\n",
                 "These images failed to generate and need manual retry.\n\n"]
        for p in pending:
            lines.append(f"## {p['id']}\n")
            lines.append(f"**Error:** {p['error']}\n\n")
            lines.append(f"**Prompt:**\n```\n{p['prompt']}\n```\n\n")
        pending_path = out_images / "pending-generation.md"
        pending_path.write_text("".join(lines))
        print(f"[generate_images] Pending prompts -> {pending_path}")

    # Summary
    generated = sum(1 for m in manifest if m["status"] == "generated")
    failed = len(manifest) - generated
    print(f"\n-- Image Generation Summary --------------------------")
    print(f"  [ok] Generated: {generated}")
    print(f"  [x] Failed:    {failed}")
    print(f"------------------------------------------------------\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_images.py <tasks.json> <output_dir>")
        sys.exit(1)
    generate_all(sys.argv[1], sys.argv[2])
