# Changelog

All notable changes to OK-Skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/byosamah/ok-skills/releases/tag/v1.0.0
