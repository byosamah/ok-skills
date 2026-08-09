# Changelog

All notable changes to OK-Skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-08-09

### Added

- **gauntlet-loop v1.0**. An implementation of [Matt Shumer's Gauntlet Loop](https://somethingbig.ai/gauntlet-loop), the prompting method behind Claude of Duty. Turns "build me X" into a run that keeps improving against a reference it can lose to, instead of stopping at the first decent result. Two-phase by design: it interviews for a goal and a real quality bar, captures that bar as inspectable files on disk, and writes a short Shumer-style prompt, then hands off to a **clean-room** Claude Code session where a lead agent splits the goal into the smallest independently judgeable pieces and pairs each with a builder and a separate harsh critic doing blind A/B against the bar. Ships 3 reference files (`bar-catalog.md` for sourcing a real bar across seven domains, `prompt-patterns.md` with the original prompt plus worked adaptations, `clean-room.md` for launch mechanics and troubleshooting) and 1 script (`launch-gauntlet.sh`).
- **Clean-room launch.** The launcher starts the run with zero MCP servers, zero skills, and no global `CLAUDE.md`, while leaving subagents, workflows, shell, file access, and web access intact. This is not in the source article: it follows from the article's first rule, since every installed skill and MCP server is a route already chosen for the agent, and persona rules in a global `CLAUDE.md` propagate into every spawned critic. The flag combination was verified empirically against Claude Code 2.1.226.

### Changed

- README intro, Requirements Overview table, and invoke list updated to include the Gauntlet Loop.
- Plugin and marketplace descriptions extended, with `gauntlet-loop`, `gauntlet`, `multi-agent`, `subagents`, `agent-orchestration`, `prompting`, and `quality-loop` added to keywords for discoverability.

---

## [1.3.1] - 2026-07-26

### Added

- **`cloning` v6.1: clones are always born on the latest stable Next.js + React.** New `scripts/pin_latest_versions.py` queries the live npm registry for `next`, `react`, `react-dom`, `eslint-config-next`, and the React `@types`, then rewrites the generated `package.json` before `npm install` ever runs. A code generator can only emit version numbers it saw during training, so Gemini scaffolds Next 14 / React 18 while the registry has moved on. Every clone was shipping two majors behind, inheriting old defaults, missing APIs, and security patches it would never get. The script runs as the first post-generation step, and Refine Mode on an older clone can run it standalone before rebuilding.

### Changed

- **`cloning` now defaults to CSS `@keyframes` instead of GSAP** for fade, slide, and stagger reveals. GSAP under React Strict Mode (18+, including 19) double-invokes `useLayoutEffect` in development, leaving elements stuck at partial opacity or mid-transform. CSS keyframes run on the browser's compositor thread, outside React's lifecycle, so they are immune. GSAP is now reserved for what it is actually needed for: scroll-linked scrub and pinned sections. Applied across `references/extraction-phases.md`, `references/implementation-quality.md`, and `references/gemini-prompt-template-v4.md`.
- **`cloning` survives very tall pages.** `scripts/clone_orchestrator.py` catches Chrome's ~16384px maximum screenshot texture height and falls back to a capped clip, instead of letting one oversized viewport kill the entire capture pipeline.
- **`cloning` codegen prompt no longer hardcodes framework versions.** `scripts/gemini_api_v4.py` instructs the model to emit `"latest"` for `next`, `react`, and `react-dom` and leave exact pinning to the post-processing step, so the model's job is the code and not the version numbers.
- `package.json` and `.claude-plugin/plugin.json` bumped to `1.3.1` together, keeping the two version strings in sync.

---

## [1.3.0] - 2026-05-27

### Added

- **branded-design v1.0**. Generate on-brand social media posts with a two-step compositing pipeline: Nano Banana produces the base visual (a photo, illustration, or scene with no brand assets baked in), then a Pillow pipeline layers the real brand assets on top (actual logo PNGs, real font TTF rendering, real decorative element files) for pixel-perfect fidelity that AI-baked assets cannot match. Adapts to six brand archetypes (photo-person, photo-product, illustration, text-card, editorial, minimal), each with its own layer stack. Includes a first-run brand interview, calibration from example posts, Latin and Arabic/RTL text rendering, and a self-improving learning loop. Ships 3 reference files (brand.yaml schema, per-archetype prompt patterns, platform formats), 5 scripts (`setup_brand.py`, `validate_brand_kit.py`, `generate_post.py`, `composite_post.py`, `log_and_learn.py`), and a `brand-kit-template/` asset scaffold.

### Changed

- README tagline, intro, Requirements Overview table, and invoke list updated to include on-brand social media post generation.
- Plugin description and keywords expanded with `social-media`, `instagram`, `brand-design`, and `compositing` for discoverability.
- `package.json` version aligned to `1.3.0` (it had drifted to `1.1.0`).

---

## [1.2.0] - 2026-05-17

### Added

- **designmd-ripper v1.0**. Generate a 100% spec-compliant Google DESIGN.md file from any public website URL. Deeply extracts the live design system via Playwright (colors, typography, spacing, components, layout, fonts, shadows), proposes subpages for user approval, then synthesizes a DESIGN.md conforming to the canonical Google design.md schema with zero lint errors. Output is portable to Stitch, Tailwind, and Figma. Includes 5 reference files (full spec, synthesis guide, linting rules, canonical example, CLI reference), 3 scripts (`extract.py` for Playwright extraction, `render_brief.py` for synthesis, `lint.sh` for validation), and 1 template asset.

### Changed

- README tagline and intro updated to mention design-system extraction alongside the existing skills.
- Plugin description and keywords expanded with `design-md`, `design-system`, `design-tokens`, `design-spec`, and `brand-spec` for better discoverability.

---

## [1.1.0] - 2026-05-05

### Added

- **tony-fadell v1.0**. Spec/PRD reviewer in Tony Fadell's voice. Scores a markdown spec 0 to 10 on each of the Core 5 pillars from his book *Build* (Story-first, Painkiller-vs-Vitamin, V1 Painted-Door, Heartbeats, Make-the-Invisible-Visible) and writes a sidecar review file with composite score, per-pillar diagnoses citing specific spec lines, and Fadell-flavored rewrites of weak sections. Includes 2 reference files (pillar rubrics, source canon) and 1 asset (sidecar template).

### Changed

- README tagline broadened to reflect the addition of product/spec review alongside Three.js and cloning.
- Plugin description and keywords updated to surface product, PRD, and spec-review use cases.

---

## [1.0.0] - 2026-04-14

### Added

- **threejs-master v1.0** — The definitive Three.js game-building skill. Scene setup, lighting, geometries, materials, animations, controls, GLTF models, game architecture, collision, input, audio, UI, and performance optimization. Modern ES modules, Three.js r170+ APIs. Includes 11 deep-dive reference guides and GLTF calibration scripts.
- **cloning v6.0** — Clone any website to 100% fidelity using Gemini 3.1 Pro. 13-phase extraction pipeline with self-healing visual verification loops. Includes 5 reference files and 19 extraction/generation scripts (JavaScript + Python).
- Plugin metadata (`.claude-plugin/plugin.json`) for Claude Code and Codex installation.
- Comprehensive README with installation instructions, detailed skill documentation, requirements, and contributing guide.

---

## Skill Version History

### cloning

#### v6.0 (Current)
- Major Phase 6 rewrite: replaced static JS bundle analysis with runtime animation recording
- New `record_runtime_animations.js` intercepts `Element.animate()`, `MutationObserver`, `requestAnimationFrame`, and GSAP calls
- Previous v4 approach failed on ~70% of modern bundled ES modules — v6 fixes this
- Added Phase 0.5: Interactive Exploration (scroll, hover, click recording)
- Added Phase 9.5: Code Quality Gate (hard checks + soft checks)

#### v5.0
- Removed black/white color exclusion (now includes `#000000` and `#ffffff`)
- Increased inline SVG icon capture: 30 → 100
- Enhanced hover matrix: 50 → 200 selectors
- Expanded design token colors: added up to 20 LOW confidence colors
- Added 8 new CSS properties: `text-shadow`, `filter`, `backdrop-filter`, `mix-blend-mode`, `clip-path`, `border` properties, `text-decoration`, `aspect-ratio`
- Lowered spacing threshold for gap detection: 30px → 8px
- Raised card limits: 8 → 20 per section
- Raised paragraph limits: 5 → 15 per section
- Raised tween signature limit: 30 → 100

#### v4.0
- Introduced confidence-scored design tokens (HIGH/MEDIUM/LOW)
- Added Gemini prompt template v4 with structured multimodal input
- Added framework detection (Tailwind, GSAP, Framer Motion, etc.)
- Added full grid/flexbox/z-index layout analysis
- Added ARIA + semantic component mapping
- Added full SVG extraction pipeline

#### v3.0
- Initial multi-phase extraction pipeline
- Basic layout analysis
- Manual animation configuration
- No framework detection or confidence scoring

### threejs-master

#### v1.0 (Current)
- Complete Three.js skill covering r170+ APIs with ES module import maps
- 11 deep-dive reference guides: coordinate system, GLTF loading (6 patterns), game loop & state, animation, collision & physics, input handling, audio, UI systems, scene management, advanced rendering, performance
- GLTF calibration helper scripts for reference frame verification
- Scenario-specific guidance for portfolio, game, data viz, background, and product viewer use cases

### tony-fadell

#### v1.0 (Current)
- First-person Tony Fadell persona for spec/PRD review with rules for voice, scoring procedure, and review-writing workflow
- Core 5 pillar scoring: Story-first, Painkiller-vs-Vitamin, V1 Painted-Door, Heartbeats, Make-the-Invisible-Visible
- Pillar rubrics with calibration anchors and disqualifying patterns (0 to 10 scoring)
- Source canon mapping every quote and framing back to *Build* chapters, podcasts, and posts
- Sidecar template with composite score, per-pillar diagnoses, and copy-pasteable rewrites of weak sections

### designmd-ripper

#### v1.0 (Current)
- Playwright-based extraction of computed-style design tokens (colors, typography, spacing, shadows, radii, motion) from any public URL
- Spec-correct synthesis to Google DESIGN.md: YAML frontmatter tokens plus body-section rationale prose
- 5 reference files: full canonical spec (`spec.md`), synthesis guide with 12-item strictness checklist, all 8 lint rules with trigger conditions, the official "Atmospheric Glass" canonical example, and `@google/design.md` CLI reference
- 3 scripts: `extract.py` (Playwright extraction pipeline), `render_brief.py` (raw signals to DESIGN.md synthesis), `lint.sh` (validation against canonical linter for 0 errors, 0 warnings)
- Output portable to Stitch, Tailwind theme generators, and Figma importers
- Skill metadata: `model: opus`, `context: fork`, `effort: max`

### branded-design

#### v1.0 (Current)
- Two-step compositing pipeline: Nano Banana base visual plus Pillow compositing of real brand assets (logo PNGs, font TTFs, decorative element PNGs)
- Six brand archetypes with per-archetype pipelines: photo-person (rembg z-ordering, elements bleed behind the subject), photo-product, illustration, text-card (no AI call, fully Pillow-rendered), editorial (contrast treatment over a full-bleed photo), minimal
- First-run Setup Mode: brand interview, `brand.yaml` creation, font setup, asset-placement guidance, calibration from example posts, validation, optional rename to `{brand-name}-brain`
- Calibration constants plus per-brand `calibration.yaml` for pixel-accurate logo, text, and element positioning
- Latin and Arabic/RTL text rendering (`arabic-reshaper` plus `python-bidi` reordering)
- Self-improving learning loop via `log_and_learn.py` and Deep Review Mode
- Nano Banana image backend resolved via the `NANO_BANANA_SCRIPT` environment variable (the `text-card` archetype needs no backend)

[1.3.0]: https://github.com/byosamah/ok-skills/releases/tag/v1.3.0
[1.2.0]: https://github.com/byosamah/ok-skills/releases/tag/v1.2.0
[1.1.0]: https://github.com/byosamah/ok-skills/releases/tag/v1.1.0
[1.0.0]: https://github.com/byosamah/ok-skills/releases/tag/v1.0.0
