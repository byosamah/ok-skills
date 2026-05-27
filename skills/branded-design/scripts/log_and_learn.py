#!/usr/bin/env python3
"""
Brand Post Logger & Learner — logs generation metadata and extracts
actionable rules from iteration feedback to improve future generations.

After each accepted design, this script:
1. Writes a detailed YAML log to brand-kit/feedback-log/{date}-{slug}.yaml
2. Extracts rules from iteration feedback (e.g. "text too small" -> "Use larger text")
3. Appends new rules to brand-kit/learnings.yaml (deduplicating)
4. Updates generation counter and timestamp

Usage:
    python log_and_learn.py \
        --brand-kit brand-kit \
        --content "Summer Sale — 50% off" \
        --direction "promotional, vibrant" \
        --platform instagram_feed \
        --aspect-ratio 1:1 \
        --references "examples/promo/sale.png,logo/logo.png" \
        --prompt-used "Create a promotional social media post..." \
        --iterations '[{"feedback":"text too small","action":"tweak"},{"feedback":"perfect","action":"accept"}]' \
        --output-path output/summer-sale.png

    # Or pipe JSON via stdin
    echo '{"content":"...","iterations":[...]}' | python log_and_learn.py --brand-kit brand-kit --stdin
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML handling — prefers PyYAML, falls back to manual read/write
# ---------------------------------------------------------------------------

_HAS_PYYAML = False
try:
    import yaml
    _HAS_PYYAML = True
except ImportError:
    pass


def load_yaml(path):
    """Load a YAML file. Uses PyYAML if available, else minimal parser."""
    if _HAS_PYYAML:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    else:
        return _manual_load_yaml(path)


def dump_yaml(data, path):
    """Write a dict to a YAML file. Uses PyYAML if available, else manual."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if _HAS_PYYAML:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        _manual_dump_yaml(data, path)


def _manual_load_yaml(path):
    """Minimal YAML parser for simple structures."""
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
                if ":" in stripped and not stripped.startswith("- "):
                    k, v = stripped.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if current_dict is None:
                        current_dict = {}
                        data[current_key] = current_dict
                    current_dict[k] = _coerce_value(v)
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
                    data[k] = _coerce_value(v)

    return data


def _coerce_value(v):
    """Coerce a string value to int/float/bool where obvious."""
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _manual_dump_yaml(data, path):
    """Write a dict as simple YAML (handles scalars, lists, one-level dicts)."""
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append("{}:".format(key))
            for item in value:
                # Escape strings that might be misread
                item_str = str(item)
                if ":" in item_str or "#" in item_str or item_str.startswith("-"):
                    lines.append('  - "{}"'.format(item_str))
                else:
                    lines.append("  - {}".format(item_str))
        elif isinstance(value, dict):
            lines.append("{}:".format(key))
            for k, v in value.items():
                v_str = str(v)
                if ":" in v_str or "#" in v_str:
                    lines.append('  {}: "{}"'.format(k, v_str))
                else:
                    lines.append("  {}: {}".format(k, v_str))
        else:
            v_str = str(value)
            if isinstance(value, bool):
                v_str = "true" if value else "false"
            if ":" in v_str or "#" in v_str:
                lines.append('{}: "{}"'.format(key, v_str))
            else:
                lines.append("{}: {}".format(key, v_str))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Feedback -> Rule extraction
# ---------------------------------------------------------------------------

# Patterns that map common feedback phrases to actionable rules.
# Each tuple: (regex_pattern, extracted_rule)
FEEDBACK_RULES = [
    # Text sizing
    (r"text.*(too small|tiny|hard to read|can.t read|unreadable)",
     "Use larger, more prominent text for readability"),
    (r"text.*(too big|too large|overwhelming|takes up too much)",
     "Use more restrained text sizing — avoid overwhelming the design"),
    (r"font.*(too small|tiny|hard to read)",
     "Increase font size for better legibility"),
    (r"font.*(wrong|different|doesn.t match|off-brand)",
     "Pay closer attention to brand font style from reference examples"),

    # Colors
    (r"(color|colour).*(too bright|saturated|loud|vibrant)",
     "Tone down color saturation — prefer more muted brand palette"),
    (r"(color|colour).*(too dark|dull|muted|washed out)",
     "Use more vibrant, saturated brand colors"),
    (r"(color|colour).*(wrong|off|doesn.t match|not brand)",
     "Strictly adhere to the brand color palette from brand.yaml"),
    (r"(background|bg).*(too busy|cluttered|distracting)",
     "Use cleaner, simpler backgrounds"),

    # Logo
    (r"logo.*(too small|tiny|hard to see|bigger)",
     "Make the logo more prominent and visible"),
    (r"logo.*(too big|too large|overwhelming|dominant)",
     "Reduce logo size — it should complement, not dominate"),
    (r"logo.*(wrong|missing|placement|position|move)",
     "Ensure correct logo placement per brand.yaml logo_placement field"),

    # Layout & spacing
    (r"(too crowded|too busy|cluttered|cramped|needs.*space)",
     "Add more whitespace and breathing room between elements"),
    (r"(too empty|too sparse|needs.*more|bare|minimal.*too)",
     "Fill more of the canvas — the design feels too sparse"),
    (r"(alignment|aligned|centered|off.?center)",
     "Pay attention to element alignment and centering"),
    (r"(hierarchy|visual.*hierarchy|importance|emphasis)",
     "Establish clearer visual hierarchy — headline > subtext > details"),

    # Style & mood
    (r"(too generic|boring|plain|bland|basic)",
     "Push for more distinctive, brand-specific visual personality"),
    (r"(not.*brand|off.?brand|doesn.t.*feel|inconsistent)",
     "Lean harder on reference images to match brand visual identity"),
    (r"(too complex|simplify|simpler|less.*elements)",
     "Simplify the composition — fewer elements, clearer message"),
    (r"(warmer|warm.*color|warm.*tone)",
     "Use warmer tones in the color treatment"),
    (r"(cooler|cool.*color|cool.*tone)",
     "Use cooler tones in the color treatment"),
    (r"(more.*contrast|low.*contrast|contrast.*higher)",
     "Increase contrast between text and background for readability"),

    # Content
    (r"(wrong.*text|typo|spelling|misspell|incorrect.*text)",
     "Double-check that all text content is rendered exactly as provided"),
    (r"(CTA|call.to.action|button).*(missing|add|needs|bigger|prominent)",
     "Make the call-to-action more prominent and clear"),
]


def extract_rules(iterations):
    """
    Extract actionable rules from a list of iteration feedback entries.

    Each iteration is expected to have at minimum:
        {"feedback": "some text", "action": "tweak"|"redo"|"accept"}

    Only 'tweak' and 'redo' actions contain actionable feedback.
    'accept' means the user was satisfied — nothing to learn.

    Returns:
        List of extracted rule strings.
    """
    rules = []

    for iteration in iterations:
        action = iteration.get("action", "").lower()
        feedback = iteration.get("feedback", "").strip()

        # Only extract rules from correction feedback
        if action not in ("tweak", "redo") or not feedback:
            continue

        feedback_lower = feedback.lower()
        matched = False

        for pattern, rule in FEEDBACK_RULES:
            if re.search(pattern, feedback_lower):
                rules.append(rule)
                matched = True
                break  # One rule per feedback entry

        # If no pattern matched, create a generic rule from the feedback
        if not matched and len(feedback) > 5:
            # Clean up the feedback into a rule-like statement
            rule = feedback.strip().rstrip(".")
            # Capitalize first letter
            rule = rule[0].upper() + rule[1:] if rule else rule
            rules.append(rule)

    return rules


def deduplicate_rules(existing, new):
    """
    Merge new rules into existing ones, deduplicating by similarity.
    Uses lowercase comparison to catch near-duplicates.
    """
    existing_lower = {r.lower().strip() for r in existing}
    added = []

    for rule in new:
        if rule.lower().strip() not in existing_lower:
            added.append(rule)
            existing_lower.add(rule.lower().strip())

    return added


# ---------------------------------------------------------------------------
# Core logging
# ---------------------------------------------------------------------------

def write_generation_log(brand_kit, metadata):
    """
    Write a detailed YAML log entry for this generation.

    Returns:
        Path to the created log file.
    """
    log_dir = brand_kit / "feedback-log"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Build a slug from the content
    content = metadata.get("content", "untitled")
    slug = re.sub(r"[^a-z0-9]+", "-", content[:50].lower()).strip("-")
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Ensure unique filename
    log_path = log_dir / "{}-{}.yaml".format(date_str, slug)
    counter = 1
    while log_path.exists():
        counter += 1
        log_path = log_dir / "{}-{}-{}.yaml".format(date_str, slug, counter)

    log_entry = {
        "timestamp": timestamp,
        "content": metadata.get("content", ""),
        "direction": metadata.get("direction", ""),
        "platform": metadata.get("platform", ""),
        "aspect_ratio": metadata.get("aspect_ratio", ""),
        "references": metadata.get("references", []),
        "prompt_used": metadata.get("prompt_used", ""),
        "output_path": metadata.get("output_path", ""),
        "iterations": metadata.get("iterations", []),
        "iteration_count": len(metadata.get("iterations", [])),
        "accepted_first_try": len(metadata.get("iterations", [])) <= 1,
    }

    # Extract any rules learned from this generation
    iterations = metadata.get("iterations", [])
    if isinstance(iterations, str):
        try:
            iterations = json.loads(iterations)
        except json.JSONDecodeError:
            iterations = []

    new_rules = extract_rules(iterations)
    if new_rules:
        log_entry["rules_extracted"] = new_rules

    dump_yaml(log_entry, str(log_path))
    return log_path


def update_learnings(brand_kit, new_rules):
    """
    Append new rules to brand-kit/learnings.yaml, deduplicating.

    Returns:
        dict with update stats: rules_added, total_rules.
    """
    learnings_path = brand_kit / "learnings.yaml"

    # Load existing learnings
    if learnings_path.exists():
        learnings = load_yaml(str(learnings_path))
    else:
        learnings = {
            "rules": [],
            "total_generations": 0,
            "last_updated": "",
        }

    existing_rules = learnings.get("rules", [])
    if not isinstance(existing_rules, list):
        existing_rules = []

    # Deduplicate and merge
    added = deduplicate_rules(existing_rules, new_rules)
    all_rules = existing_rules + added

    # Update the learnings file
    learnings["rules"] = all_rules
    total_gen = learnings.get("total_generations", 0)
    if isinstance(total_gen, int):
        learnings["total_generations"] = total_gen + 1
    else:
        learnings["total_generations"] = 1
    learnings["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    dump_yaml(learnings, str(learnings_path))

    return {
        "rules_added": len(added),
        "rules_added_list": added,
        "total_rules": len(all_rules),
        "total_generations": learnings["total_generations"],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Log branded-design generations and extract learnings from feedback.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python log_and_learn.py \\
        --brand-kit brand-kit \\
        --content "Summer Sale" \\
        --direction "promotional, vibrant" \\
        --platform instagram_feed \\
        --aspect-ratio 1:1 \\
        --references "examples/promo/sale.png,logo/logo.png" \\
        --prompt-used "Create a promotional..." \\
        --iterations '[{"feedback":"text too small","action":"tweak"},{"feedback":"perfect","action":"accept"}]' \\
        --output-path output/summer-sale.png

    # Or pipe all metadata as JSON via stdin
    echo '{"content":"..."}' | python log_and_learn.py --brand-kit brand-kit --stdin
        """,
    )

    parser.add_argument(
        "--brand-kit", required=True,
        help="Path to the brand-kit directory.",
    )
    parser.add_argument("--content", help="Post content/copy text.")
    parser.add_argument("--direction", help="Creative direction brief.")
    parser.add_argument("--platform", help="Target platform.")
    parser.add_argument("--aspect-ratio", help="Aspect ratio used.")
    parser.add_argument(
        "--references",
        help="Comma-separated list of reference paths used.",
    )
    parser.add_argument("--prompt-used", help="The full prompt sent to Nano Banana.")
    parser.add_argument(
        "--iterations",
        help="JSON array of iteration objects: "
             '[{"feedback":"...","action":"tweak|redo|accept"}, ...]',
    )
    parser.add_argument("--output-path", help="Path to the final accepted image.")
    parser.add_argument(
        "--stdin", action="store_true",
        help="Read all metadata as a JSON object from stdin.",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON only.",
    )

    args = parser.parse_args()

    brand_kit = Path(args.brand_kit).resolve()
    if not brand_kit.is_dir():
        print("ERROR: Brand kit directory not found: {}".format(brand_kit), file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Build metadata from args or stdin
    # ------------------------------------------------------------------
    if args.stdin:
        try:
            raw = sys.stdin.read()
            metadata = json.loads(raw)
        except json.JSONDecodeError as e:
            print("ERROR: Invalid JSON on stdin: {}".format(e), file=sys.stderr)
            sys.exit(1)
    else:
        # Parse references
        refs = []
        if args.references:
            refs = [r.strip() for r in args.references.split(",") if r.strip()]

        # Parse iterations
        iterations = []
        if args.iterations:
            try:
                iterations = json.loads(args.iterations)
            except json.JSONDecodeError as e:
                print("ERROR: --iterations must be valid JSON: {}".format(e), file=sys.stderr)
                sys.exit(1)

        metadata = {
            "content": args.content or "",
            "direction": args.direction or "",
            "platform": args.platform or "",
            "aspect_ratio": args.aspect_ratio or "",
            "references": refs,
            "prompt_used": args.prompt_used or "",
            "iterations": iterations,
            "output_path": args.output_path or "",
        }

    # ------------------------------------------------------------------
    # 1. Write the generation log
    # ------------------------------------------------------------------
    try:
        log_path = write_generation_log(brand_kit, metadata)
    except Exception as e:
        print("ERROR: Failed to write log: {}".format(e), file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Extract rules from iterations and update learnings
    # ------------------------------------------------------------------
    iterations = metadata.get("iterations", [])
    if isinstance(iterations, str):
        try:
            iterations = json.loads(iterations)
        except json.JSONDecodeError:
            iterations = []

    new_rules = extract_rules(iterations)

    try:
        learning_stats = update_learnings(brand_kit, new_rules)
    except Exception as e:
        print("ERROR: Failed to update learnings: {}".format(e), file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # 3. Build result
    # ------------------------------------------------------------------
    result = {
        "success": True,
        "log_path": str(log_path),
        "rules_extracted": new_rules,
        "rules_added": learning_stats["rules_added"],
        "rules_added_list": learning_stats["rules_added_list"],
        "total_rules": learning_stats["total_rules"],
        "total_generations": learning_stats["total_generations"],
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("  Log written: {}".format(log_path))
        print("  Generation #{}".format(learning_stats["total_generations"]))

        if new_rules:
            print("  Rules extracted ({}):".format(len(new_rules)))
            for rule in new_rules:
                print("    + {}".format(rule))
            print("  New rules added: {} "
                  "(total: {})".format(learning_stats["rules_added"],
                                       learning_stats["total_rules"]))
        else:
            print("  No new rules extracted (accepted first try).")

        print()
        print("--- JSON ---")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
