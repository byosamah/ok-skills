#!/usr/bin/env python3
"""
Website Design Extraction (thin wrapper around the cloning skill's orchestrator).

Runs Playwright deep-extraction on a URL and returns:
  - Path to the extraction directory (with screenshots/, extraction/, assets/)
  - A list of candidate subpage URLs (from nav, footer, primary content) so the
    invoking agent can ask the user which ones to also extract.

The actual extraction is delegated to:
  /Users/osamakhalil/.claude/skills/cloning/scripts/clone_orchestrator.py

That orchestrator already runs every JS extraction script we need (design tokens,
fonts, components, layout, animations, measurements, SVGs). We do NOT reimplement
that pipeline. We only orchestrate it for the DESIGN.md use case.

Usage:
    python extract.py <url> [<output_dir>] [--no-video] [--include-subpages url1,url2,...]

Returns (stdout, JSON):
    {
      "ok": true,
      "extraction_dir": "~/Desktop/designmd-ripper/<host>-<ts>",
      "primary_url": "https://...",
      "candidate_subpages": [
        {"url": "...", "label": "Pricing", "where": "nav"},
        ...
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

CLONING_ORCHESTRATOR = Path(
    "/Users/osamakhalil/.claude/skills/cloning/scripts/clone_orchestrator.py"
)


def slugify_host(url: str) -> str:
    host = urlparse(url).hostname or "site"
    return re.sub(r"[^a-z0-9.-]+", "-", host.lower()).strip("-") or "site"


def run_orchestrator(url: str, out_dir: Path, record_video: bool) -> int:
    if not CLONING_ORCHESTRATOR.exists():
        sys.stderr.write(
            f"Cloning orchestrator not found at {CLONING_ORCHESTRATOR}.\n"
            "Install or symlink the `cloning` skill before running designmd-ripper.\n"
        )
        return 2

    cmd = [sys.executable, str(CLONING_ORCHESTRATOR), url, str(out_dir)]
    if not record_video:
        cmd.append("--no-video")

    # Stream output so user sees progress. Inherit stdout/stderr.
    proc = subprocess.run(cmd)
    return proc.returncode


def collect_candidate_subpages(extraction_dir: Path, base_url: str) -> list[dict[str, str]]:
    """Read components extraction JSON and surface nav/footer link candidates."""
    components_path = extraction_dir / "extraction" / "components.json"
    if not components_path.exists():
        return []

    try:
        data = json.loads(components_path.read_text())
    except Exception:
        return []

    base_host = urlparse(base_url).hostname or ""
    seen: set[str] = set()
    candidates: list[dict[str, str]] = []

    def consider(raw_href: str | None, label: str, where: str) -> None:
        if not raw_href:
            return
        href = raw_href.strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            return
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            return
        if parsed.hostname and parsed.hostname != base_host:
            return
        # Strip query/fragment for de-duplication; keep path as the canonical key.
        canonical = parsed._replace(fragment="", query="").geturl().rstrip("/")
        if canonical == base_url.rstrip("/"):
            return
        if canonical in seen:
            return
        seen.add(canonical)
        candidates.append(
            {"url": canonical, "label": label.strip()[:80] or canonical, "where": where}
        )

    nav = data.get("navigation") or {}
    # analyze_components.js shape: navigation.primary = {selector, linkCount, links:[{text,href,hasDropdown}], hasLogo, hasMobileToggle}
    primary_nav = nav.get("primary") if isinstance(nav, dict) else None
    if isinstance(primary_nav, dict):
        for link in primary_nav.get("links") or []:
            if isinstance(link, dict):
                consider(link.get("href"), link.get("text", ""), "nav")

    # secondary is initialized as [] in the JS extractor and rarely populated, but be tolerant of
    # either shape (array of nav-shaped objects, or a single nav-shaped object).
    secondary = nav.get("secondary") if isinstance(nav, dict) else None
    if isinstance(secondary, dict):
        for link in secondary.get("links") or []:
            if isinstance(link, dict):
                consider(link.get("href"), link.get("text", ""), "secondary-nav")
    elif isinstance(secondary, list):
        for sec in secondary:
            if isinstance(sec, dict):
                for link in sec.get("links") or sec.get("items") or []:
                    if isinstance(link, dict):
                        consider(link.get("href"), link.get("text", ""), "secondary-nav")

    interactive = data.get("interactiveElements") or {}
    for link in interactive.get("links") or []:
        if isinstance(link, dict):
            consider(link.get("href"), link.get("text", ""), "page-link")

    # Cap at 20 to keep the approval list reviewable.
    return candidates[:20]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL to extract")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Output directory (default: ~/Desktop/designmd-ripper/<host>-<ts>)",
    )
    parser.add_argument("--no-video", action="store_true", help="Skip video recording (faster)")
    parser.add_argument(
        "--include-subpages",
        default="",
        help="Comma-separated subpage URLs to also extract after the primary URL.",
    )
    args = parser.parse_args()

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else Path.home() / "Desktop" / "designmd-ripper" / f"{slugify_host(args.url)}-{timestamp}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    primary_dir = out_dir / "primary"
    primary_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[extract] Primary URL: {args.url}", flush=True)
    print(f"[extract] Output dir: {out_dir}", flush=True)

    rc = run_orchestrator(args.url, primary_dir, record_video=not args.no_video)
    if rc != 0:
        print(json.dumps({"ok": False, "error": f"orchestrator exited {rc}"}, indent=2))
        return rc

    candidates = collect_candidate_subpages(primary_dir, args.url)

    extra_dirs: list[dict[str, Any]] = []
    if args.include_subpages:
        for sub_url in [u.strip() for u in args.include_subpages.split(",") if u.strip()]:
            sub_dir = out_dir / ("sub-" + slugify_host(sub_url) + "-" + str(len(extra_dirs)))
            sub_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n[extract] Subpage: {sub_url}", flush=True)
            sub_rc = run_orchestrator(sub_url, sub_dir, record_video=False)
            extra_dirs.append({"url": sub_url, "dir": str(sub_dir), "ok": sub_rc == 0})

    result = {
        "ok": True,
        "extraction_dir": str(out_dir),
        "primary_dir": str(primary_dir),
        "primary_url": args.url,
        "candidate_subpages": candidates,
        "extracted_subpages": extra_dirs,
    }
    # Also dump to disk so the calling agent can read it back later.
    (out_dir / "extract-summary.json").write_text(json.dumps(result, indent=2))
    print("\n[extract] Summary:")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
