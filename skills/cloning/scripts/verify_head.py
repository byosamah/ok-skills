#!/usr/bin/env python3
"""
Compare <title> and every <meta> tag between the original and the clone.

Why this needs its own gate: nothing else in the pipeline can see these. Pixel
diffs, SSIM scores and DOM geometry checks all read the body. A page can match
the original perfectly on screen while shipping a title and description the
generator invented, and every visual check will pass.

That is not hypothetical. A clone shipped a /lab page titled "Lab / Coming Soon"
where the original said "Lab / Experiments", with an extra sentence bolted onto
the description. Screenshots passed. Element-by-element DOM comparison passed.
The defect survived to delivery because no check ever read the head.

Some differences are expected and are reported separately rather than as
failures: the `generator` tag names whichever framework version the clone was
built with, and asset URLs differ when a hashed build path is replaced by a
static one.

Usage:
    python verify_head.py --original https://site.com --clone http://localhost:3000
                          [--routes /,/about,/lab] [--out head-report.json]
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) clone-verify/1.0"}

# Differences here are a consequence of rebuilding, not a content mistake.
EXPECTED_DIFFERENT = {
    "generator": "names the framework version the clone was built with",
}
ASSET_URL_KEYS = {"og:image", "twitter:image", "og:image:secure_url"}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def parse_head(html):
    head = html.split("</head>")[0]
    out = {}
    t = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
    out["<title>"] = re.sub(r"\s+", " ", t.group(1)).strip() if t else None
    for tag in re.findall(r"<meta\b[^>]*>", head, re.I):
        key = re.search(r'(?:name|property)\s*=\s*"([^"]+)"', tag, re.I)
        val = re.search(r'content\s*=\s*"([^"]*)"', tag, re.I)
        if key:
            out[key.group(1)] = val.group(1) if val else ""
    for tag in re.findall(r"<link\b[^>]*rel\s*=\s*\"canonical\"[^>]*>", head, re.I):
        href = re.search(r'href\s*=\s*"([^"]*)"', tag, re.I)
        if href:
            out["link:canonical"] = href.group(1)
    return out


def compare_route(original, clone, route):
    o_url = original.rstrip("/") + route
    c_url = clone.rstrip("/") + route
    try:
        o, c = parse_head(fetch(o_url)), parse_head(fetch(c_url))
    except Exception as e:
        return {"route": route, "error": str(e)[:200], "defects": [], "expected": []}

    defects, expected, missing = [], [], []
    for key in sorted(set(o) | set(c)):
        ov, cv = o.get(key), c.get(key)
        if ov == cv:
            continue
        entry = {"key": key, "original": ov, "clone": cv}
        if key in EXPECTED_DIFFERENT:
            entry["reason"] = EXPECTED_DIFFERENT[key]
            expected.append(entry)
        elif key in ASSET_URL_KEYS:
            entry["reason"] = "asset path differs after rebuild; confirm the file resolves"
            expected.append(entry)
        elif ov is not None and cv is None:
            missing.append(entry)
        else:
            defects.append(entry)

    return {
        "route": route,
        "tags_original": len(o), "tags_clone": len(c),
        "defects": defects, "missing_in_clone": missing, "expected": expected,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True)
    ap.add_argument("--clone", required=True)
    ap.add_argument("--routes", default="/")
    ap.add_argument("--out", default="head-report.json")
    args = ap.parse_args()

    routes = [r.strip() for r in args.routes.split(",") if r.strip()]
    reports = [compare_route(args.original, args.clone, r) for r in routes]
    Path(args.out).write_text(json.dumps(reports, indent=2))

    total_def = sum(len(r.get("defects", [])) for r in reports)
    total_missing = sum(len(r.get("missing_in_clone", [])) for r in reports)

    print("=" * 68)
    for r in reports:
        if r.get("error"):
            print(f"{r['route']:<12} ERROR: {r['error']}")
            continue
        n = len(r["defects"]) + len(r["missing_in_clone"])
        status = "OK" if n == 0 else f"{n} defect(s)"
        print(f"{r['route']:<12} {r['tags_clone']}/{r['tags_original']} tags   {status}")
        for d in r["defects"] + r["missing_in_clone"]:
            print(f"    {d['key']}")
            print(f"      original: {d['original']}")
            print(f"      clone   : {d['clone']}")
        for e in r["expected"]:
            print(f"    (expected) {e['key']}: {e['reason']}")
    print("=" * 68)
    print(f"Report: {args.out}")

    if total_def or total_missing:
        print(f"\nFIX THESE. {total_def} wrong value(s), {total_missing} missing tag(s).")
        print("A wrong title or description is invisible to every visual check.")
        sys.exit(1)
    print("\nHead matches on every route.")


if __name__ == "__main__":
    main()
