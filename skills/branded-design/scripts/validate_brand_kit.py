#!/usr/bin/env python3
"""
Brand Kit Validator — verifies that a brand-kit/ directory is complete
and ready for the branded-design skill.

Checks:
  - brand.yaml exists and has required fields
  - Required folders have at least one asset
  - Color values are valid hex codes
  - Reports missing optional assets with friendly suggestions

Usage:
    python validate_brand_kit.py <path-to-brand-kit>
    python validate_brand_kit.py brand-kit --json   # JSON-only output
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML loader — prefers PyYAML, falls back to a minimal manual parser
# ---------------------------------------------------------------------------

try:
    import yaml

    def load_yaml(path):
        """Load a YAML file using PyYAML."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

except ImportError:

    def load_yaml(path):
        """
        Minimal YAML parser for simple key-value / nested-dict files.
        Handles: scalars, lists (- item), and one level of nesting.
        """
        data = {}
        current_key = None
        current_dict = None

        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
                    continue

                indent = len(line) - len(line.lstrip())

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

                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    current_key = k
                    current_dict = None
                    if v:
                        data[k] = v

        return data


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tiff"}

# Fields that MUST exist in brand.yaml
REQUIRED_FIELDS = ["name", "tone", "colors", "style_keywords"]

# Color sub-keys that must exist under colors
REQUIRED_COLORS = ["primary", "secondary", "accent", "background", "text"]

# Hex color pattern: #RGB, #RRGGBB, or #RRGGBBAA
HEX_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

# Folders that MUST have at least one image
REQUIRED_FOLDERS = {
    "logo": "Add at least one logo file (logo.png, logo-white.png, etc.).",
    "examples": "Add at least one example post in a subcategory folder "
                "(e.g. examples/promotional/sale.png).",
}

# Optional folders — we report suggestions, not errors
OPTIONAL_FOLDERS = {
    "backgrounds": "Background textures/patterns help Nano Banana match your brand's visual feel.",
    "photography": "Product/lifestyle photos give the model real brand imagery to reference.",
    "characters": "If your brand has a mascot or illustrated character, add them here.",
    "moodboard": "Moodboard images provide extra style context for creative direction.",
    "icons": "Brand icons and graphic elements for post compositions.",
    "fonts": "Font files (.ttf/.otf) enable exact font rendering via font_to_image.py.",
    "guidelines": "Brand guideline pages (screenshots/PDFs) help maintain consistency.",
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def count_images(directory):
    """Recursively count image files inside a directory."""
    if not directory.is_dir():
        return 0
    return sum(1 for f in directory.rglob("*") if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS)


def is_valid_hex(value):
    """Check if a string is a valid hex color code."""
    if not isinstance(value, str):
        return False
    return bool(HEX_PATTERN.match(value.strip()))


def validate(brand_kit_path):
    """
    Validate a brand-kit directory.

    Returns:
        dict with keys: valid (bool), errors (list), warnings (list),
        suggestions (list), summary (dict).
    """
    brand_kit = Path(brand_kit_path).resolve()
    errors = []
    warnings = []
    suggestions = []

    # ------------------------------------------------------------------
    # 1. Check brand-kit directory exists
    # ------------------------------------------------------------------
    if not brand_kit.is_dir():
        return {
            "valid": False,
            "errors": ["Brand kit directory not found: {}".format(brand_kit)],
            "warnings": [],
            "suggestions": [],
            "summary": {},
        }

    # ------------------------------------------------------------------
    # 2. Check brand.yaml exists and parse it
    # ------------------------------------------------------------------
    brand_yaml = brand_kit / "brand.yaml"
    brand = {}

    if not brand_yaml.exists():
        errors.append("brand.yaml not found in brand-kit directory.")
    else:
        try:
            brand = load_yaml(str(brand_yaml))
        except Exception as e:
            errors.append("Failed to parse brand.yaml: {}".format(e))

    # ------------------------------------------------------------------
    # 3. Check required fields in brand.yaml
    # ------------------------------------------------------------------
    if brand:
        for field in REQUIRED_FIELDS:
            value = brand.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append("brand.yaml: required field '{}' is missing or empty.".format(field))

        # Check colors sub-keys
        colors = brand.get("colors", {})
        if not isinstance(colors, dict):
            errors.append("brand.yaml: 'colors' must be a mapping with keys: "
                          + ", ".join(REQUIRED_COLORS))
        else:
            for color_key in REQUIRED_COLORS:
                color_val = colors.get(color_key)
                if not color_val:
                    errors.append("brand.yaml: colors.{} is missing.".format(color_key))
                elif not is_valid_hex(color_val):
                    errors.append(
                        "brand.yaml: colors.{} = '{}' "
                        "is not a valid hex color (expected #RGB, #RRGGBB, or #RRGGBBAA).".format(
                            color_key, color_val
                        )
                    )

            # Check any additional color values are also valid hex
            for color_key, color_val in colors.items():
                if color_key in REQUIRED_COLORS:
                    continue  # Already checked above
                if color_val and isinstance(color_val, str) and not is_valid_hex(color_val):
                    warnings.append(
                        "brand.yaml: colors.{} = '{}' "
                        "doesn't look like a valid hex color.".format(color_key, color_val)
                    )

        # Optional but recommended fields
        optional_yaml_fields = {
            "tagline": "A tagline helps the model understand your brand's voice.",
            "logo_placement": "Specifies where to place the logo (default: top-left corner).",
            "font_strategy": "Set to 'exact' to render text with your brand font, or 'reference' (default).",
            "fonts": "Listing your font families helps guide typography in generations.",
        }
        for field, hint in optional_yaml_fields.items():
            if not brand.get(field):
                suggestions.append("brand.yaml: consider adding '{}' — {}".format(field, hint))

    # ------------------------------------------------------------------
    # 4. Check required folders
    # ------------------------------------------------------------------
    for folder, fix_msg in REQUIRED_FOLDERS.items():
        folder_path = brand_kit / folder
        img_count = count_images(folder_path)
        if img_count == 0:
            errors.append("No images found in {}/. {}".format(folder, fix_msg))

    # ------------------------------------------------------------------
    # 5. Check optional folders and suggest improvements
    # ------------------------------------------------------------------
    asset_summary = {}
    for folder, hint in OPTIONAL_FOLDERS.items():
        folder_path = brand_kit / folder
        img_count = count_images(folder_path)
        asset_summary[folder] = img_count
        if img_count == 0:
            suggestions.append("No images in {}/. {}".format(folder, hint))

    # Also count required folder assets for the summary
    for folder in REQUIRED_FOLDERS:
        asset_summary[folder] = count_images(brand_kit / folder)

    # ------------------------------------------------------------------
    # 6. Check learnings.yaml if it exists (non-blocking)
    # ------------------------------------------------------------------
    learnings_path = brand_kit / "learnings.yaml"
    if learnings_path.exists():
        try:
            learnings = load_yaml(str(learnings_path))
            rule_count = len(learnings.get("rules", []))
            asset_summary["learned_rules"] = rule_count
        except Exception:
            warnings.append("learnings.yaml exists but could not be parsed.")

    # ------------------------------------------------------------------
    # 7. Check feedback-log directory
    # ------------------------------------------------------------------
    feedback_dir = brand_kit / "feedback-log"
    if feedback_dir.is_dir():
        log_count = sum(1 for f in feedback_dir.iterdir()
                        if f.is_file() and f.suffix in (".yaml", ".yml"))
        asset_summary["feedback_logs"] = log_count
    else:
        asset_summary["feedback_logs"] = 0

    # ------------------------------------------------------------------
    # Build result
    # ------------------------------------------------------------------
    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "summary": {
            "brand_name": brand.get("name", "(not set)"),
            "brand_kit_path": str(brand_kit),
            "assets": asset_summary,
            "total_images": sum(v for k, v in asset_summary.items()
                                if k not in ("learned_rules", "feedback_logs")),
        },
    }


# ---------------------------------------------------------------------------
# Pretty output
# ---------------------------------------------------------------------------

def print_human_readable(result):
    """Print a human-friendly summary of the validation result."""
    summary = result.get("summary", {})
    brand_name = summary.get("brand_name", "Unknown")
    total = summary.get("total_images", 0)

    print()
    if result["valid"]:
        print("  Brand Kit: {}".format(brand_name))
        print("  Status: VALID")
        print("  Total image assets: {}".format(total))
    else:
        print("  Brand Kit: {}".format(brand_name))
        print("  Status: INVALID — {} error(s)".format(len(result["errors"])))
        print("  Total image assets: {}".format(total))

    # Errors
    if result["errors"]:
        print()
        print("  ERRORS (must fix):")
        for err in result["errors"]:
            print("    - {}".format(err))

    # Warnings
    if result["warnings"]:
        print()
        print("  WARNINGS:")
        for warn in result["warnings"]:
            print("    - {}".format(warn))

    # Suggestions
    if result["suggestions"]:
        print()
        print("  SUGGESTIONS (optional):")
        for sug in result["suggestions"]:
            print("    - {}".format(sug))

    # Asset breakdown
    assets = summary.get("assets", {})
    if assets:
        print()
        print("  ASSET INVENTORY:")
        for folder, count in sorted(assets.items()):
            label = "files" if folder in ("learned_rules", "feedback_logs") else "images"
            indicator = "OK" if count > 0 else "--"
            print("    {}  {}: {} {}".format(indicator, folder, count, label))

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate a brand-kit directory for the branded-design skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_brand_kit.py brand-kit/
    python validate_brand_kit.py brand-kit/ --json
        """,
    )
    parser.add_argument(
        "brand_kit",
        help="Path to the brand-kit directory.",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output JSON only (no human-readable summary).",
    )

    args = parser.parse_args()
    result = validate(args.brand_kit)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result)
        # Also print JSON for programmatic consumption
        print("--- JSON ---")
        print(json.dumps(result, indent=2))

    # Exit with non-zero if invalid
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
