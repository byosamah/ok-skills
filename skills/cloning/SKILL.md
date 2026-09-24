---
name: cloning
description: |
  Clone any website to 100% fidelity — not 90%, not "close enough", 100%.
  Recovers the site's real animation libraries and exact versions off the wire first
  (source maps, GSAP/Lenis/Smooothy/Swiper fingerprints, npm version pinning), generates
  with Gemini 3.1 Pro, then pushes through a self-healing visual loop until every section,
  every badge color, every easing curve and every pixel matches. Verifies motion at the
  same animation phase against a measured noise floor, not at a fixed clock time.
  Playwright-only deterministic pipeline. Never stops until the clone is indistinguishable.
  Use when the user says "clone this website", "/cloning [URL]", "perfect clone this design",
  or wants to replicate any website's visual design. Also use when the user mentions
  "website cloning", "copy this design", "replicate this UI", "match this site exactly",
  "rebuild this site", "keep fixing", "push to 100%", or "refine the clone" — and whenever
  they want a site's animations, scroll effects, carousel physics or page transitions
  reproduced faithfully rather than approximated.
model: opus
context: fork
effort: max
---

# Website Cloning Skill v6.2

Clone any website with **100% fidelity**. Not 90%. Not "close enough." 100%.

The goal is a clone a person cannot tell apart from the original. Gemini writes the first draft. Then compare every section, fix every difference, and repeat. Compiling code is not the finish line; the exit criteria in Step 3g are.

## The governing principle: don't guess what you can read

Video inference is this pipeline's most-used tool and its least reliable one. A recording
shows you the *result* of an animation. It cannot show you the easing function, the stagger
interval, the scrub value, or whether a carousel runs on a spring or a tween.

Most sites hand you far better evidence, and it is sitting in the network tab. Before
inferring any motion, find out how much of the real thing you can simply obtain: the
original source via source maps, or failing that the exact animation libraries and their
exact versions. Installing `gsap@3.15.0` reproduces the original's easing curves perfectly
and costs one command. Approximating those curves by eye never fully converges.

Treat Gemini-from-video as the **fallback for whatever remains unexplained**, not as the
default path.

**Behavior rules:**
- Do not offer simplified alternatives or option menus. The user wants the full clone.
- The visual comparison is the source of truth, not your memory, the quality gate, or the SSIM score. If the screenshots differ, the clone is not done.

**Architecture:** Playwright-only. No Chrome extension. Deterministic orchestrator + self-healing visual loop.

---

## API Key Setup (Required)

```bash
export GEMINI_API_KEY="your-key-here"
source ~/.zshrc
```

Get a key: [Google AI Studio](https://aistudio.google.com/apikey)

---

## Quick Start

```
/cloning https://example.com          # Full clone: extract + generate + refine
/cloning --refine ~/Desktop/my-clone  # Refine mode: skip generation, go straight to visual fix loop
```

---

## Workflow

Two modes: **Full Clone** (3 steps) and **Refine** (step 3 only).

### Mode Detection

If the user provides a URL → **Full Clone** (Steps 1-3)
If the user provides `--refine` + a directory path → **Refine Mode** (Step 3 only on existing clone)
If the user says "keep fixing", "push to 100%", "refine the clone" → **Refine Mode** on the most recent clone

In Refine Mode, do not regenerate the codebase from Gemini, because regeneration destroys previous fixes. Work with the existing code: compare against the original, fix differences, repeat.

### Step 0: Recover the real motion source (do this FIRST)

```bash
python scripts/recover_motion_source.py {url} /tmp/claude/cloning-{timestamp} \
    --routes "/,{other-routes}"
```

This captures every JavaScript file the page loads — including chunks that arrive only
via dynamic `import()`, which never appear as `<script src>` in the initial HTML and are
frequently where the animation code lives. It then resolves source maps, fingerprints the
animation libraries, and matches their exact versions on npm.

Read the printed `STRATEGY` line and act on it:

| Strategy | What it means | What to do |
|---|---|---|
| `source-maps` | The original unminified source was recovered | Read `motion-source/sources/` and transcribe the real logic. Best possible case. |
| `install-and-read` | Libraries identified, some with exact versions | Run the printed install commands. Read `motion-source/pretty/` for the choreography the libraries don't supply. |
| `infer-from-video` | Nothing recoverable | The videos are now justified. Proceed to Steps 1–3 as normal. |

**Install every `high` confidence package before writing animation code.** Deleting a
library you turned out not to need is easy. Discovering three passes into the refine loop
that your hand-rolled momentum will never match a real physics library is not.

Detection works on traces a minifier cannot remove: runtime warning strings, public API
names, DOM attribute hooks like `[data-smooothy]`, and embedded version literals such as
`.version="3.15.0"`. It deliberately does **not** look for quoted import specifiers,
because a bundler that inlines a library erases those entirely — which is why naive scans
report nothing on exactly the sites worth analysing.

Full detail, including the four-rung recovery ladder and what survives minification:
[motion-forensics.md](references/motion-forensics.md)

### Step 0.5: Decide the target framework

The orchestrator's `detect_frameworks.js` output names what the original was built with.
Use it.

Porting a site to Next.js when the original is Astro, Svelte or Nuxt means rewriting every
animation into a different component lifecycle, and lifecycle timing is exactly what makes
scroll-linked and load-triggered motion feel right. **When Step 0 finds a real animation
library, prefer scaffolding in the original's framework.** The default Next.js path below
stays correct for sites with little or no motion, and whenever the user asks for Next.

Match the original's animation stack regardless of framework choice. If it runs GSAP plus
Lenis, the clone runs GSAP plus Lenis at the same versions.

### Step 1: Run Orchestrator (automated extraction)

```bash
python scripts/clone_orchestrator.py {url} /tmp/claude/cloning-{timestamp}
```

The orchestrator runs ALL extraction phases automatically:
- Multi-viewport screenshots (mobile, tablet, desktop, wide) at 2x DPI
- Section-level close-up screenshots (auto-detected, up to 15)
- 3 video recordings (scroll, interactions, hover) via Playwright
- All 9 extraction scripts (frameworks, tokens, layout, components, SVGs, HTML, measurements, fonts, animations)
- Asset downloading (images + fonts via same-origin browser requests)
- Full page HTML extraction
- Clone contract generation

Output: structured directory with screenshots/, videos/, extraction/, assets/, clone-contract.json

If Playwright is not installed, run: `pip install playwright && playwright install chromium`

### Step 2: Generate Code (Gemini)

```bash
python scripts/gemini_api_v4.py --artifacts /tmp/claude/cloning-{timestamp} --output ~/Desktop/{site}-clone
```

The `gemini_api_v4.py` script automatically:
- Assembles the prompt from all extraction data
- Attaches all 3 videos (scroll, interactions, hover) as inline video/webm
- Attaches screenshots (viewport + section close-ups)
- Includes all extraction data (tokens, layout, measurements, fonts, etc.)
- Sends to Gemini 3.1 Pro with optimal parameters

Then run mandatory post-processing:
- **Pin the latest Next.js + React** (do this FIRST, before `npm install`):
  ```bash
  python scripts/pin_latest_versions.py ~/Desktop/{site}-clone
  ```
  This queries the live npm registry and rewrites `package.json` so `next`, `react`,
  `react-dom` (plus `eslint-config-next` and the React `@types`) are the newest stable
  release. Gemini's training data is always months stale (it defaults to Next 14 /
  React 18), so without this step every clone ships two majors behind. See
  [Framework Versions: Always Latest](#framework-versions-always-latest).
- Deploy downloaded assets to `public/images/`
- Self-host fonts in `public/fonts/` (rewrite @font-face)
- Enforce measurements against extracted data
- Verify content against extracted HTML

### Step 3: Push to 100% — Section-by-Section Visual Loop (MANDATORY)

This is where fidelity goes from 80% to 100%. The Gemini output is a FIRST DRAFT — it always needs polish. Your job is to compare every section of the clone against the original and fix every difference until they're indistinguishable.

**3a. Start the dev server:**
```bash
cd ~/Desktop/{site}-clone && npm install && npm run dev
```
> If you skipped straight to Refine Mode on an older clone, run
> `python scripts/pin_latest_versions.py <clone-dir>` before `npm install` so the
> clone is rebuilt on the latest Next.js + React, not whatever it was frozen at.

**3b. Missing section audit (FIRST — before any detail work):**

Screenshot the FULL PAGE of both original and clone. Count the major sections:
- Original sections: list every major section the original has, in order
- Clone sections: list what exists

If ANY section from the original is MISSING in the clone, build it FIRST:
1. Read the extraction data for that section (html-content.json, components.json)
2. Look at the original screenshot to understand the visual design
3. Create the missing component file
4. Add it to page.tsx in the correct position

**Do NOT proceed to detail polish until all sections exist.** Missing sections are the #1 source of fidelity loss.

**3c. Open the original site in Playwright MCP:**
```
browser_navigate → {original-url}
```

**3d. Section-by-section comparison loop:**

For EACH viewport-height section (scroll down one viewport at a time on BOTH sites):

1. **Screenshot the original** at current scroll position using `browser_take_screenshot`
2. **Navigate to the clone** → `browser_navigate → http://localhost:{port}`
3. **Scroll to the same position** → `browser_evaluate → window.scrollTo(0, {same_y})`
4. **Screenshot the clone** at the same scroll position
5. **Read BOTH screenshots** using the Read tool and compare pixel-by-pixel
6. **List EVERY difference** — be exhaustive, not just "looks close enough":

**Detail Checklist (check ALL of these for each section):**
- [ ] Badge/pill colors match? (not gray defaults — check extraction for exact hex)
- [ ] Active indicators sized correctly? (oversized active vs small inactive, not all same size)
- [ ] Decorative SVGs present? (timeline connectors, dividers — not replaced with simple lines)
- [ ] Background colors exact? (check extraction design tokens for exact hex)
- [ ] Font sizes match? (check extraction measurements, not Gemini's guess)
- [ ] Spacing/padding match? (check extraction computed measurements)
- [ ] Images loading? (check public/images/ for the file, fix `<Image>` props if needed)
- [ ] Hover states work? (hover on buttons, cards, links — do they match original?)
- [ ] Auto-cycling/timer animations running? (tabs, carousels — use GSAP pattern from gsap-patterns.md)
- [ ] Scroll animations firing? (scroll the clone — do elements reveal/highlight like the original?)
- [ ] Floating UI elements present? (tooltips, dropdowns, suggestion popups in hero)
- [ ] Border styles match? (rounded corners, border colors, shadow styles)
- [ ] Text content exact? (line breaks, em dashes, special characters)

7. **Fix each difference** by editing the component code directly:
   - Wrong badge color → `style={{ backgroundColor: "#exact-hex" }}`
   - Missing decorative SVG → extract from original HTML or create matching path
   - Wrong indicator size → adjust w-/h- classes (active should be 3-4x inactive)
   - Static grid should be auto-cycling → implement GSAP pattern from gsap-patterns.md
   - Missing hover image preview → add `useState` + `onMouseEnter` + `<Image>`
   - Missing floating UI → add positioned absolute element with proper content

8. **Scroll to next section** and repeat

**3e. Full-page verification pass:**

After fixing all sections, do ONE final full-page comparison:
1. Screenshot original full-page
2. Screenshot clone full-page
3. Read both and confirm overall match

**3f. REPEAT the entire page scan if needed (up to 3 full passes):**
```
Pass 1: Fix major structural differences (layout, missing sections, broken components)
Pass 2: Fix detail differences (colors, sizes, spacing, badges, indicators)
Pass 3: Fix micro differences (shadows, borders, font weights, hover states)
```

**3g. EXIT criteria — declare done ONLY when:**
- Every section has been compared side-by-side with screenshots
- No visible differences remain (or only dynamic content like dates/counters)
- All scroll animations fire at the correct positions
- All hover states match
- All auto-cycling components cycle with correct timing
- `compare_motion.py` reports every route matching **within the measured noise floor**
- `verify_head.py` exits 0 on every route

The noise floor is what turns "keep iterating" into something with an end. Read
[Verifying Motion](#verifying-motion-without-false-failures) before using it.

**3h. After visual loop exits, run code quality gate:**
Phase 9.5 automated checks (TypeScript compilation, no placeholders, etc.)

---

## Verifying Motion Without False Failures

Two mistakes make motion verification confidently wrong. Both are easy to make.

**Mistake 1: comparing at the same clock time.** Screenshotting both sites "3 seconds
after load" compares two *different moments in the animation*. Intro timelines usually
start on an event rather than on page load, and `document.fonts.ready` is the common one.
Fonts resolve far sooner from localhost than over a network, so the clone is routinely
further through its timeline than the original at any fixed moment. A perfectly correct
clone looks broken, and you go hunting for a bug that was never there.

Compare at the same **phase** instead: wait until the page stops changing, then measure.

**Mistake 2: treating every difference as a defect.** Physics-driven motion never settles
to the same sub-pixel position twice. Inertial carousels, smooth scroll and springs all
land slightly differently on each load, so a diff always shows differences and a loop that
chases them never terminates.

Measure the clone against **itself** across two loads first. That disagreement is the noise
floor, and differences at or below it carry no information about the original.

This is not theoretical. On one real clone a DOM comparison showed 19 of 263 elements
differing from the original — a convincing-looking defect list. The same clone compared
against itself differed by 24 of 263. Every apparent defect was smaller than the
measurement's own variance.

```bash
python scripts/compare_motion.py --original {url} --clone http://localhost:{port} \
    --routes "/,{other-routes}"
```

The script samples the clone twice to establish the noise floor, then reports only
differences that exceed it. Watch the settle times it prints: seeing the clone settle at
8785ms while the original settles at 6200ms is normal, and is exactly why fixed waits fail.

A noise floor of zero means the settle logic is working and the comparison is
deterministic. That is a good result, not a broken one — but confirm the probe actually
captured elements before believing it.

## Verify the Head, Not Just the Body

Titles, descriptions and social tags are invisible to every visual check in this pipeline.
Pixel diffs, SSIM scores and DOM geometry comparisons all read the body. A clone can match
the original exactly on screen while shipping a title the generator invented.

This has happened: a clone shipped a `/lab` page titled "Lab / Coming Soon" where the
original said "Lab / Experiments", plus an extra sentence bolted onto the description.
Every screenshot passed. Element-by-element DOM comparison passed. The defect reached
delivery because nothing ever read the head.

```bash
python scripts/verify_head.py --original {url} --clone http://localhost:{port} \
    --routes "/,{all-other-routes}"
```

Exits non-zero on any wrong or missing value. It separates real defects from the two
differences a rebuild legitimately causes: the `generator` tag naming your framework
version, and asset URLs changing when a hashed build path becomes a static one. Confirm
those asset URLs still resolve before shipping.

## Framework Versions: Always Latest

Every clone must be born on the **latest stable Next.js + React**, resolved at clone
time, never a version frozen into a model's training data.

**Why this is non-negotiable:** the code generator can only emit version numbers it saw
during training, and those go stale within weeks. Left alone, Gemini scaffolds Next 14 /
React 18 while the registry has already moved on (Next 16 / React 19 and climbing). A
fresh clone that boots two majors behind inherits old defaults, missing APIs, and
security patches it will never get. "Latest available" is a moving target, so the only
correct source of truth is the live npm registry, queried the moment the clone is built.

**Mechanism:** `scripts/pin_latest_versions.py` runs as the first post-generation step.
It calls `npm view <pkg> version` for `next`, `react`, `react-dom`, `eslint-config-next`,
and the React `@types`, then rewrites `package.json` with those exact versions before
`npm install` ever runs.

- **Compatibility is guaranteed by construction.** `next`, `react`, and `react-dom` are
  all resolved to their `latest` dist-tag in the same pass, and npm's latest Next is
  released against the latest stable React. `react` and `react-dom` are forced equal.
- **Only the framework moves.** Tailwind, TypeScript, PostCSS, and animation libraries
  (`gsap`, `framer-motion`) are deliberately left as-is. Bumping Tailwind v3 -> v4, for
  example, would break the generated CSS config. Freshening the framework is a different
  job from rewriting the styling engine.
- **No fallbacks.** If npm or the network is unreachable, the script exits non-zero with a
  clear message and writes nothing, rather than silently pinning a stale default. A
  visibly failed pin is safer than an invisibly outdated one.
- **Breaking changes are absorbed downstream.** Latest Next/React can introduce breaks
  (async `params`/`searchParams`, React 19 ref semantics). The Phase 9.5 `npx tsc --noEmit`
  hard gate catches them and the self-healing visual loop fixes them. That safety net is
  why targeting latest is safe, not reckless.

---

## Implementation Quality Rules

These rules are injected into every Gemini prompt. Full details: [implementation-quality.md](references/implementation-quality.md)

### Forbidden in Generated Output

- Emoji as image/icon placeholders → use downloaded assets or extracted SVGs
- Placeholder URLs (unsplash, picsum, placehold.co) → all assets local in public/images/
- Lorem ipsum text → use extracted real content
- Wireframe gray boxes → use real images from asset manifest
- Gratuitous effects not in original (neon glows, gradient text, extra shadows)
- Default shadcn styling without customization to match original
- External font CDN URLs → self-host in public/fonts/
- Hardcoded #000000 unless original uses it

### Animation Implementation (CRITICAL for fidelity)

**Use the libraries Step 0 identified, at the versions it found.** Substituting CSS plus
IntersectionObserver for a real animation library is the largest single source of fidelity
loss, because you are re-deriving easing curves and thresholds that were already available
to install.

The same rule applies beyond GSAP. If Step 0 reports `smooothy`, install `smooothy` — a
hand-rolled drag carousel will not reproduce its momentum or its snapping. If it reports
`lenis`, install `lenis`, because smooth scroll shifts the position of every scroll-linked
animation on the page and approximating it puts everything slightly out of step.

Ready-to-use GSAP code templates for the 3 most common patterns: [gsap-patterns.md](references/gsap-patterns.md)

| Pattern | Template | When to Use |
|---------|----------|-------------|
| Word-by-word scroll reveal | `gsap.fromTo(words, {opacity: 0.15}, {opacity: 1, scrub: 0.5})` | Manifesto/statement sections |
| Auto-cycling tabs + timer bar | `gsap.to({value:0}, {value:100, duration:6, onComplete: cycle})` | Tab systems with progress |
| Sticky scroll timeline | `ScrollTrigger.create({onEnter/onEnterBack: setActive})` | Process/workflow sections |

**CONFLICT RULE:** Never mix GSAP + Framer Motion in the same component.
CSS is acceptable ONLY for: hover transitions, continuous loops, and sites with NO animation library detected.

### Performance Guardrails

- **GPU-only animation:** transform, opacity, filter, clip-path. NEVER animate width/height/top/left/margin
- **prefers-reduced-motion:** Add to globals.css
- **Mobile (pointer: coarse):** Disable parallax, cap particles
- **Cleanup:** Every useEffect with GSAP/IntersectionObserver MUST return cleanup function

### Accessibility Minimum

- prefers-reduced-motion media query in globals.css
- Visible focus rings (never outline: none without replacement)
- aria-live="polite" on dynamically updating regions
- Keyboard-reachable interactive elements

---

## Code Quality Gate (Phase 9.5)

After evaluator passes, run automated code checks. Full details: [verification-phases.md](references/verification-phases.md#phase-95)

### Hard Gate (auto-fix, blocks delivery)

| # | Check | Command | Fix |
|---|-------|---------|-----|
| 0 | TypeScript compiles | `npx tsc --noEmit` | Fix type annotations |
| 1 | No placeholder URLs | `grep -r "unsplash\|picsum\|placeholder" src/` | Replace with assets |
| 2 | No emoji placeholders | `grep -rP '[\x{1F300}-\x{1FFFF}]' src/` | Replace with <img> or SVG |
| 3 | All image assets exist | Verify each `<img src="/images/...">` file | Copy from downloads |
| 4 | Head matches on every route | `python scripts/verify_head.py --original {url} --clone {local} --routes "..."` | Fix titles/meta; invisible to every visual check |
| 5 | Motion matches within noise floor | `python scripts/compare_motion.py --original {url} --clone {local} --routes "..."` | Fix only differences exceeding the floor |

### Soft Gate (warnings in report)

| # | Check | Command | Recommendation |
|---|-------|---------|----------------|
| 6 | Animation tool consistency | No dual gsap + framer-motion imports | Refactor per matrix |
| 7 | prefers-reduced-motion | `grep -r "prefers-reduced-motion" src/` | Add to globals.css |
| 8 | GPU-only properties | No animate width/height/top/left | Use transform |
| 9 | Fonts self-hosted | No fonts.googleapis.com | Download to public/fonts/ |

---

## Reference Files

| When you need... | Read this file | ~Tokens |
|-----------------|----------------|---------|
| Detailed extraction procedures | [extraction-phases.md](references/extraction-phases.md) | ~4K |
| Verification + evaluator details | [verification-phases.md](references/verification-phases.md) | ~3K |
| Implementation quality rules | [implementation-quality.md](references/implementation-quality.md) | ~2K |
| Gemini prompt template | [gemini-prompt-template-v4.md](references/gemini-prompt-template-v4.md) | ~2K |
| GSAP code templates (when GSAP detected) | [gsap-patterns.md](references/gsap-patterns.md) | ~1.5K |
| Recovering + verifying motion (read at Step 0) | [motion-forensics.md](references/motion-forensics.md) | ~2.5K |

---

## Known Limitations

- **WebGL/Three.js:** 3D elements not fully captured. Step 0 will name the library
  (`three`, `ogl`, `curtainsjs`) but shader logic still needs manual work.
- **Custom cursors:** Detected but not always replicated
- **Sound/Video:** Media files not cloned (only poster images)
- **Bespoke choreography:** Step 0 recovers libraries and versions, not the site's own
  hand-written timelines. Those still come from beautified bundles or from the videos.
- **Console-heavy sites:** some sites log huge base64 payloads (easter eggs, sprite data).
  Always filter console reads by pattern or the output will blow past tool limits.
- **Server-side behavior:** Only client-side appearance cloned
- **Authentication flows:** Login screens captured but not functional
- **Dynamic content:** Real-time data shows snapshot values
