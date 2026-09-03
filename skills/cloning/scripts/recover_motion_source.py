#!/usr/bin/env python3
"""
Motion Source Recovery (run this before any code generation).

Inferring motion from a screen recording is a last resort, not a first move.
Before guessing, find out how much of the real thing you can simply obtain:

  1. Source maps        -> the ORIGINAL unminified source, real file names.
  2. Library identity   -> which animation packages the site actually vendors.
  3. Exact versions     -> `npm i gsap@3.15.0` reproduces the real easing curves
                           and the real physics, instead of an approximation of
                           them. This is usually the single biggest fidelity win
                           available, and it costs one install.

Why identity beats reading the bundle: production bundles are almost always
minified, so local variable names are gone and the code is not worth
transcribing by hand. But library *identity* survives minification, because it
leaks through things a minifier must preserve: runtime warning strings
("gsap.registerPlugin()"), public API names, DOM attribute hooks
("[data-smooothy]"), and embedded version literals (`.version="3.15.0"`).
Those are the fingerprints this script hunts for.

Usage:
    python recover_motion_source.py <url> <output-dir> [--routes /,/about]

Output (under <output-dir>/motion-source/):
    bundles/                  every JS file the page loaded, verbatim
    sources/                  originals recovered from source maps, when present
    pretty/                   re-formatted bundles, readable control flow
    motion-source-report.json findings plus the exact install commands to run
"""

import argparse
import asyncio
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Each entry lists fingerprints that survive minification. Import specifiers are
# deliberately NOT used: when a library is inlined into a bundle, the string
# "gsap" never appears as a quoted module specifier, which is exactly why naive
# specifier scans report nothing on real sites.
LIBRARY_SIGNATURES = {
    "gsap": {
        "signals": [r"registerPlugin", r"_gsap\b", r"gsap\.registerPlugin"],
        "note": "timeline engine; easing curves and durations come from here",
    },
    "gsap/ScrollTrigger": {
        "signals": [r"ScrollTrigger", r"scrollerProxy", r"toggleActions"],
        "note": "scroll-driven timelines; ships inside the gsap package",
    },
    "gsap/Observer": {
        "signals": [r"registerPlugin\(Observer\)", r"\bObserver\b.*onDragStart"],
        "note": "unified wheel/touch/pointer input; ships inside gsap",
    },
    "gsap/SplitText": {
        "signals": [r"SplitText", r"linesClass", r"splitType"],
        "note": "splits text for staggered reveals; ships inside gsap",
    },
    "gsap/Flip": {
        "signals": [r"Flip\.getState", r"saveStyles"],
        "note": "layout transition plugin; ships inside gsap",
    },
    "lenis": {
        "signals": [r"smoothWheel", r"syncTouch", r"lerp.*wheelMultiplier"],
        "note": "smooth scroll with inertia; shifts every scroll-linked value",
    },
    "smooothy": {
        "signals": [r"data-smooothy", r"smooothy"],
        "note": "physics-based drag carousel (three o's); do not reimplement",
    },
    "locomotive-scroll": {
        "signals": [r"data-scroll-container", r"locomotive"],
        "note": "smooth scroll plus scroll-triggered classes",
    },
    "swiper": {
        "signals": [r"swiper-slide", r"swiper-wrapper"],
        "note": "carousel with its own momentum and easing",
    },
    "embla-carousel": {
        "signals": [r"embla__", r"emblaApi"],
        "note": "carousel engine with physics options",
    },
    "keen-slider": {"signals": [r"keen-slider"], "note": "carousel with momentum"},
    "flickity": {"signals": [r"flickity"], "note": "drag carousel with physics"},
    "framer-motion": {
        "signals": [r"framerAppearId", r"whileInView", r"layoutDependency"],
        "note": "React animation; never mix with GSAP in one component",
    },
    "motion": {"signals": [r"animateMini", r"inView\(", r"motionValue"],
               "note": "Motion One"},
    "animejs": {"signals": [r"anime\.timeline", r"animejs"], "note": "timeline engine"},
    "@barba/core": {
        "signals": [r"data-barba", r"barba\.init"],
        "note": "page transitions; controls enter/leave choreography",
    },
    "swup": {"signals": [r"swup", r"data-swup"], "note": "page transitions"},
    "split-type": {"signals": [r"split-type", r"SplitType"],
                   "note": "open-source SplitText equivalent"},
    "lottie-web": {"signals": [r"lottie", r"bodymovin"],
                   "note": "After Effects vector playback"},
    "@rive-app/canvas": {"signals": [r"rive", r"\.riv\b"],
                         "note": "interactive vector runtime"},
    "matter-js": {"signals": [r"Matter\.Engine", r"matter-js"],
                  "note": "2d rigid-body physics"},
    "three": {"signals": [r"THREE\.", r"WebGLRenderer"],
              "note": "WebGL; motion may live in shaders"},
    "ogl": {"signals": [r"\bOGL\b", r"ogl"], "note": "lightweight WebGL"},
    "scrollama": {"signals": [r"scrollama"], "note": "scrollytelling triggers"},
    "tempus": {"signals": [r"tempus"], "note": "raf scheduler; Lenis syncs through it"},
}

# Version literals a bundler cannot mangle away: `.version="3.15.0"`.
VERSION_RE = re.compile(r"""\.version\s*=\s*[`"']([0-9]+\.[0-9]+\.[0-9]+)[`"']""")

SKIP_HOST_RE = re.compile(
    r"google-analytics|googletagmanager|doubleclick|facebook\.net|hotjar|"
    r"segment\.(io|com)|intercom|sentry\.io|clarity\.ms|newrelic|datadoghq|"
    r"cloudflareinsights|cdn-cgi/challenge-platform",
    re.I,
)


def safe_name(url: str) -> str:
    p = urlparse(url)
    raw = (p.netloc + p.path).strip("/")
    return (re.sub(r"[^A-Za-z0-9._-]", "_", raw) or "bundle")[-180:]


async def capture(url, routes, outdir, timeout_ms):
    from playwright.async_api import async_playwright

    bundles = outdir / "bundles"
    bundles.mkdir(parents=True, exist_ok=True)
    seen, errors, attrs = {}, [], set()

    async with async_playwright() as pw:
        # --no-sandbox: Chromium's sandbox fails with a mach port error in some
        # macOS agent environments and aborts the whole capture.
        browser = await pw.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        async def on_response(resp):
            u = resp.url
            if u in seen or SKIP_HOST_RE.search(u):
                return
            ctype = (resp.headers or {}).get("content-type", "")
            if "javascript" not in ctype and not u.split("?")[0].endswith((".js", ".mjs")):
                return
            try:
                body = await resp.body()
            except Exception as e:
                errors.append({"url": u[:180], "error": str(e)[:160]})
                return
            fname = safe_name(u)
            if not fname.endswith((".js", ".mjs")):
                fname += ".js"
            (bundles / fname).write_bytes(body)
            seen[u] = {"file": fname, "bytes": len(body)}

        page.on("response", lambda r: asyncio.create_task(on_response(r)))

        for route in routes:
            target = urljoin(url, route)
            try:
                await page.goto(target, wait_until="networkidle", timeout=timeout_ms)
            except Exception as e:
                errors.append({"url": target, "error": str(e)[:160]})
                continue
            # Scroll the whole page: modules that are imported lazily only arrive
            # when their section enters the viewport, and those are frequently the
            # animation modules. A <script src> scan never sees them.
            try:
                await page.evaluate(
                    """async () => {
                        const step = window.innerHeight, end = document.body.scrollHeight;
                        for (let y = 0; y <= end; y += step) {
                            window.scrollTo(0, y);
                            await new Promise(r => setTimeout(r, 200));
                        }
                        window.scrollTo(0, 0);
                    }"""
                )
                await page.wait_for_timeout(1000)
                # Libraries are frequently wired up through DOM attributes, so the
                # markup names the library even when the bundle does not.
                found = await page.evaluate(
                    """() => {
                        const out = new Set();
                        for (const el of document.querySelectorAll('*')) {
                            for (const a of el.attributes) {
                                if (a.name.startsWith('data-')) out.add(a.name);
                            }
                        }
                        return [...out];
                    }"""
                )
                attrs.update(found)
            except Exception as e:
                errors.append({"url": target, "error": "scroll/attrs: " + str(e)[:140]})

        await browser.close()
    return seen, errors, sorted(attrs)


def resolve_source_maps(outdir, base_url):
    """Free win when present: the original source, with real names and comments."""
    import base64
    import urllib.request

    recovered, pkgs, notes = [], {}, []
    for bundle in sorted((outdir / "bundles").glob("*.js")):
        try:
            text = bundle.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        m = re.search(r"//[#@]\s*sourceMappingURL=(\S+)", text)
        if not m:
            continue
        ref = m.group(1).strip()
        try:
            if ref.startswith("data:"):
                raw = base64.b64decode(ref.split(",", 1)[1]).decode("utf-8", "replace")
            else:
                with urllib.request.urlopen(urljoin(base_url, ref), timeout=20) as r:
                    raw = r.read().decode("utf-8", "replace")
            smap = json.loads(raw)
        except Exception as e:
            notes.append(f"{bundle.name}: map referenced but unreadable ({str(e)[:70]})")
            continue

        contents = smap.get("sourcesContent") or []
        for i, src in enumerate(smap.get("sources") or []):
            mm = re.search(r"node_modules/((?:@[^/]+/)?[^/]+)", src)
            if mm:
                pkgs.setdefault(mm.group(1), set()).add(bundle.name)
            if i < len(contents) and contents[i]:
                rel = re.sub(r"[^A-Za-z0-9._/-]", "_", re.sub(r"^(\.\./)+", "", src).lstrip("/"))
                dest = outdir / "sources" / bundle.name[:-3] / (rel or f"src_{i}.js")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(contents[i], encoding="utf-8")
                recovered.append(str(dest.relative_to(outdir)))
    return recovered, {k: sorted(v) for k, v in pkgs.items()}, notes


def fingerprint(outdir, dom_attrs):
    """Identify libraries by traces a minifier is forced to keep."""
    attr_blob = " ".join(dom_attrs)
    hits = {}
    for bundle in sorted((outdir / "bundles").glob("*.js")):
        try:
            text = bundle.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        versions = sorted(set(VERSION_RE.findall(text)))
        for pkg, spec in LIBRARY_SIGNATURES.items():
            matched = [s for s in spec["signals"]
                       if re.search(s, text, re.I) or re.search(s, attr_blob, re.I)]
            if not matched:
                continue
            e = hits.setdefault(pkg, {
                "package": pkg, "note": spec["note"],
                "signals_matched": set(), "found_in": [], "version_candidates": set(),
            })
            e["signals_matched"].update(matched)
            e["found_in"].append(bundle.name)
            e["version_candidates"].update(versions)

    out = []
    for pkg, e in hits.items():
        e["signals_matched"] = sorted(e["signals_matched"])
        e["version_candidates"] = sorted(e["version_candidates"])
        # One matched signal on a generic word is weak evidence. Two is a library.
        e["confidence"] = "high" if len(e["signals_matched"]) >= 2 else "low"
        out.append(e)
    out.sort(key=lambda x: (x["confidence"] != "high", x["package"]))
    return out


def npm_exists(pkg, version=None):
    target = f"{pkg}@{version}" if version else pkg
    try:
        r = subprocess.run(["npm", "view", target, "version"],
                           capture_output=True, text=True, timeout=45)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def beautify(outdir, limit_kb=400):
    """Re-format bundles so control flow is followable.

    Names stay mangled, so this is not a substitute for a source map. It is still
    worth doing: reading the real sequence of calls beats inferring that sequence
    from a video, even when the variables are called `n` and `r`.
    """
    if not shutil.which("npx"):
        return []
    pretty_dir = outdir / "pretty"
    pretty_dir.mkdir(exist_ok=True)
    done = []
    for bundle in sorted((outdir / "bundles").glob("*.js"),
                         key=lambda p: -p.stat().st_size):
        if bundle.stat().st_size > limit_kb * 1024:
            continue
        dest = pretty_dir / bundle.name
        try:
            r = subprocess.run(
                ["npx", "--yes", "prettier", "--parser", "babel", str(bundle)],
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode == 0 and r.stdout.strip():
                dest.write_text(r.stdout, encoding="utf-8")
                done.append(dest.name)
        except Exception:
            continue
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir")
    ap.add_argument("--routes", default="/")
    ap.add_argument("--timeout", type=int, default=45000)
    ap.add_argument("--no-beautify", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir).expanduser() / "motion-source"
    outdir.mkdir(parents=True, exist_ok=True)
    routes = [r.strip() for r in args.routes.split(",") if r.strip()]

    print(f"[1/5] Capturing JS from {args.url} ({len(routes)} route(s))...")
    seen, errors, dom_attrs = asyncio.run(capture(args.url, routes, outdir, args.timeout))
    print(f"      {len(seen)} file(s) saved; {len(dom_attrs)} data-* attributes seen")

    print("[2/5] Resolving source maps...")
    recovered, map_pkgs, notes = resolve_source_maps(outdir, args.url)
    print(f"      {len(recovered)} original source file(s) recovered"
          if recovered else "      none published")

    print("[3/5] Fingerprinting libraries...")
    libs = fingerprint(outdir, dom_attrs)
    for pkg in map_pkgs:
        if not any(l["package"] == pkg for l in libs):
            libs.append({"package": pkg, "note": "seen in source map paths",
                         "signals_matched": ["source-map"], "found_in": map_pkgs[pkg],
                         "version_candidates": [], "confidence": "high"})

    print("[4/5] Matching versions on npm...")
    for lib in libs:
        base = lib["package"].split("/")[0] if not lib["package"].startswith("@") else lib["package"]
        lib["npm_package"] = base
        lib["exact_version"] = None
        for v in lib["version_candidates"]:
            if npm_exists(base, v):
                lib["exact_version"] = v
                break
        lib["install"] = (f"npm i {base}@{lib['exact_version']}"
                          if lib["exact_version"] else f"npm i {base}")

    pretty = [] if args.no_beautify else beautify(outdir)
    print(f"[5/5] Beautified {len(pretty)} bundle(s) into motion-source/pretty/")

    strategy = ("source-maps" if recovered
                else "install-and-read" if any(l["confidence"] == "high" for l in libs)
                else "infer-from-video")
    report = {
        "url": args.url, "routes": routes,
        "bundles": [{"url": k, **v} for k, v in seen.items()],
        "dom_data_attributes": dom_attrs,
        "source_maps": {"recovered_count": len(recovered),
                        "recovered_files": recovered, "notes": notes},
        "libraries": libs,
        "beautified": pretty,
        "strategy": strategy,
        "errors": errors,
    }
    (outdir / "motion-source-report.json").write_text(json.dumps(report, indent=2))

    print("\n" + "=" * 70)
    print(f"STRATEGY: {strategy}")
    high = [l for l in libs if l["confidence"] == "high"]
    if high:
        # Several detections collapse to one install: gsap, gsap/ScrollTrigger and
        # gsap/Observer all ship inside the gsap package. Print the command once
        # and list underneath it what that single install actually buys.
        by_cmd = {}
        for l in high:
            by_cmd.setdefault(l["install"], []).append(l)
        print("\n  Install these instead of reimplementing their behaviour:")
        for cmd, group in by_cmd.items():
            exact = " (exact version confirmed on npm)" if group[0]["exact_version"] else ""
            print(f"    {cmd}{exact}")
            for l in group:
                print(f"        - {l['package']}: {l['note']}")

    if recovered:
        print(f"\n  Read motion-source/sources/ first: {len(recovered)} original files.")
    elif pretty:
        print("\n  No source maps. Read motion-source/pretty/ for real control flow.")
    elif args.no_beautify:
        print("\n  No source maps, and beautify was skipped. Re-run without"
              " --no-beautify to make the bundles readable.")
    else:
        print("\n  Bundles are minified and no maps are published. Install the"
              " packages above, then infer only what remains from the videos.")
    print("=" * 70)


if __name__ == "__main__":
    main()
