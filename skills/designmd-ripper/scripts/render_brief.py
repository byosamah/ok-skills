#!/usr/bin/env python3
"""
Render a synthesis brief from a cloning-orchestrator extraction directory.

This script does NOT synthesize the DESIGN.md itself — that is the agent's
job, because mapping raw signal to spec-correct tokens is a judgment call
(naming, clustering, role assignment). This script normalizes the noisy
JSON outputs into a compact, readable brief that the agent can read once
and then use as the source of truth while writing DESIGN.md.

Usage:
    python render_brief.py <extraction_dir> [--out brief.md]

Where <extraction_dir> is the parent dir produced by extract.py (contains
primary/extraction/*.json + sub-* siblings).

Output is a markdown file with:
  - URL + page title
  - Brand-critical colors (high confidence) with hex + role hints
  - Secondary colors (medium confidence)
  - Typography clusters (font families, distinct size/weight combos)
  - Font manifest (face URLs)
  - Spacing scale + page padding
  - Shadows, radii, gradients
  - Detected components / landmarks / navigation
  - Layout signals (breakpoints, grid/flex usage)
  - Screenshot paths for the agent to view

The brief is the input the agent reads alongside `references/spec.md`
and `references/synthesis-guide.md` to write DESIGN.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_error": f"failed to parse {path.name}: {exc}"}


def rgb_to_hex(rgb: str | None) -> str | None:
    if not rgb:
        return None
    rgb = rgb.strip()
    if rgb.startswith("#"):
        return rgb.upper()
    # rgb(r, g, b) / rgba(r, g, b, a)
    import re

    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", rgb)
    if not m:
        return rgb  # keyword like "transparent" — let the agent decide
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def unique_preserve_order(seq: list[Any]) -> list[Any]:
    seen: set[str] = set()
    out: list[Any] = []
    for item in seq:
        key = json.dumps(item, sort_keys=True) if not isinstance(item, str) else item
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def render_colors(tokens: dict | None) -> str:
    if not tokens or not isinstance(tokens, dict):
        return "_No design tokens extracted._"
    colors = tokens.get("colors") or {}
    sections: list[str] = []
    total_extracted = 0
    for bucket, label in (
        ("high", "Brand-critical (high confidence)"),
        ("medium", "Interactive / secondary (medium confidence)"),
        ("low", "Generic UI (low confidence — usually skip)"),
    ):
        items = colors.get(bucket) or []
        if not items:
            continue
        rows: list[str] = []
        seen_hex: set[str] = set()
        for entry in items:
            if isinstance(entry, dict):
                value = entry.get("hex") or entry.get("value") or entry.get("color")
                role_bits = [
                    entry.get("property"),
                    entry.get("role"),
                    entry.get("context"),
                    entry.get("selector"),
                ]
                count = entry.get("count")
                role = " · ".join(b for b in role_bits if b)
                if count:
                    role = f"{role} ({count}×)" if role else f"({count}×)"
            else:
                value, role = str(entry), ""
            hex_val = rgb_to_hex(value) or (str(value) if value else None)
            if not hex_val or hex_val in seen_hex:
                continue
            seen_hex.add(hex_val)
            role_text = f" — used as {role}" if role else ""
            rows.append(f"- `{hex_val}`{role_text}")
        if rows:
            total_extracted += len(rows)
            sections.append(f"### {label}\n\n" + "\n".join(rows[:25]))
    if sections:
        return "\n\n".join(sections)
    return (
        "_No authored colors were extracted from CSS. The site likely uses_\n"
        "_user-agent defaults (rare) or has CSS that the tokens extractor_\n"
        "_could not classify. **Inspect the screenshots listed at the bottom**_\n"
        "_**of this brief and derive the palette visually.** Even a 2-color_\n"
        "_palette is fine — pick `primary` and `on-primary` from the most_\n"
        "_prominent text/background pair, then build out from there._"
    )


def render_typography(tokens: dict | None, fonts: dict | None) -> str:
    parts: list[str] = []
    if tokens and isinstance(tokens, dict):
        typo = tokens.get("typography") or {}
        families = unique_preserve_order(typo.get("fontFamilies") or [])
        sizes = unique_preserve_order(typo.get("fontSizes") or [])
        weights = unique_preserve_order(typo.get("fontWeights") or [])
        line_heights = unique_preserve_order(typo.get("lineHeights") or [])
        letter_spacings = unique_preserve_order(typo.get("letterSpacings") or [])
        primary = typo.get("primary")
        heading = typo.get("heading")
        accent = typo.get("accent")
        parts.append(
            "### Role hints from extractor\n\n"
            f"- Primary (body) font: `{primary or 'unknown'}`\n"
            f"- Heading font: `{heading or 'unknown'}`\n"
            f"- Accent font: `{accent or 'unknown'}`"
        )
        if families:
            parts.append("### Font families observed\n\n" + "\n".join(f"- `{f}`" for f in families[:10]))
        if sizes:
            parts.append("### Font sizes observed\n\n" + ", ".join(f"`{s}`" for s in sizes[:30]))
        if weights:
            parts.append("### Font weights observed\n\n" + ", ".join(f"`{w}`" for w in weights[:15]))
        if line_heights:
            parts.append("### Line heights observed\n\n" + ", ".join(f"`{lh}`" for lh in line_heights[:15]))
        if letter_spacings:
            parts.append("### Letter spacings observed\n\n" + ", ".join(f"`{ls}`" for ls in letter_spacings[:15]))
    if fonts and isinstance(fonts, dict):
        faces = fonts.get("fontFaces") or []
        if faces:
            rows = []
            for face in faces[:20]:
                if not isinstance(face, dict):
                    continue
                family = face.get("family") or "?"
                weight = face.get("weight") or ""
                src = ""
                sources = face.get("src") or []
                if sources and isinstance(sources[0], dict):
                    src = sources[0].get("url") or ""
                rows.append(f"- **{family}** weight `{weight}` — `{src}`")
            if rows:
                parts.append("### @font-face declarations\n\n" + "\n".join(rows))
    return "\n\n".join(parts) if parts else "_No typography extracted._"


def render_spacing(tokens: dict | None) -> str:
    if not tokens:
        return "_No spacing extracted._"
    spacing = tokens.get("spacing") or {}
    scale = unique_preserve_order(spacing.get("scale") or [])
    section_gaps = unique_preserve_order(spacing.get("sectionGaps") or [])
    component_gaps = unique_preserve_order(spacing.get("componentGaps") or [])
    page_padding = spacing.get("pagePadding")
    parts = []
    if scale:
        parts.append("### Spacing scale observed\n\n" + ", ".join(f"`{v}`" for v in scale[:30]))
    if page_padding:
        parts.append(f"### Page padding\n\n`{page_padding}`")
    if section_gaps:
        parts.append("### Gaps between page sections\n\n" + ", ".join(f"`{v}`" for v in section_gaps[:15]))
    if component_gaps:
        parts.append("### Gaps within components\n\n" + ", ".join(f"`{v}`" for v in component_gaps[:15]))
    return "\n\n".join(parts) if parts else "_No spacing extracted._"


def render_shapes(tokens: dict | None) -> str:
    if not tokens:
        return "_No shape data extracted._"
    radii = unique_preserve_order(tokens.get("borderRadius") or [])
    if not radii:
        return "_No border radii extracted._"
    return "### Border radii observed\n\n" + ", ".join(f"`{v}`" for v in radii[:20])


def render_elevation(tokens: dict | None) -> str:
    if not tokens:
        return "_No elevation data extracted._"
    shadows = unique_preserve_order(tokens.get("shadows") or [])
    if not shadows:
        return "_No shadows observed — site likely uses flat hierarchy (borders / tonal layers)._"
    rows = []
    for shadow in shadows[:10]:
        rows.append(f"- `{shadow}`")
    return "### Shadows observed\n\n" + "\n".join(rows)


def render_layout(layout: dict | None) -> str:
    if not layout:
        return "_No layout data extracted._"
    parts = []
    page = layout.get("pageStructure") or {}
    if page.get("maxWidth"):
        parts.append(f"- Max content width: `{page['maxWidth']}`")
    if page.get("pagePadding"):
        parts.append(f"- Page edge padding: `{page['pagePadding']}`")
    breakpoints = unique_preserve_order(layout.get("breakpoints") or [])
    if breakpoints:
        parts.append("- Breakpoints: " + ", ".join(f"`{b}`" for b in breakpoints[:10]))
    method = layout.get("layoutMethod") or {}
    grid_count = len(method.get("grid") or [])
    flex_count = len(method.get("flexbox") or [])
    if grid_count or flex_count:
        parts.append(f"- Layout primitives in use: `{flex_count}` flex containers, `{grid_count}` grid containers")
    return "\n".join(parts) if parts else "_No layout signals._"


def render_components(components: dict | None) -> str:
    if not components:
        return "_No component data extracted._"
    parts = []
    landmarks = components.get("landmarks") or []
    if landmarks:
        names = Counter(lm.get("role") or lm.get("tag") for lm in landmarks if isinstance(lm, dict))
        parts.append("### Landmarks present\n\n" + ", ".join(f"`{n}`×{c}" for n, c in names.most_common()))
    nav = components.get("navigation") or {}
    primary_nav = nav.get("primary")
    if primary_nav and isinstance(primary_nav, dict):
        links = primary_nav.get("links") or primary_nav.get("items") or []
        if links:
            rows = [f"- `{i.get('text','?')}` → `{i.get('href','?')}`" for i in links[:15] if isinstance(i, dict)]
            parts.append("### Primary navigation\n\n" + "\n".join(rows))
    interactive = components.get("interactiveElements") or {}
    button_count = len(interactive.get("buttons") or [])
    link_count = len(interactive.get("links") or [])
    form_count = len(interactive.get("forms") or [])
    if button_count or link_count or form_count:
        parts.append(
            "### Interactive elements\n\n"
            f"- Buttons: `{button_count}`\n"
            f"- Links: `{link_count}`\n"
            f"- Forms: `{form_count}`"
        )
    sections = components.get("sections") or []
    if sections:
        rows = []
        for sec in sections[:15]:
            if not isinstance(sec, dict):
                continue
            rows.append(f"- `{sec.get('selector','?')}` ({sec.get('purpose') or 'section'})")
        if rows:
            parts.append("### Page sections detected\n\n" + "\n".join(rows))
    return "\n\n".join(parts) if parts else "_No components detected._"


def list_screenshots(extraction_root: Path) -> list[str]:
    shots: list[str] = []
    for shot in sorted((extraction_root / "screenshots").glob("*.png")):
        shots.append(str(shot))
    for shot in sorted((extraction_root / "screenshots" / "sections").glob("*.png")):
        shots.append(str(shot))
    return shots[:20]


def render_brief(extraction_dir: Path, primary_url: str) -> str:
    primary_root = extraction_dir / "primary"
    extract_root = primary_root / "extraction"

    tokens = load_json(extract_root / "design-tokens.json")
    fonts = load_json(extract_root / "fonts.json")
    layout = load_json(extract_root / "layout.json")
    components = load_json(extract_root / "components.json")

    shots = list_screenshots(primary_root)

    lines = [
        "# Synthesis Brief",
        "",
        f"**URL:** {primary_url}",
        f"**Extraction directory:** `{extraction_dir}`",
        "",
        "> This brief is the normalized output of the Playwright extraction.",
        "> Read alongside `references/spec.md`, `references/synthesis-guide.md`,",
        "> and `references/canonical-example.md`, then write DESIGN.md.",
        "",
        "## Colors",
        render_colors(tokens),
        "",
        "## Typography",
        render_typography(tokens, fonts),
        "",
        "## Spacing",
        render_spacing(tokens),
        "",
        "## Shapes (corner radii)",
        render_shapes(tokens),
        "",
        "## Elevation & Depth",
        render_elevation(tokens),
        "",
        "## Layout signals",
        render_layout(layout),
        "",
        "## Components / structure",
        render_components(components),
        "",
        "## Screenshots to inspect",
    ]
    if shots:
        lines.extend(f"- `{s}`" for s in shots)
    else:
        lines.append("_No screenshots found._")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extraction_dir", help="Directory produced by extract.py")
    parser.add_argument(
        "--out",
        default=None,
        help="Output path for the brief (default: <extraction_dir>/synthesis-brief.md)",
    )
    args = parser.parse_args()

    extraction_dir = Path(args.extraction_dir).expanduser().resolve()
    if not extraction_dir.exists():
        sys.stderr.write(f"Extraction dir not found: {extraction_dir}\n")
        return 2

    summary_path = extraction_dir / "extract-summary.json"
    primary_url = ""
    if summary_path.exists():
        try:
            primary_url = json.loads(summary_path.read_text()).get("primary_url", "")
        except Exception:
            pass

    out = Path(args.out) if args.out else extraction_dir / "synthesis-brief.md"
    out.write_text(render_brief(extraction_dir, primary_url))
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
