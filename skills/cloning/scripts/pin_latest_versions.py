#!/usr/bin/env python3
"""
pin_latest_versions.py -- Pin a generated Next.js clone to the LATEST stable
Next.js + React at clone time.

WHY THIS EXISTS
    The code generator (Gemini) can only emit version numbers it saw during
    training, and those drift stale fast (it defaults to Next 14 / React 18).
    "Latest available" is a moving target that only the live npm registry knows.
    This script queries npm at clone time and rewrites package.json so every
    clone ships on the newest stable framework, never an end-of-life version.

WHAT IT PINS (and ONLY these -- everything else in package.json is untouched)
    dependencies:     next, react, react-dom
    devDependencies:  eslint-config-next, @types/react, @types/react-dom

    Tailwind, TypeScript, PostCSS, and animation libs (gsap / framer-motion) are
    deliberately NOT bumped. A Tailwind v3 -> v4 jump would break the generated
    config, which is a different kind of change from "use the latest framework."

COMPATIBILITY
    next, react, and react-dom are all resolved to their `latest` dist-tag in the
    same run, so they are mutually compatible by construction: npm's latest Next
    is released and tested against the latest stable React. react and react-dom
    are forced to the exact same version.

NO FALLBACKS
    If npm or the network is unavailable, this FAILS LOUDLY (exit 1) rather than
    pinning a stale hardcoded version. A visibly failed pin is safer than a
    silently outdated one.

USAGE
    python pin_latest_versions.py <project-dir>          # rewrite package.json
    python pin_latest_versions.py <project-dir> --dry-run # print, don't write
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# The only packages we touch. Grouped by the package.json section they live in.
PROD_DEPS = ["next", "react", "react-dom"]
DEV_DEPS = ["eslint-config-next", "@types/react", "@types/react-dom"]


def npm_latest(package: str) -> str:
    """Return the latest stable version string for `package` from the live npm
    registry. Raises RuntimeError (never returns a stale guess) on any failure."""
    try:
        result = subprocess.run(
            ["npm", "view", package, "version"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("npm is not installed or not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"npm view {package} timed out (network?)") from exc

    version = result.stdout.strip()
    if result.returncode != 0 or not version:
        raise RuntimeError(
            f"npm could not resolve latest version of '{package}'. "
            f"stderr: {result.stderr.strip() or '(none)'}"
        )
    return version


def resolve_latest_versions() -> dict:
    """Query npm once for every package we pin. react-dom is forced to match
    react so the two never drift apart across a race in the registry."""
    versions = {pkg: npm_latest(pkg) for pkg in PROD_DEPS + DEV_DEPS}
    versions["react-dom"] = versions["react"]  # lockstep guarantee
    return versions


def pin_package_json(project_dir: Path, dry_run: bool = False) -> dict:
    """Rewrite <project_dir>/package.json so the framework deps use the latest
    stable versions. Returns a report of old -> new for each changed field."""
    pkg_path = project_dir / "package.json"
    if not pkg_path.exists():
        raise FileNotFoundError(f"No package.json at {pkg_path}")

    data = json.loads(pkg_path.read_text())
    latest = resolve_latest_versions()

    data.setdefault("dependencies", {})
    data.setdefault("devDependencies", {})

    report = {}
    for section, names in (("dependencies", PROD_DEPS), ("devDependencies", DEV_DEPS)):
        target = data[section]
        for name in names:
            new_range = f"^{latest[name]}"
            old_range = target.get(name, "(absent)")
            if old_range != new_range:
                report[f"{section}/{name}"] = (old_range, new_range)
            target[name] = new_range

    if not dry_run:
        # 2-space indent + trailing newline is the npm/prettier convention.
        pkg_path.write_text(json.dumps(data, indent=2) + "\n")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pin a generated Next.js clone to the latest stable Next.js + React."
    )
    parser.add_argument("project_dir", help="Path to the generated clone (contains package.json)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()

    try:
        report = pin_package_json(project_dir, dry_run=args.dry_run)
    except (RuntimeError, FileNotFoundError) as exc:
        # Fail loudly. Do NOT paper over a failed lookup with a stale default.
        print(f"[pin_latest_versions] ERROR: {exc}", file=sys.stderr)
        return 1

    mode = "DRY RUN (nothing written)" if args.dry_run else "package.json updated"
    print(f"[pin_latest_versions] {mode} -> {project_dir / 'package.json'}")
    if report:
        for field, (old, new) in report.items():
            print(f"  {field}: {old} -> {new}")
    else:
        print("  Already on the latest stable versions. No changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
