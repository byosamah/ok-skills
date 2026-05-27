#!/usr/bin/env python3
"""
Brand Post Generator — the beating heart of the branded-design skill.

Reads brand-kit/brand.yaml, selects reference assets, constructs prompts,
and calls nano-banana's generate_image.py to produce on-brand social posts.

Usage:
    # List available assets (inventory mode)
    python generate_post.py --brand-kit brand-kit --inventory

    # Generate a new post
    python generate_post.py \
        --brand-kit brand-kit \
        --content "Summer Sale — 50% off everything" \
        --direction "promotional post, vibrant and energetic" \
        --platform instagram_feed \
        --aspect-ratio 1:1 \
        --references "examples/promotional/sale.png,logo/logo.png" \
        --output output/summer-sale.png

    # Iterate on a previous output
    python generate_post.py \
        --brand-kit brand-kit \
        --content "Summer Sale — 50% off everything" \
        --direction "promotional post, vibrant and energetic" \
        --previous-output output/summer-sale.png \
        --tweak "make the text bigger and move the logo to top-right"
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML loader — prefers PyYAML, falls back to a minimal manual parser
# ---------------------------------------------------------------------------

try:
    import yaml

    def load_yaml(path: str) -> dict:
        """Load a YAML file using PyYAML."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

except ImportError:

    def load_yaml(path: str) -> dict:
        """
        Minimal YAML parser for simple key-value / nested-dict files.
        Handles: scalars, lists (- item), and one level of nesting.
        Does NOT handle multi-line strings or complex anchors.
        """
        data: dict = {}
        current_key = None
        current_dict = None

        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")

                # Skip blanks, comments, and YAML document markers
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
                    continue

                indent = len(line) - len(line.lstrip())

                # Nested key (indented under a parent dict key)
                if indent >= 2 and current_key is not None:
                    if ":" in stripped:
                        k, v = stripped.split(":", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if current_dict is None:
                            current_dict = {}
                            data[current_key] = current_dict
                        current_dict[k] = v
                    elif stripped.startswith("- "):
                        item = stripped[2:].strip().strip("'\"")
                        if not isinstance(data.get(current_key), list):
                            data[current_key] = []
                        data[current_key].append(item)
                    continue

                # Top-level key
                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    current_key = k
                    current_dict = None
                    if v:
                        data[k] = v
                    # If v is empty, the value may be a nested dict/list — handled above
                    continue

        return data


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
NANO_BANANA_SCRIPT = SCRIPT_DIR / ".." / ".." / "nano-banana" / "scripts" / "generate_image.py"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tiff"}

PLATFORM_DEFAULTS = {
    "instagram_feed":    {"aspect_ratio": "1:1",  "resolution": "2K"},
    "instagram_story":   {"aspect_ratio": "9:16", "resolution": "2K"},
    "instagram_reels":   {"aspect_ratio": "9:16", "resolution": "2K"},
    "tiktok":            {"aspect_ratio": "9:16", "resolution": "2K"},
    "linkedin":          {"aspect_ratio": "16:9", "resolution": "2K"},
    "twitter":           {"aspect_ratio": "16:9", "resolution": "2K"},
    "facebook":          {"aspect_ratio": "16:9", "resolution": "2K"},
    "pinterest":         {"aspect_ratio": "2:3",  "resolution": "2K"},
    "youtube_thumbnail": {"aspect_ratio": "16:9", "resolution": "2K"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_image(path: Path) -> bool:
    """Return True if the path points to a recognised image file."""
    return path.suffix.lower() in IMAGE_EXTENSIONS


def scan_assets(brand_kit: Path) -> dict:
    """
    Walk the brand-kit directory and return a categorised inventory.

    Returns:
        dict mapping category names to lists of relative path strings.
    """
    inventory = {}
    for item in sorted(brand_kit.rglob("*")):
        if not item.is_file() or not is_image(item):
            continue
        rel = item.relative_to(brand_kit)
        category = rel.parts[0] if len(rel.parts) > 1 else "root"
        inventory.setdefault(category, []).append(str(rel))
    return inventory


def load_learnings(brand_kit: Path) -> list:
    """Load learned rules from brand-kit/learnings.yaml, if it exists."""
    learnings_path = brand_kit / "learnings.yaml"
    if not learnings_path.exists():
        return []

    data = load_yaml(str(learnings_path))
    rules = data.get("rules", [])
    if isinstance(rules, list):
        return [str(r) for r in rules]
    return []


def build_prompt(brand, content, direction, platform, aspect_ratio,
                 tweak=None, learned_rules=None):
    """
    Construct the generation prompt from brand config + user input.

    When *tweak* is provided we're iterating on a previous output, so the
    prompt focuses on the edit instruction while keeping brand context.
    """
    colors = brand.get("colors", {})
    color_str = ", ".join(
        "{} {}".format(k, v) for k, v in colors.items() if v
    ) if isinstance(colors, dict) else str(colors)

    style_kw = brand.get("style_keywords", "")
    if isinstance(style_kw, list):
        style_kw = ", ".join(style_kw)

    logo_placement = brand.get("logo_placement", "top-left corner")
    tone = brand.get("tone", "")
    if isinstance(tone, list):
        tone = ", ".join(tone)

    # Base prompt
    lines = [
        "Create a {} social media post for {} ({}).".format(direction, platform, aspect_ratio),
        "",
        "Brand: {}.{}".format(
            brand.get("name", "Unknown"),
            " Tagline: {}.".format(brand.get("tagline", "")) if brand.get("tagline") else ""
        ),
        "Tone: {}. Style: {}.".format(tone, style_kw),
        "Colors: {}.".format(color_str),
        "",
        'Content text: "{}"'.format(content),
        "Creative direction: {}".format(direction),
        "",
        "Design instructions:",
        "- Match the visual style of the reference images exactly",
        "- Place the logo {}".format(logo_placement),
        "- Use the brand colors consistently",
        "- Keep text legible with clear visual hierarchy",
        "- The reference images define the brand aesthetic — stay within that visual system",
    ]

    # Learned rules
    if learned_rules:
        lines.append("")
        lines.append("Learned preferences from past designs:")
        for rule in learned_rules:
            lines.append("- {}".format(rule))

    # Tweak instruction (iteration mode)
    if tweak:
        lines.append("")
        lines.append("EDIT INSTRUCTION: {}".format(tweak))
        lines.append("Apply this edit to the provided previous output image while "
                      "preserving everything else about the design.")

    return "\n".join(lines)


def resolve_nano_banana():
    """Resolve the absolute path to nano-banana's generate_image.py."""
    resolved = NANO_BANANA_SCRIPT.resolve()
    if not resolved.exists():
        # Also try the environment variable override
        env_path = os.environ.get("NANO_BANANA_SCRIPT")
        if env_path:
            resolved = Path(env_path).resolve()
    if not resolved.exists():
        print("ERROR: nano-banana script not found at {}".format(resolved), file=sys.stderr)
        print("Expected relative path: ../../nano-banana/scripts/generate_image.py", file=sys.stderr)
        print("Set NANO_BANANA_SCRIPT env var to override.", file=sys.stderr)
        sys.exit(1)
    return resolved


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_inventory(brand_kit):
    """Print a JSON inventory of all image assets in the brand kit."""
    inventory = scan_assets(brand_kit)

    # Also check for brand.yaml
    brand_yaml = brand_kit / "brand.yaml"
    has_brand = brand_yaml.exists()

    result = {
        "brand_kit": str(brand_kit.resolve()),
        "brand_yaml_exists": has_brand,
        "categories": {},
        "total_assets": 0,
    }

    for cat, files in sorted(inventory.items()):
        result["categories"][cat] = {
            "count": len(files),
            "files": files,
        }
        result["total_assets"] += len(files)

    print(json.dumps(result, indent=2))


def cmd_generate(args):
    """Run the full generation pipeline."""
    brand_kit = Path(args.brand_kit).resolve()

    # ------------------------------------------------------------------
    # 1. Load brand config
    # ------------------------------------------------------------------
    brand_yaml = brand_kit / "brand.yaml"
    if not brand_yaml.exists():
        print(json.dumps({
            "success": False,
            "error": "brand.yaml not found at {}. Run validate_brand_kit.py first.".format(brand_yaml)
        }, indent=2))
        sys.exit(1)

    brand = load_yaml(str(brand_yaml))

    # ------------------------------------------------------------------
    # 2. Determine platform defaults
    # ------------------------------------------------------------------
    platform = args.platform or "instagram_feed"
    defaults = PLATFORM_DEFAULTS.get(platform, {"aspect_ratio": "1:1", "resolution": "2K"})
    aspect_ratio = args.aspect_ratio or defaults["aspect_ratio"]
    resolution = defaults["resolution"]

    # ------------------------------------------------------------------
    # 3. Collect references
    # ------------------------------------------------------------------
    references = []
    if args.references:
        for ref in args.references.split(","):
            ref = ref.strip()
            if not ref:
                continue
            ref_path = Path(ref)
            # If not absolute, treat as relative to brand_kit
            if not ref_path.is_absolute():
                ref_path = brand_kit / ref_path
            if not ref_path.exists():
                print("WARNING: Reference not found: {}".format(ref_path), file=sys.stderr)
                continue
            references.append(str(ref_path.resolve()))

    # If iterating, the previous output becomes the primary reference
    if args.previous_output:
        prev = Path(args.previous_output).resolve()
        if not prev.exists():
            print(json.dumps({
                "success": False,
                "error": "Previous output not found: {}".format(prev)
            }, indent=2))
            sys.exit(1)
        # Insert at the front so it's the primary reference
        references.insert(0, str(prev))

    # ------------------------------------------------------------------
    # 4. Load learned rules
    # ------------------------------------------------------------------
    learned_rules = load_learnings(brand_kit)

    # ------------------------------------------------------------------
    # 5. Build prompt
    # ------------------------------------------------------------------
    prompt = build_prompt(
        brand=brand,
        content=args.content,
        direction=args.direction or "",
        platform=platform,
        aspect_ratio=aspect_ratio,
        tweak=args.tweak,
        learned_rules=learned_rules,
    )

    # ------------------------------------------------------------------
    # 6. Determine output path
    # ------------------------------------------------------------------
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", args.content[:40].lower()).strip("-")
        output_dir = brand_kit / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "{}-{}.png".format(timestamp, slug)

    # ------------------------------------------------------------------
    # 7. Call nano-banana's generate_image.py
    # ------------------------------------------------------------------
    nano_banana = resolve_nano_banana()

    cmd = [
        sys.executable, str(nano_banana),
        prompt,
        "--raw",  # We build our own prompt
        "--aspect-ratio", aspect_ratio,
        "--resolution", resolution,
        "--type", "marketing",
        "--json",
        "-o", str(output_path),
    ]

    # Add each reference as a separate -i flag
    for ref in references:
        cmd.extend(["-i", ref])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for image generation
        )
    except subprocess.TimeoutExpired:
        print(json.dumps({
            "success": False,
            "error": "Image generation timed out after 600 seconds."
        }, indent=2))
        sys.exit(1)
    except FileNotFoundError as e:
        print(json.dumps({
            "success": False,
            "error": "Failed to run nano-banana script: {}".format(e)
        }, indent=2))
        sys.exit(1)

    # ------------------------------------------------------------------
    # 8. Parse result and return JSON
    # ------------------------------------------------------------------
    if result.returncode != 0:
        print(json.dumps({
            "success": False,
            "error": "nano-banana exited with code {}".format(result.returncode),
            "stderr": result.stderr.strip() if result.stderr else None,
            "stdout": result.stdout.strip() if result.stdout else None,
        }, indent=2))
        sys.exit(1)

    # nano-banana outputs JSON when --json is passed
    try:
        nb_result = json.loads(result.stdout)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract useful info from stdout
        nb_result = {
            "success": output_path.exists(),
            "path": str(output_path) if output_path.exists() else None,
            "raw_output": result.stdout.strip(),
        }

    # Build our own enriched result
    output = {
        "success": nb_result.get("success", output_path.exists()),
        "image_path": nb_result.get("path", str(output_path)),
        "prompt_used": prompt,
        "references_used": references,
        "platform": platform,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "brand_name": brand.get("name", "Unknown"),
        "is_iteration": bool(args.previous_output),
        "tweak": args.tweak,
    }

    if nb_result.get("error"):
        output["error"] = nb_result["error"]
        output["success"] = False

    if nb_result.get("text_response"):
        output["model_notes"] = nb_result["text_response"]

    print(json.dumps(output, indent=2))

    if not output["success"]:
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate on-brand social media posts using Nano Banana 2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Inventory mode — list all brand assets
  python generate_post.py --brand-kit brand-kit --inventory

  # Generate a new post
  python generate_post.py \\
      --brand-kit brand-kit \\
      --content "Summer Sale — 50% off" \\
      --direction "promotional, vibrant" \\
      --platform instagram_feed \\
      --aspect-ratio 1:1 \\
      --references "examples/promotional/sale.png,logo/logo.png"

  # Iterate on a previous output
  python generate_post.py \\
      --brand-kit brand-kit \\
      --content "Summer Sale — 50% off" \\
      --direction "promotional, vibrant" \\
      --previous-output output/summer-sale.png \\
      --tweak "make the text bigger"
        """,
    )

    parser.add_argument(
        "--brand-kit", required=True,
        help="Path to the brand-kit directory containing brand.yaml and assets.",
    )
    parser.add_argument(
        "--inventory", action="store_true",
        help="List all available assets in the brand kit and exit.",
    )
    parser.add_argument(
        "--content",
        help="The copy/text content for the post (headline, body, CTA).",
    )
    parser.add_argument(
        "--direction",
        help="Creative direction brief (e.g. 'promotional post, warm and festive').",
    )
    parser.add_argument(
        "--platform",
        choices=list(PLATFORM_DEFAULTS.keys()),
        default="instagram_feed",
        help="Target platform (default: instagram_feed).",
    )
    parser.add_argument(
        "--aspect-ratio",
        help="Override the aspect ratio (e.g. 1:1, 9:16, 16:9). "
             "Defaults to the platform's recommended ratio.",
    )
    parser.add_argument(
        "--references",
        help="Comma-separated list of reference image paths (relative to brand-kit or absolute).",
    )
    parser.add_argument(
        "--previous-output",
        help="Path to a previous generation to iterate on.",
    )
    parser.add_argument(
        "--tweak",
        help="Edit instruction for iteration (requires --previous-output).",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path. Auto-generated if not provided.",
    )

    args = parser.parse_args()

    # Validate brand-kit path
    brand_kit = Path(args.brand_kit)
    if not brand_kit.is_dir():
        print("ERROR: Brand kit directory not found: {}".format(brand_kit), file=sys.stderr)
        sys.exit(1)

    # Inventory mode
    if args.inventory:
        cmd_inventory(brand_kit)
        return

    # Generation mode — require content
    if not args.content:
        parser.error("--content is required for generation (omit only with --inventory)")

    # Tweak requires previous output
    if args.tweak and not args.previous_output:
        parser.error("--tweak requires --previous-output")

    cmd_generate(args)


if __name__ == "__main__":
    main()
