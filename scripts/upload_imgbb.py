#!/usr/bin/env python3
"""
upload_imgbb.py — Standalone imgbb uploader

Upload a local file or a remote URL to imgbb for permanent hosting.

Usage:
    python upload_imgbb.py <file_path_or_url> [--name <name>]

Environment:
    IMGBB_API_KEY — required

Outputs the permanent imgbb URL to stdout.
"""

import sys
import os
import base64
import json
import urllib.request
import urllib.parse
import argparse
from pathlib import Path


IMGBB_API = "https://api.imgbb.com/1/upload"


def upload_file(source: str, name: str, api_key: str) -> dict:
    """Upload a local file or remote URL to imgbb. Returns the full API response data."""
    if source.startswith("http://") or source.startswith("https://"):
        print(f"[imgbb] Downloading {source}...")
        with urllib.request.urlopen(source, timeout=30) as resp:
            image_bytes = resp.read()
    else:
        image_bytes = Path(source).read_bytes()

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    form_data = urllib.parse.urlencode({
        "key": api_key,
        "image": image_b64,
        "name": name or Path(source).stem,
    }).encode("utf-8")

    req = urllib.request.Request(IMGBB_API, data=form_data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())

    if not result.get("success"):
        raise RuntimeError(f"imgbb upload failed: {result}")

    return result["data"]


def main():
    parser = argparse.ArgumentParser(description="Upload image to imgbb")
    parser.add_argument("source", help="Local file path or remote URL")
    parser.add_argument("--name", default="", help="Optional name for the image")
    args = parser.parse_args()

    api_key = os.environ.get("IMGBB_API_KEY", "")
    if not api_key:
        print("[ERROR] IMGBB_API_KEY environment variable not set.")
        sys.exit(1)

    data = upload_file(args.source, args.name, api_key)

    print(f"URL:        {data['url']}")
    print(f"Display:    {data['display_url']}")
    print(f"Delete URL: {data['delete_url']}")
    print(f"Size:       {data.get('size', 'unknown')} bytes")
    print(f"ID:         {data['id']}")


if __name__ == "__main__":
    main()
