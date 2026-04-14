# OK-Skills

A curated collection of production-ready skills for [Claude Code](https://claude.ai/code) and [Codex](https://openai.com/index/introducing-codex/) by [Osama Khalil](https://osama.me).

OK-Skills gives your AI coding assistant deep expertise in **Three.js game development** and **pixel-perfect website cloning**. Each skill is a self-contained knowledge base with guides, reference documentation, and executable scripts that the AI reads and follows to produce expert-level output.

---

## Installation

### Claude Code

```bash
claude plugins install --from github:byosamah/ok-skills
```

After installation, the skills appear in your skill list and can be invoked by name.

### Codex

```bash
codex install github:byosamah/ok-skills
```

### Manual Installation

```bash
git clone https://github.com/byosamah/ok-skills.git ~/.claude/plugins/ok-skills
```

Then register it in your Claude Code plugins configuration.

---

## Skills

### 🎮 threejs-master

**The definitive Three.js game-building skill.** Teaches your AI assistant to build production-grade 3D web experiences and games using modern Three.js (r170+ with ES module import maps).

#### What It Does

When you invoke `/threejs-master`, your AI gains comprehensive knowledge of Three.js scene setup, lighting, geometries, materials, animations, controls, GLTF model loading, game architecture, collision detection, input handling, audio systems, UI overlays, and performance optimization. It doesn't just know the API — it knows the *patterns* that make 3D apps work well.

#### What's Inside

**Main Guide (SKILL.md)** covers:
- Scene graph mental model and philosophy
- Quick-start HTML template with import maps (r170+)
- 7 geometry primitives (Box, Sphere, Cylinder, Torus, Plane, Cone, Icosahedron)
- 5 material types with full property reference (Basic, Standard, Physical, Lambert, Phong)
- 4 light types with shadow configuration (Ambient, Directional, Point, Spot)
- Camera controls setup (OrbitControls)
- Animation patterns (rotation, wave motion, mouse-driven interaction)
- Game architecture overview (7 core systems)
- Common scene patterns (rotating cube, particle field, parallax backgrounds)
- Hex color reference guide
- Anti-patterns to avoid
- Scenario-specific guidance (portfolio, game, data viz, background effect, product viewer)

**11 Deep-Dive Reference Guides:**

| Guide | What It Covers |
|-------|---------------|
| `coordinate-system.md` | Right-handed axes, GLTF default orientation (-Z forward), camera-relative movement, Object3D forward convention, rotation cheat sheet |
| `gltf-loading-guide.md` | 6 loading patterns from basic to advanced: simple load, promise-based, with fallback, batch loading, caching with `SkeletonUtils.clone()`, model normalization |
| `game-loop-and-state.md` | State machine pattern, delta-time with capping, time scaling, screen effects (shake, flash, zoom), parallax layers, object pooling, fixed game camera |
| `animation-guide.md` | Finding and playing animations, crossfading with guards (prevents frame freezing), safe animation selection, facing direction for side-scrollers, squash and stretch |
| `collision-and-physics.md` | AABB collision (Box3), sphere collision, raycasting for ground detection and mouse picking, trigger zones, collision layers/masks, spatial hashing, physics engine integration (Cannon-es, Rapier3D) |
| `input-handling.md` | Keyboard state tracking, input action mapping abstraction, Gamepad API, touch controls (virtual joystick pattern), touch buttons, pointer lock for FPS, preventing default browser behavior |
| `audio-guide.md` | AudioListener setup, non-positional audio (music, UI sounds), positional 3D audio (spatial SFX), SFX pool pattern for rapid fire, music crossfade, mute/volume controls, AudioContext resume |
| `ui-systems.md` | HTML overlay approach, HUD elements (score, timer, lives), health/progress bars, floating damage text with animation, menu screens (start, pause, game over), loading screens with progress, minimap |
| `scene-management.md` | `dispose()` contract for GPU cleanup, level loading/unloading, scene transitions (fade and crossfade), asset manifest and preloader pattern, memory cleanup checklist, leak detection |
| `advanced-rendering.md` | Post-processing (Bloom effect), custom shaders (ShaderMaterial), text sprites, raycasting techniques, environment maps, `InstancedMesh`, `BatchedMesh` (r170+), physics integration, TypeScript setup, debug helpers |
| `performance-guide.md` | Profiling with Stats.js and `renderer.info`, draw call reduction (merge geometry, InstancedMesh, BatchedMesh), LOD (Level of Detail), texture optimization (compression, atlasing), frustum culling, shadow optimization, mobile-specific tricks, object pooling, memory leak detection, performance budget, quick wins checklist |

**Calibration Scripts:**
- `gltf-calibration-helpers.mjs` — Drop-in module that visualizes axes, bounding boxes, forward direction arrows, and label sprites on any loaded GLTF model. Verify your model's reference frame in ~60 seconds.
- `install-gltf-calibration-helpers.py` — Copies the helper module into your project with a single command.

#### Usage

```
/threejs-master
```

**Example prompts after invoking:**
- "Build a 3D space shooter with WASD controls and particle explosions"
- "Create a product viewer with orbit controls and environment lighting"
- "Add collision detection and a health bar to my game"
- "Optimize my Three.js scene — it's running at 20fps on mobile"

#### Requirements

None. This is a pure knowledge skill — no API keys, no external dependencies. It works entirely by teaching your AI assistant Three.js patterns and best practices.

---

### 🌐 cloningv6

**Clone any website to 100% fidelity.** Not 90%. Not "close enough." 100%. Uses a 13-phase extraction pipeline powered by Gemini 3.1 Pro, with self-healing visual verification loops that push relentlessly until every section, every badge color, every animation, every pixel matches the original.

#### What It Does

When you invoke `/cloningv6`, your AI orchestrates a complete extraction-to-generation pipeline: it captures the target site from every angle (screenshots, videos, computed styles, assets, animations), feeds everything to Gemini 3.1 Pro for code generation, then enters a visual verification loop comparing the clone against the original until fidelity reaches 100%.

#### How It Works — The 13-Phase Pipeline

| Phase | Name | What Happens |
|-------|------|-------------|
| 0 | Framework Detection | Identifies CSS frameworks (Tailwind, Bootstrap), JS animation libs (GSAP, Framer Motion), icon libraries, and component systems |
| 0.5 | Interactive Exploration | Scrolls the page, hovers elements, clicks interactive components — records everything |
| 1 | Multi-Viewport Screenshots | Captures the full page at 4 viewport widths (mobile, tablet, desktop, wide) at 2x DPI |
| 2 | Asset Downloading | Downloads all images, SVGs, fonts, and media files |
| 3 | Design Token Extraction | Extracts colors, typography, spacing, and effects with confidence scoring (HIGH/MEDIUM/LOW) |
| 4 | Layout Analysis | Maps grid/flexbox structures, z-index layers, and responsive breakpoints |
| 5 | Component Mapping | Identifies ARIA landmarks, UI patterns, section structures |
| 6 | Animation Recording | Records scroll animations, hover state changes, and interaction videos |
| 6.5 | HTML & Measurements | Extracts section-level HTML content and exact pixel measurements via `getComputedStyle()` |
| 7 | Gemini Code Generation | Assembles all extracted data into a structured prompt, sends to Gemini 3.1 Pro with completeness gates |
| 8 | Post-Processing | Deploys downloaded assets, self-hosts fonts, enforces exact measurements, verifies content accuracy |
| 9 | Visual Verification Loop | Compares clone screenshots against originals using SSIM scoring — loops until match |
| 9.5 | Code Quality Gate | Hard checks (TypeScript, no placeholders) and soft checks (animation consistency, accessibility) |

#### What's Inside

**Main Guide (SKILL.md)** covers:
- Complete workflow documentation for all 13 phases
- Two operation modes: Full Clone (give it a URL) and Refine Mode (`--refine` flag for existing clones)
- Implementation quality rules and forbidden patterns
- Behavior rules: maximum effort, never declare done early, visual comparison is the source of truth

**5 Reference Files:**

| Reference | What It Covers |
|-----------|---------------|
| `extraction-phases.md` | Detailed procedures for Phases 0–6.5 with error handling and parameter tuning |
| `verification-phases.md` | Generation (Phase 7), post-processing (Phase 8), verification loop (Phase 9), and code quality gate (Phase 9.5) |
| `implementation-quality.md` | Forbidden patterns (anti-slop rules), animation tool selection matrix, performance guardrails, accessibility minimums, TypeScript gotchas, shared patterns |
| `gsap-patterns.md` | 5 production-ready GSAP + ScrollTrigger patterns for React/Next.js: word-by-word scroll reveal, auto-cycling tabs, sticky scroll timeline, entrance animations with stagger, horizontal scroll sections |
| `gemini-prompt-template-v4.md` | Complete v6.0 prompt structure for 98-100% fidelity, optimal Gemini parameters, multimodal content ordering, troubleshooting guide |

**19 Extraction & Generation Scripts:**

*JavaScript (11 scripts) — run in-browser via Playwright:*
- `detect_frameworks.js` — Identifies CSS/JS/icon/component libraries
- `extract_design_tokens_v4.js` — Confidence-scored color, typography, and effect tokens
- `analyze_layout.js` — Grid, flexbox, z-index, and responsive breakpoint extraction
- `analyze_components.js` — ARIA landmarks and component pattern detection
- `extract_svgs.js` — Inline SVG and icon sprite extraction
- `extract_html_content.js` — Section-level HTML with headings, links, images, buttons, cards
- `extract_computed_measurements.js` — Exact pixel measurements via `getComputedStyle()` and `getBoundingClientRect()`
- `extract_font_assets.js` — `@font-face` rules, variable font detection, text rendering properties
- `extract_js_animations.js` — JS bundle animation forensics (fallback when runtime recording fails)
- `map_animations_v4.js` — Legacy animation detection (Phase 6 fallback)
- `capture_hover_matrix.js` — Hover state capture across ~200 CSS selectors

*Python (8 scripts) — orchestration, recording, API:*
- `clone_orchestrator.py` — Master orchestrator that runs all extraction phases automatically
- `clone_website_v4.py` — Reference implementation of the full extraction workflow
- `capture_multi_viewport.py` — Multi-viewport screenshot capture at 2x DPI
- `record_scroll.py` — Video recording of scroll-triggered animations
- `record_interactions.py` — Video recording of interactive element states
- `stitch_screenshots.py` — Combines screenshots into composite images
- `gemini_api_v4.py` — Gemini 3.1 Pro API integration with optimal parameters
- `verify_clone.py` — SSIM-based verification scoring of clone vs original

#### Usage

```
/cloningv6
```

**Full clone:**
```
Clone https://example.com to 100% fidelity
```

**Refine an existing clone:**
```
/cloningv6 --refine
The hero section animation timing is off — fix it to match the original
```

**Example prompts:**
- "Clone https://linear.app landing page pixel-for-pixel"
- "Clone this site but swap the color palette to my brand colors"
- "The footer layout doesn't match — run the verification loop again"

#### Requirements

| Requirement | Details |
|------------|---------|
| `GEMINI_API_KEY` | Environment variable — get one at [ai.google.dev](https://ai.google.dev) |
| Playwright | For browser automation during extraction (`npx playwright install`) |
| Python 3.12+ | For orchestration and recording scripts |
| Node.js | For in-browser extraction scripts |
| ImageMagick | *Optional* — for SSIM visual comparison scoring |

#### Known Limitations

- WebGL content (Canvas-rendered graphics can't be extracted)
- Custom cursors and pointer effects
- Sound and video playback behavior
- Server-side dynamic behavior (API-driven content)
- Authentication-gated pages
- Highly dynamic real-time data (stock tickers, live feeds)

---

## Requirements Overview

| Requirement | threejs-master | cloningv6 |
|------------|:-:|:-:|
| Claude Code or Codex | ✅ | ✅ |
| API Keys | — | `GEMINI_API_KEY` |
| Python 3.12+ | — | ✅ |
| Node.js | — | ✅ |
| Playwright | — | ✅ |
| ImageMagick | — | Optional |

---

## Adding to Your Project

**Global install** (available in all projects):
```bash
claude plugins install --from github:byosamah/ok-skills
```

**Project-scoped** (available only in a specific project):
```bash
claude plugins install --from github:byosamah/ok-skills --scope project
```

After installation, skills appear in your skill list. Invoke them by name (`/threejs-master`, `/cloningv6`) or let Claude auto-detect when they're relevant to your task.

---

## Contributing

Want to add a skill or improve an existing one? Contributions are welcome.

### Adding a New Skill

1. Create a directory under `skills/` with your skill name:
   ```
   skills/your-skill-name/
   ├── SKILL.md           # Required — main skill file
   ├── references/        # Optional — supporting documentation
   └── scripts/           # Optional — executable scripts
   ```

2. Write your `SKILL.md` with YAML frontmatter:
   ```markdown
   ---
   name: your-skill-name
   description: One-line description of what the skill does
   ---

   # Your Skill Name

   Skill content here...
   ```

3. Optional frontmatter fields:
   - `model: opus` — require a specific model
   - `context: fork` — run in a forked context
   - `effort: max` — set effort level

4. Open a PR with your skill. Include a description of what it does and example usage.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Author

**Osama Khalil** — Product designer and builder.

- Website: [osama.me](https://osama.me)
- GitHub: [@byosamah](https://github.com/byosamah)
- Skills: [skills.osama.me](https://skills.osama.me)
