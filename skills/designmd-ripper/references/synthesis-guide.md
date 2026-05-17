# Synthesis Guide — From Extracted Signal to Spec-Correct DESIGN.md

> Read this AFTER you have an `extraction-summary.json` and synthesis brief
> from `scripts/render_brief.py`, AND you have skimmed `references/spec.md`.
> This file is the mapping layer — how raw computed-CSS signal becomes
> the right shape in DESIGN.md.
>
> **Golden rule (verbatim from the linter research): read with tolerance,
> write with strictness.** The linter accepts `rgba()`, `transparent`, and
> CSS shorthand for `padding`, but the spec text says hex-only and a
> single Dimension. Always emit the strict form even if the source site
> uses a loose form. Your DESIGN.md should lint to 0 errors / 0 warnings
> / 1 info (the unavoidable `token-summary`).

## The strictness checklist (run mentally against every DESIGN.md you write)

Apply this checklist before you save the file. Each item maps to a
specific lint rule it prevents.

1. **`name:` is set in frontmatter.** (Schema requires it.)
2. **`colors.primary` is defined.** (Prevents `missing-primary`.)
3. **`typography:` has at least one entry.** (Prevents `missing-typography`.)
4. **Both `spacing:` AND `rounded:` are non-empty.** (Prevents two
   `missing-sections` info findings.)
5. **Every `{path.to.token}` you reference inside `components:` resolves to
   a value you actually defined.** (Prevents `broken-ref` errors.)
6. **Component property names are ONLY from this closed set:**
   `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`,
   `size`, `height`, `width`. Anything else triggers a `broken-ref`
   warning. (No `borderColor`, no `boxShadow`, no `gap` — express those
   in prose instead.)
7. **For any component with both `backgroundColor` and `textColor`,
   the contrast ratio of the resolved hex pair is ≥ 4.5:1.** When in
   doubt, pick a text color from one of the on-* tokens you defined
   (e.g. `on-primary`, `on-surface`) — these are paired for contrast
   by convention. (Prevents `contrast-ratio` warning.)
8. **Every color you put in `colors:` is referenced by at least one
   component.** Yes, including `primary` — the MD3-family exemption
   the README hints at is unreliable in practice. The simplest path
   to zero `orphaned-tokens` warnings is to make sure each color shows
   up as `"{colors.<name>}"` inside at least one component. If a color
   you defined isn't doing visible work in any component, delete it.
9. **`##` headings appear in this exact order**, with aliases allowed:
   Overview → Colors → Typography → Layout → Elevation & Depth →
   Shapes → Components → Do's and Don'ts. (Prevents `section-order`.)
10. **No duplicate `##` headings.** (Parser rejects the file entirely.)
11. **Dimensions use `px`, `em`, or `rem` ONLY.** No `%`, no `vw`, no
    bare numbers (unless intentional unitless `lineHeight` multiplier).
12. **Hex colors are quoted strings**, e.g. `primary: "#1A1C1E"`.
    Unquoted `#1A1C1E` is parsed as a YAML comment by some loaders.

## Source-of-truth mapping: extracted JSON → DESIGN.md fields

The cloning skill's orchestrator drops these files into
`<extraction_dir>/primary/extraction/`:

| JSON file              | Key fields                                                           | Maps to                 |
| :--------------------- | :------------------------------------------------------------------- | :---------------------- |
| `design-tokens.json`   | `colors.high/medium/low`, `typography`, `spacing`, `shadows`, `borderRadius`, `gradients`, `customProperties`, `timingConstants` | almost everything       |
| `fonts.json`           | `fontFaces`, `usedFonts`, `textRendering`                            | typography fontFamily   |
| `layout.json`          | `pageStructure`, `breakpoints`, `layoutMethod`                       | Layout section prose    |
| `components.json`      | `landmarks`, `sections`, `navigation`, `interactiveElements`         | Components + prose      |
| `measurements.json`    | computed widths/paddings/margins of key elements                     | spacing tokens, components |
| `animations.json`      | keyframes, durations, easings                                        | Optional prose mentions |

## Field-by-field mapping rules

### Frontmatter

#### `name`
- Try the site's `<title>` content without trailing brand suffix.
- If the title is generic ("Home"), use the host without TLD,
  title-cased — e.g. `linear.app` → `Linear`, `stripe.com` → `Stripe`.

#### `description` (optional)
- 1–2 sentences capturing the brand personality. Look at the hero
  copy + meta description. Skip if you cannot say something specific.

#### `colors`
- Pull from `design-tokens.json → colors.high` first (brand-critical),
  then merge in selected `medium` (interactive). Skip `low` unless the
  extracted brand list has fewer than 4 distinct hues.
- Convert any `rgb()` or `rgba()` to hex. For `rgba()` use alpha-hex
  (`#RRGGBBAA`) only if you cannot collapse the surface to an opaque
  equivalent — many extractor outputs include `rgba(255,255,255,0.1)`
  on a known background, in which case compute the opaque pair and
  emit hex.
- **Token naming:** use semantic roles, not raw values. Prefer this
  recommended set: `primary`, `secondary`, `tertiary`, `neutral`,
  `surface`, `on-surface`, `error`. Add tone variants (`primary-90`,
  `primary-10`) only if the site genuinely has light/dark variants of
  the same hue.
- **Pick `primary`:** the single color a designer would point to as
  "the brand color." For SaaS sites, this is almost always the CTA
  button background. If there is no obvious brand color (monochrome
  sites), use the darkest text color as `primary`.

#### `typography`
- One token per semantic level, NOT one per extracted size. Most sites
  have 6–10 meaningful sizes; the extractor often surfaces 20+.
  Cluster sizes within ~2px and pick one canonical value per cluster.
- Use these names where appropriate:
  `display-lg`, `headline-lg`, `headline-md`, `headline-sm`,
  `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`.
- `fontFamily`: use the first NON-fallback name (drop generic
  fallbacks like `sans-serif`, `system-ui`). If the value is an
  unquoted system stack, use `system-ui` literally.
- `fontWeight`: emit as a bare number (`600`), not a string. (Both are
  legal per spec; bare is cleaner.)
- `lineHeight`: prefer unitless multiplier (`1.5`) over a pixel value.
  Compute it as `lineHeightPx / fontSizePx` if the extractor gives
  pixels.
- `letterSpacing`: only emit if the value is non-zero. Use `em` units
  (compute as `letterSpacingPx / fontSizePx`) — produces consistent
  tracking across sizes.

#### `rounded`
- Cluster the extracted radii to at most 5 levels: `none`, `sm`, `md`,
  `lg`, `xl`, plus `full` for pill shapes (`9999px`).
- If the site has only one non-zero radius, define `sm` and `full`
  and leave the others off (keeping the section non-empty avoids
  `missing-sections`).

#### `spacing`
- Detect the base unit: usually 4px or 8px. If you see values
  `8, 16, 24, 32, 48, 64`, the base unit is `8px`.
- Emit a scale plus 1–2 named tokens for project-specific values:
  ```yaml
  spacing:
    unit: 8px
    xs: 4px
    sm: 8px
    md: 16px
    lg: 24px
    xl: 48px
    container-padding: 24px
    section-margin: 80px
  ```

#### `components`
- Start small: `button-primary`, `button-secondary`, `card`, `input`.
- Add a `-hover` variant for any button that has a clearly different
  hover state in `extraction/hover-matrix.json`.
- Cite tokens via `{path.to.token}` references — do not duplicate
  values. References make the file self-consistent and let downstream
  consumers (Stitch, agents) re-theme by changing the token, not the
  component.
- Skip components that don't have a visible identity on the page
  (no point defining `tooltip` if the site has no tooltips).

### Markdown body

Each section should be **2–4 short paragraphs** plus bullet lists where
appropriate. The prose answers "why" while the tokens answer "what."

#### `## Overview` (a.k.a. Brand & Style)
- Open with one declarative sentence on the brand personality, in the
  voice of a designer describing it to a peer.
- Identify the target user and the emotion the UI should evoke.
- Name the "house style" in 2–3 words (e.g. "editorial minimalism",
  "engineered atmospheric glass", "playful technical maximalism").

#### `## Colors`
- One bullet per top-level palette, with the hex inline:
  `- **Primary (#1A1C1E):** A deep ink used for headlines …`
- Use descriptive color names ("Midnight Forest Green") in addition
  to the systematic token names — the spec encourages prose names.

#### `## Typography`
- Name the font(s) and what role each plays.
- Note any treatments: small-caps, weight bumps over images,
  variable-axis settings, tabular numerals.
- Mention preferred line length / measure if discernible (often
  60–75ch for body text).

#### `## Layout` (a.k.a. Layout & Spacing)
- State the grid model (fluid / fixed-max-width / asymmetric).
- Give the base spacing unit.
- Note breakpoint cutoffs from `layout.json → breakpoints`.

#### `## Elevation & Depth`
- If the site is FLAT, explain how hierarchy is achieved (borders,
  tonal layers, weight).
- If the site uses SHADOWS, list each shadow level and its purpose.
- For glass UIs, describe backdrop-filter usage.

#### `## Shapes`
- One sentence on the shape language ("architectural sharpness",
  "soft organic", "geometric brutalist").
- Per-component radius application (cards, buttons, inputs).

#### `## Components`
- 3–5 subsections, one per category (buttons, inputs, cards,
  navigation, etc.). Each is 1–2 paragraphs describing behavior,
  states, and rationale.
- Do NOT redocument values that already appear in the tokens —
  the prose adds context, not duplication.

#### `## Do's and Don'ts`
- 4–8 bullet points, each one a clear DO or DON'T.
- These should be testable assertions a code reviewer could enforce
  ("Don't mix rounded and sharp corners in the same view") rather
  than vague guidance ("Be consistent").

## Common synthesis pitfalls

- **Over-extracting.** The site has 47 hex colors? Cluster them. A
  good DESIGN.md is the SMALLEST set of tokens that captures the
  visual identity, not the LARGEST.
- **Treating every interactive element as a component.** A site has
  five buttons that share styling — that is ONE component
  (`button-primary`), not five. Look for the platonic form, not the
  list of instances.
- **Inventing tokens to be thorough.** If the site has no shadows,
  don't fabricate `elevation-sm` / `elevation-md`. Empty `rounded`
  triggers `missing-sections`; empty `colors` does not — feel free
  to leave token groups empty when the site genuinely lacks them
  (but emit the corresponding info comment in prose).
- **Skipping prose because tokens "say it all."** The spec is
  explicit: prose provides RATIONALE, tokens provide VALUES. A file
  with rich tokens and 3-word section bodies is technically valid
  but not a useful DESIGN.md.

## Beyond atoms — capture molecule-level patterns

The canonical spec gives you four token surfaces (colors, typography,
spacing, rounded) and a closed set of 8 component sub-tokens. Real sites
have entire categories of design decision that **none of those token
surfaces can hold**. The skill's job is to surface those decisions in
**prose** so downstream builders aren't blindsided. The seven items
below were identified from a real audit and are the most-missed
categories. Walk this checklist before you save the file.

### 1. Font sources (CRITICAL)

For every `fontFamily` you declare in `typography:`, the prose must say:

- The **fallback chain** (e.g. `"Teg", "DM Serif Display", "Georgia", serif`).
- The **availability** — Google Fonts URL if applicable, "licensed face,
  see corporate brand assets" otherwise.
- If the face is a paid/proprietary one (Teg, Founders Grotesk, NB
  International), explicitly say so. The DESIGN.md will be used by
  builders who may not have a license — give them a graceful degradation
  path. Builders without this info pick wildly wrong fallbacks.

This goes in the Typography section under a "**Font sources.**" sub-paragraph.

### 2. Illustration & iconography style (CRITICAL)

This is the most-missed category in real-world DESIGN.md output. Builders treat
"there's an illustration here" as enough — it's not. **Illustration style is to
a brand what typography is**: a consumable design decision with its own rules,
vocabulary, and consequences if substituted carelessly. Treat it with the same
rigor as the Typography section.

**Step 1 — detect content slots beyond tokens.** Before writing component
descriptions, look at the screenshots and ask: do my cards/chips/sections
have content slots beyond the tokens?

- Illustration regions (isometric graphics, photographic compositions, product mockups)
- Icon slots (24-32px monochrome icons in feature cards)
- Logos / wordmarks (partner strips, footer)
- Multi-line subtitle/description text in addition to a label

The token surface cannot encode "the upper 60% of this card is an illustration."
Put it in prose.

**Step 2 — describe the illustration LANGUAGE, not just the slot.** Add a
`### Illustration & Iconography` subsection under `## Shapes` (the spec's
section taxonomy doesn't have a dedicated illustration section, so Shapes is
the most natural fit since both deal with visual vocabulary). For each
distinct visual language the site uses (often two: illustrations + icons),
specify:

- **Technique** — isometric / flat / line / hand-drawn / 3D-render / photographic. Be specific.
- **Style register** — matte vs glossy, friendly vs technical, editorial vs clinical.
- **Subject vocabulary** — what does the brand draw? Financial primitives? Abstract geometry? Human figures? Product mockups?
- **Palette** — drawn from token set, or off-palette accents? If on-palette, which tokens?
- **Stroke / fill rules** — outlines? Filled volumes? Both? Stroke weight?
- **Composition inside components** — where does illustration sit relative to text? What proportion of the surface?
- **Icon family** — line vs filled, weight, cap/join style, size range, color usage.
- **Photography policy** — does the brand use photos at all? Where? Anti-pairings with illustrations?

**Step 3 — anti-patterns.** End the section with what NOT to do. ("Don't substitute
photographic stock imagery for the isometric illustrations." "Don't recolor icons
in the accent color — icons stay quiet in neutral or primary.")

A builder substituting flat doodles for isometric volumes will visibly break the
brand even if every token is correct. The illustration section is what prevents
that.

### 3. Motion language

If the site has any non-trivial motion — carousel, marquee, hover
transitions, scroll-triggered reveals, pulsing status dots — add a
**`### Motion`** subsection under `## Elevation & Depth` documenting:

- **Default transition duration** for color/opacity (commonly 120-200ms).
- **Easing curves** (often `ease`, `ease-in-out`, or a custom cubic-bezier).
- **Pattern-specific timings**: marquee loop length, carousel slide
  duration, pulse intervals.

The canonical spec does not surface motion as tokens — treat the prose
values as binding contracts.

### 4. Component variant completeness

For every interactive component, document the variants the site uses:

- **default**
- **hover** (almost always present; check `hover-matrix.json`)
- **focus-visible** (keyboard accessibility; often absent in extraction
  but mandatory for production)
- **disabled** (lower opacity or a desaturated variant)
- **loading** (if the component shows pending state — buttons during
  form submission, etc.)

Encode the hover variant as a separate component (`button-primary-hover`)
when the spec allows. Document focus and disabled in prose since their
"differences" are often `opacity`/`box-shadow`/`outline` which aren't in
the closed sub-token set.

### 5. Multi-lane container widths

Most real sites have **2-3 container widths**, not one:

- **Narrow** (~600-700px) — body prose, hero copy, focused reading.
- **Default** (~1024-1200px) — the most common content area.
- **Wide** (~1240-1440px) — system grids, nav, footer, dashboards.
- **Full-bleed** — viewport edge to edge for hero images, footer bands.

Add them as `spacing.container-narrow`, `spacing.container-wide` (or
similar) tokens, and explain in the Layout section's prose which content
goes in which lane. A single `max-width` is almost always under-spec.

### 6. Closed-set escape hatches

The canonical spec's component sub-tokens are CLOSED to exactly 8:
`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`,
`size`, `height`, `width`. Anything else triggers a `broken-ref`
warning.

In practice you will routinely need:

- **`borderColor`** / **`borderWidth`** — feature cards on tinted
  backgrounds, secondary buttons, inputs.
- **Asymmetric padding** (`paddingX`, `paddingY`, or shorthand
  `0 24px`) — buttons in particular almost never want equal x/y padding.
- **Box shadow** — even on flat designs, code blocks and modals often
  carry one shadow.
- **Motion properties** (duration, easing, delay).

**These don't fit the token surface.** Encode them as CSS-binding rules
in component prose (e.g., "feature cards sit on tinted bg with a 1px
hairline at `#E5E7EB`"). And add a Do/Don't bullet warning builders to
encode hairline outlines, motion durations, and padding splits in CSS,
not as token references.

### 7. Status color taxonomy

Always check for status colors, even if they're not visually prominent:

- **success** (often green or mint)
- **warning** (often amber or orange)
- **error** (often red)
- **info** (often blue or neutral)

If the site visibly uses a status color (e.g., a green dot, a red error
border, an orange "beta" badge), include it in `colors:` and reference
it from at least one component (`status-error-dot`, `badge-warning`,
etc.) so it doesn't trigger `orphaned-tokens`.

If the site has no visible status colors, you may still add a
half-line note in the Colors section: "Status colors are not part of
this brand's homepage surface — define them at integration time using
the closest extracted hues." This prevents builders from inventing
clashing values in `Do's and Don'ts` violation scenarios.

### Quick mental test

Before saving, ask yourself: **could a builder produce a brand-new
pricing page, login page, and docs landing using only this file?** If
the answer requires them to invent things (form input styles, icon
treatment, motion timing, container widths for non-hero sections), go
back and either add prose or, where possible, add tokens.

## Validation loop

After writing the file:

```bash
npx @google/design.md lint /path/to/DESIGN.md
```

Expected target:
- `errors: 0`
- `warnings: 0`
- `infos: 1`  (the unavoidable `token-summary`)

If warnings appear, walk the table in `references/linting-rules.md`
and patch the file. The most common are `orphaned-tokens` (define a
color but never use it in a component — either reference it or
remove it) and `contrast-ratio` (component `textColor` on
`backgroundColor` is below 4.5:1 — pick a different `textColor` or
use the darker/lighter variant in `colors`).

If the user does not have `npx` or `@google/design.md` available,
fall back to the manual checklist at the top of this file.
