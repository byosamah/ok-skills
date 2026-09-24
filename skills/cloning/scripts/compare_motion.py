#!/usr/bin/env python3
"""
Motion comparison that does not produce false failures.

Two failure modes make naive motion verification untrustworthy, and this script
exists to remove both.

FALSE FAILURE 1 - comparing at the same clock time.
    Screenshotting both sites "3 seconds after load" compares two different
    moments in the animation. Intro timelines usually start on an event like
    `document.fonts.ready`, which resolves far sooner on localhost than over the
    network. A real clone can look badly broken for this reason alone.
    Fix: align on the animation's own PHASE. Wait until the page stops changing,
    then measure. Both sides then get measured at the same point in the timeline
    rather than at the same point on the clock.

FALSE FAILURE 2 - reporting drift as a defect.
    Physics-driven motion (inertial carousels, smooth scroll) never settles to
    exactly the same sub-pixel position twice. Diffing a clone against an
    original will therefore always show differences, and a loop that treats them
    as defects never terminates.
    Fix: measure the clone against ITSELF across two loads first. That gives an
    empirical noise floor. Only differences larger than the clone's own
    run-to-run variance are real, and the noise floor doubles as a principled
    stop condition for the refinement loop.

Usage:
    python compare_motion.py --original https://site.com --clone http://localhost:3000
                             [--routes /,/about] [--width 1440] [--out report.json]
"""

import argparse
import asyncio
import json
import os
import statistics
import sys
from pathlib import Path

# Captures layout and paint state for every rendered element. Elements that
# never paint (script, style, link) are excluded because they add noise without
# describing anything a viewer can see.
PROBE = """
() => {
  const SKIP = new Set(['SCRIPT','NOSCRIPT','IFRAME','STYLE','LINK','META','TITLE','HEAD']);
  const els = [...document.querySelectorAll('body *')].filter(e => !SKIP.has(e.tagName));
  return {
    count: els.length,
    textLength: document.body.innerText.length,
    viewport: window.innerWidth,
    elements: els.map(e => {
      const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      return {
        tag: e.tagName,
        x: Math.round(r.left), y: Math.round(r.top),
        w: Math.round(r.width), h: Math.round(r.height),
        fontSize: cs.fontSize, fontWeight: cs.fontWeight,
        color: cs.color, opacity: cs.opacity, display: cs.display
      };
    })
  };
}
"""

# Waits for the page to reach a stable phase instead of a stable clock reading.
# Both the element count and the geometry must hold still, because an intro
# timeline can finish adding nodes long before it finishes moving them.
SETTLE = """
async (maxMs) => {
  const sig = () => {
    const els = document.querySelectorAll('body *');
    let s = els.length + ':';
    for (const e of els) {
      const r = e.getBoundingClientRect();
      s += (r.left | 0) + ',' + (r.top | 0) + ';';
    }
    return s;
  };
  const t0 = performance.now();
  let prev = '', stable = 0;
  while (performance.now() - t0 < maxMs && stable < 6) {
    await new Promise(r => setTimeout(r, 150));
    const s = sig();
    if (s === prev) stable++; else { stable = 0; prev = s; }
  }
  return { settledMs: Math.round(performance.now() - t0), reachedStable: stable >= 6 };
}
"""


# Chromium's own sandbox stays on: these scripts load arbitrary third-party
# sites, so a compromised renderer must not get the operator's full user
# rights. Some macOS agent sandboxes break Chromium's sandbox with a mach port
# error. Only there, and only inside a container or VM, set
# CLONE_ALLOW_UNSANDBOXED_BROWSER=1 to launch with --no-sandbox.
UNSANDBOXED_ENV = "CLONE_ALLOW_UNSANDBOXED_BROWSER"


async def launch_browser(pw):
    if os.environ.get(UNSANDBOXED_ENV) == "1":
        print(f"WARNING: {UNSANDBOXED_ENV}=1, launching Chromium with --no-sandbox. "
              "Hostile pages are not contained. Use only inside a container or VM.",
              file=sys.stderr)
        return await pw.chromium.launch(args=["--no-sandbox"])
    try:
        return await pw.chromium.launch()
    except Exception as e:
        raise SystemExit(
            f"Chromium failed to start with its sandbox on: {e}\n"
            f"If this is the macOS mach port error inside an agent sandbox, run the "
            f"command outside that sandbox. As a last resort, inside a container or VM "
            f"only, set {UNSANDBOXED_ENV}=1."
        )


async def sample(url, width, settle_ms):
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await launch_browser(pw)
        page = await browser.new_page(viewport={"width": width, "height": 900})
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            # networkidle never fires on pages with long-lived connections; the
            # settle probe below is the real readiness signal anyway.
            pass
        settle = await page.evaluate(SETTLE, settle_ms)
        data = await page.evaluate(PROBE)
        await browser.close()
    data["settle"] = settle
    return data


def diff(a, b, tolerance=0):
    """Compare two samples element by element, in document order."""
    ea, eb = a["elements"], b["elements"]
    result = {
        "count_a": len(ea), "count_b": len(eb),
        "count_match": len(ea) == len(eb),
        "text_match": a["textLength"] == b["textLength"],
        "differences": [],
    }
    for i, (x, y) in enumerate(zip(ea, eb)):
        fields = []
        for k in ("x", "y", "w", "h"):
            if abs(x[k] - y[k]) > tolerance:
                fields.append({"field": k, "a": x[k], "b": y[k], "delta": abs(x[k] - y[k])})
        for k in ("tag", "fontSize", "fontWeight", "color", "opacity", "display"):
            if x[k] != y[k]:
                fields.append({"field": k, "a": x[k], "b": y[k], "delta": None})
        if fields:
            result["differences"].append({"index": i, "tag": x["tag"], "fields": fields})
    return result


def geometry_deltas(d):
    return [f["delta"] for e in d["differences"] for f in e["fields"] if f["delta"] is not None]


async def run_route(original, clone, route, width, settle_ms):
    o_url = original.rstrip("/") + route
    c_url = clone.rstrip("/") + route

    # Two clone samples first. Their disagreement is the noise floor, and without
    # it there is no way to tell drift from a defect.
    clone_a = await sample(c_url, width, settle_ms)
    clone_b = await sample(c_url, width, settle_ms)
    orig = await sample(o_url, width, settle_ms)

    noise = diff(clone_a, clone_b)
    noise_deltas = geometry_deltas(noise)
    noise_px = max(noise_deltas) if noise_deltas else 0
    noise_elements = len(noise["differences"])

    raw = diff(clone_a, orig)
    # Anything the clone cannot reproduce against itself is not evidence about
    # the original, so it is filtered out rather than reported as a defect.
    real = [d for d in raw["differences"]
            if any(f["delta"] is None or f["delta"] > noise_px for f in d["fields"])]

    return {
        "route": route,
        "viewport": width,
        "settle": {"clone": clone_a["settle"], "original": orig["settle"]},
        "noise_floor": {
            "elements_differing": noise_elements,
            "max_pixel_delta": noise_px,
            "explanation": (
                "The clone differs from itself by this much across two loads. "
                "Differences at or below this level are drift, not defects."
            ),
        },
        "structure": {
            "clone_elements": raw["count_a"],
            "original_elements": raw["count_b"],
            "element_count_match": raw["count_match"],
            "text_length_match": raw["text_match"],
        },
        "raw_differences": len(raw["differences"]),
        "real_differences": len(real),
        "verdict": (
            "MISMATCH: element counts differ" if not raw["count_match"]
            else "MATCH: differences are within the clone's own drift" if not real
            else f"{len(real)} difference(s) exceed the noise floor"
        ),
        "details": real[:40],
    }


async def main_async(args):
    routes = [r.strip() for r in args.routes.split(",") if r.strip()]
    reports = []
    for route in routes:
        print(f"  {route} ...", flush=True)
        r = await run_route(args.original, args.clone, route, args.width, args.settle)
        reports.append(r)
        nf = r["noise_floor"]
        print(f"    noise floor: {nf['elements_differing']} elements, "
              f"{nf['max_pixel_delta']}px")
        print(f"    {r['verdict']}")
    return reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True)
    ap.add_argument("--clone", required=True)
    ap.add_argument("--routes", default="/")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--settle", type=int, default=15000,
                    help="max ms to wait for the page to stop changing")
    ap.add_argument("--out", default="motion-comparison.json")
    args = ap.parse_args()

    print("Comparing motion (clone sampled twice to establish a noise floor)...")
    reports = asyncio.run(main_async(args))
    Path(args.out).write_text(json.dumps(reports, indent=2))

    total_real = sum(r["real_differences"] for r in reports)
    print("\n" + "=" * 66)
    for r in reports:
        print(f"{r['route']:<12} {r['verdict']}")
    print("=" * 66)
    print(f"Report: {args.out}")
    if total_real == 0:
        print("All routes match within the clone's own run-to-run variance.")
    else:
        print(f"{total_real} real difference(s) to fix. See 'details' in the report.")


if __name__ == "__main__":
    main()
