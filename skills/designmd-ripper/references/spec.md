# DESIGN.md Specification — Complete Reproduction

> Source: `docs/spec.md` in `google-labs-code/design.md` (main branch),
> reproduced verbatim. This file is generated upstream from
> `packages/cli/src/linter/spec-config.yaml` + a Stitch MDX template via
> `bun run spec:gen`.
>
> The Stitch docs pages at `stitch.withgoogle.com/docs/design-md/*` are
> JavaScript-rendered single-page-app routes — WebFetch returns only the
> shell title "Stitch - Design with AI" because the body is hydrated
> client-side. The GitHub repo's `docs/spec.md` is the same content and is
> the canonical, machine-generated source of truth. Lint rule severities
> and CLI flags below are also cross-checked against the linter and CLI
> source files (`packages/cli/src/linter/linter/rules/*.ts`,
> `packages/cli/src/commands/*.ts`).
>
> Format version: **alpha**

---

<!-- Generated from spec.mdx + spec-config.ts | version: alpha -->
<!-- Do not edit directly. Run `bun run spec:gen` to regenerate. -->

# DESIGN.md Format

DESIGN.md is a self-contained, plain-text representation of a design system. It defines the visual identity of a brand and product, thereby ensuring that these stylistic choices can be followed across design sessions and between different AI agents and tools.  As a human-readable, open-format document, it serves as a living source of truth that both humans and AI can understand and refine.

A DESIGN.md file contains two parts: An optional YAML frontmatter, and a markdown body. The YAML front matter contains machine-readable design tokens. The markdown body sections provide human-readable design rationale and guidance. Prose may use descriptive color names (e.g., "Midnight Forest Green") that correspond to systematic token names (e.g., `primary`). The tokens are the normative values; the prose provides context for how to apply them.

# Design Tokens

DESIGN.md may embed design tokens in a structured format. The system that we use to describe design tokens is inspired by the
[Design Token JSON spec](https://www.designtokens.org/tr/2025.10/format/#abstract). Specifically, we adopt the concept of typed token groups (colors, typography, spacing) and the `{path.to.token}` reference syntax for cross-referencing values.

These tokens are easily converted from or to `tokens.json`, Figma variables, and Tailwind theme configs.

Design tokens are embedded as YAML front matter at the beginning of the file. The front matter block must begin with a line containing exactly `---` and end with a line containing exactly `---`. The YAML content between these delimiters is parsed according to the schema defined below.

Example:

```yaml
---
version: alpha
name: Daylight Prestige
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
---
```

## Schema

Below is the schema for the design tokens defined in the front matter:

```yaml
version: <string>          # optional, current version: "alpha"
name: <string>
description: <string>      # optional
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <token-name>: <string|token reference>
```

The `<scale-level>` placeholder represents a named level in a sizing or spacing scale. Common level names include `xs`, `sm`, `md`, `lg`, `xl`, and `full`. Any descriptive string key is valid.

**Color**: A color value must start with "#" followed by a hex color code in the SRGB color space.

- `fontFamily` (string)
- `fontSize` (Dimension)
- `fontWeight` (number) - A numeric font weight value (e.g., `400`, `700`). In YAML, this may be expressed as either a bare number or a quoted string; both are equivalent.
- `lineHeight` (Dimension | number) - Accepts either a Dimension (e.g., `24px`, `1.5rem`) or a unitless number (e.g., `1.6`). A unitless number represents a multiplier of the element's `fontSize`, which is the recommended CSS practice.
- `letterSpacing` (Dimension)
- `fontFeature` (string) - configures
  [`font-feature-settings`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font-feature-settings).
- `fontVariation` (string) - configures
  [`font-variation-settings`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font-variation-settings).

**Dimension**: A dimension value is a string with a unit suffix. Valid units are: px, em, rem.

**Token References**: A token reference must be wrapped in curly braces, and contain an object path to another value in the YAML tree. For most token groups, the reference must point to a primitive value (e.g., `colors.primary-60`), not a group (e.g., `colors`). Within the `components` section, references to composite values (e.g., `{typography.label-md}`) are permitted.

# Sections

Every `DESIGN.md` follows the same structure. Sections can be omitted if they're not relevant to your project, but those present should appear in the sequence listed below. All sections use `<h2>` (`##`) headings. An optional `<h1>` heading may appear for document titling purposes but is not parsed as a section.

### Section Order

1. **Overview** (also: "Brand & Style")
2. **Colors**
3. **Typography**
4. **Layout** (also: "Layout & Spacing")
5. **Elevation & Depth** (also: "Elevation")
6. **Shapes**
7. **Components**
8. **Do's and Don'ts**

### Prose and Tokens

## Overview

Also known as "Brand & Style".

This section is a holistic description of a product's look and feel. It defines the brand personality, target audience, and the emotional response the UI should evoke, such as whether it should feel playful or professional, dense or spacious. It serves as foundational context for guiding the agent's high-level stylistic decisions when a specific rule or token isn't explicitly defined.

## Colors

This section defines the color palettes for the design system.

At least the `primary` color palette must be defined, and additional color palettes may be defined as needed.

When there are multiple color palettes, the design system may assign a semantic role for each palette. A common convention is to name the palettes in this order: `primary`, `secondary`, `tertiary`, and `neutral`.

Example:

```markdown
## Colors

The palette is rooted in high-contrast neutrals and a single, evocative accent color.

- **Primary (#1A1C1E):** A deep ink used for headlines and core text to provide
  maximum readability and a sense of permanence.
- **Secondary (#6C7278):** A sophisticated slate used primarily for utilitarian
  elements like borders, captions, and metadata.
- **Tertiary (#B8422E):** A vibrant earthy red as the sole driver for
  interaction, used exclusively for primary actions and critical highlights.
- **Neutral (#F7F5F2):** A warm limestone that serves as the foundation for all
  pages, providing a softer, more organic feel than pure white.
```

### Design Tokens

The `colors` section defines all color design tokens. The color tokens should be derived from the key color palettes defined in the markdown prose. The exact mapping from color palettes to color tokens may follow any consistent naming convention.

It is a
map\<string, Color>, that maps the name of the color token to its value.

```yaml
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
```

## Typography

This section defines typography levels.

Most design systems have 9 - 15 typography levels. The design system may prescribe a role for each typography level.

A common naming convention for typography levels is to use semantic categories such as `headline`, `display`, `body`, `label`, `caption`. Each category may further be divided into different sizes, such as `small`, `medium`, and `large`.

Example:

```markdown
## Typography

The typography strategy leverages two distinct weights of **Public Sans** for
the narrative and **Space Grotesk** for technical data.

- **Headlines:** Set in Public Sans Semi-Bold to establish an institutional
  and trustworthy voice.
- **Body:** Public Sans Regular at 16px ensures contemporary professionalism
  and long-form readability.
- **Labels:** Space Grotesk is used for all technical data, timestamps, and
  metadata. Its geometric construction evokes the precision of a digital
  stopwatch. Labels are strictly uppercase with generous letter spacing.
```

### Design Tokens

The `typography` section defines the precise font properties for the typography design tokens.

It is a
map\<string, Typography>

```yaml
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  label-caps:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.1em
```

## Layout

Also known as "Layout & Spacing".

This section describes the layout and spacing strategy.

Many design systems follow a grid-based layout. Others, like Liquid Glass, use margins, safe areas, and dynamic padding.

Example:

```markdown
## Layout

The layout follows a **Fluid Grid** model for mobile devices and a
**Fixed-Max-Width Grid** for desktop (max 1200px).

A strict 8px spacing scale (with a 4px half-step for micro-adjustments) is used to maintain a consistent rhythm. Components are grouped using "containment" principles, where related items are housed in cards with generous internal padding (24px) to emphasize the soft, approachable nature of the brand.
```

### Design Tokens

The spacing section defines the spacing design tokens. These may include spacing units that are useful for implementing the layout model. For example, a fixed grid layout may have spacing units for column spans, gutters, and margins.

It is a
map\<string, Dimension | number> that maps the spacing scale identifier to a dimension value or a unitless number (e.g., column counts or ratios).

```yaml
spacing:
  base: 16px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
  gutter: 24px
  margin: 32px
```

## Elevation & Depth

Also known as "Elevation".

This section describes how visual hierarchy is conveyed based on the design style. If elevation is used, it defines the required styling (spread, blur, color). For flat designs, this section explains the alternative methods used to convey visual hierarchy (e.g., borders, color contrast).

Example:

```markdown
## Elevation & Depth

Depth is achieved through **Tonal Layers** rather than heavy shadows. The
background uses a soft off-white or very light green, while primary content sits on pure white cards.
```

## Shapes

This section describes how visual elements are shaped.

Example:

```markdown
## Shapes

The shape language is defined by **Architectural Sharpness**. All interactive
elements, containers, and inputs utilize a minimal **4px corner radius**. This
provides just enough softness to feel modern while maintaining a rigid,
engineered aesthetic.
```

### Design Tokens

The `rounded` section defines the design tokens for rounded corners used in
buttons, cards, and other rectangular shapes.

It is a map\<string, Dimension>.

```yaml
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
```

## Components

This section provides style guidance for component atoms within the design system. The following are common component types. Design systems are encouraged to define additional components relevant to their domain.

* **Buttons**: Covers primary, secondary, and tertiary variants, including sizing, padding, and states.
* **Chips**: Covers selection chips, filter chips, and action chips.
* **Lists**: Covers styling for list items, dividers, and leading/trailing elements.
* **Tooltips**: Covers positioning, colors, and timing.
* **Checkboxes**: Covers checked, unchecked, and indeterminate states.
* **Radio buttons**: Covers selected and unselected states.
* **Input fields**: Covers text inputs, text areas, labels, helper text, and error states.

> **Note:** The components specification is actively evolving. The current structure provides intentional flexibility for domain-specific component definitions while the spec matures.

### Design Tokens

The components section defines a collection of design tokens used to ensure consistent styling of common components. It's a map\<string, map\<string, string>> that maps a component identifier to a group of sub token names and values. The design token values may be literal values, or references to previously defined design tokens.

**Variants**. A component may have a variant for different UI states such as active, hover, pressed, etc. Those variant components may be defined under a different but related key, for example, "button-primary", "button-primary-hover", "button-primary-active". The agent will consider all variants and make the appropriate styling decisions.

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary-60}"
    textColor: "{colors.primary-20}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary-70}"
```

### Component Property Tokens

Each component has a set of properties that are themselves design tokens:

- backgroundColor: \<Color\>
- textColor: \<Color\>
- typography: \<Typography\>
- rounded: \<Dimension\>
- padding: \<Dimension\>
- size: \<Dimension\>
- height: \<Dimension\>
- width: \<Dimension\>

## Do's and Don'ts

This section provides practical guidelines and common pitfalls. These act as guardrails when creating designs.

```markdown
## Do's and Don'ts

- Do use the primary color only for the single most important action per screen
- Don't mix rounded and sharp corners in the same view
- Do maintain WCAG AA contrast ratios (4.5:1 for normal text)
- Don't use more than two font weights on a single screen
```

# Recommended Token Names (Non-Normative)

The following names are commonly used across design systems. They are not required but are provided as guidance for consistency.

**Colors:** `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`

**Typography:** `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`

**Rounded:** `none`, `sm`, `md`, `lg`, `xl`, `full`

# Consumer Behavior for Unknown Content

When a DESIGN.md consumer encounters content not defined by this spec:

| Scenario | Behavior | Example |
|---|---|---|
| Unknown section heading | Preserve; do not error | `## Iconography` |
| Unknown color token name | Accept if value is valid | `surface-container-high: '#ede7dd'` |
| Unknown typography token name | Accept as valid typography | `telemetry-data` |
| Unknown spacing value | Accept; store as string if not a valid dimension | `grid-columns: '5'` |
| Unknown component property | Accept with warning | `borderColor` |
| Duplicate section heading | Error; reject the file | Two `## Colors` headings |

---

# Appendix A: Machine-Readable Spec Configuration

> Source: `packages/cli/src/linter/spec-config.yaml` — the single source of
> truth the CLI reads at runtime. The human-facing spec above is generated
> from this file. Reproduced for downstream consumers.

```yaml
version: alpha

units:
  - px
  - em
  - rem

sections:
  - canonical: Overview
    aliases:
      - Brand & Style
  - canonical: Colors
  - canonical: Typography
  - canonical: Layout
    aliases:
      - Layout & Spacing
  - canonical: Elevation & Depth
    aliases:
      - Elevation
  - canonical: Shapes
  - canonical: Components
  - canonical: "Do's and Don'ts"

typography_properties:
  - name: fontFamily
    type: string
  - name: fontSize
    type: Dimension
  - name: fontWeight
    type: number
    description: "A numeric font weight value (e.g., `400`, `700`). In YAML, this may be expressed as either a bare number or a quoted string; both are equivalent."
  - name: lineHeight
    type: "Dimension | number"
    description: "Accepts either a Dimension (e.g., `24px`, `1.5rem`) or a unitless number (e.g., `1.6`). A unitless number represents a multiplier of the element's `fontSize`, which is the recommended CSS practice."
  - name: letterSpacing
    type: Dimension
  - name: fontFeature
    type: string
    description: "configures `font-feature-settings`."
  - name: fontVariation
    type: string
    description: "configures `font-variation-settings`."

component_sub_tokens:
  - name: backgroundColor
    type: Color
  - name: textColor
    type: Color
  - name: typography
    type: Typography
  - name: rounded
    type: Dimension
  - name: padding
    type: Dimension
  - name: size
    type: Dimension
  - name: height
    type: Dimension
  - name: width
    type: Dimension

color_roles:
  - primary
  - secondary
  - tertiary
  - neutral

recommended_tokens:
  colors:
    - primary
    - secondary
    - tertiary
    - neutral
    - surface
    - on-surface
    - error
  typography:
    - headline-display
    - headline-lg
    - headline-md
    - body-lg
    - body-md
    - body-sm
    - label-lg
    - label-md
    - label-sm
  rounded:
    - none
    - sm
    - md
    - lg
    - xl
    - full
```

---

# Appendix B: Quick Reference Tables

## B.1 Token Types

| Type            | Format                                      | Example                |
| :-------------- | :------------------------------------------ | :--------------------- |
| Color           | `#` + hex (sRGB)                            | `"#1A1C1E"`            |
| Dimension       | number + unit (one of `px`, `em`, `rem`)    | `48px`, `-0.02em`      |
| Token Reference | `{path.to.token}`                           | `{colors.primary}`     |
| Typography      | object with the seven properties below      | see Typography schema  |

## B.2 Typography Object Properties

| Property         | Type                  | Required | Notes                                                                                          |
| :--------------- | :-------------------- | :------- | :--------------------------------------------------------------------------------------------- |
| `fontFamily`     | string                | no       | Font family name. Unquoted scalar is fine in YAML.                                             |
| `fontSize`       | Dimension             | no       | e.g. `48px`, `1.5rem`.                                                                         |
| `fontWeight`     | number                | no       | Numeric (`400`, `700`). Bare number or quoted string both valid in YAML.                       |
| `lineHeight`     | Dimension \| number   | no       | Dimension (`24px`, `1.5rem`) OR unitless multiplier (`1.6`). Unitless is the recommended form. |
| `letterSpacing`  | Dimension             | no       | e.g. `-0.02em`, `0.1em`.                                                                       |
| `fontFeature`    | string                | no       | Sets CSS `font-feature-settings`.                                                              |
| `fontVariation`  | string                | no       | Sets CSS `font-variation-settings`.                                                            |

## B.3 Component Sub-Tokens (CLOSED SET)

The linter `broken-ref` rule emits a `warning` for any sub-token NOT in this list.

| Property          | Type        |
| :---------------- | :---------- |
| `backgroundColor` | Color       |
| `textColor`       | Color       |
| `typography`      | Typography  |
| `rounded`         | Dimension   |
| `padding`         | Dimension   |
| `size`            | Dimension   |
| `height`          | Dimension   |
| `width`           | Dimension   |

## B.4 Sections and Aliases

| Order | Canonical Heading | Allowed Aliases     |
| :---- | :---------------- | :------------------ |
| 1     | Overview          | Brand & Style       |
| 2     | Colors            | (none)              |
| 3     | Typography        | (none)              |
| 4     | Layout            | Layout & Spacing    |
| 5     | Elevation & Depth | Elevation           |
| 6     | Shapes            | (none)              |
| 7     | Components        | (none)              |
| 8     | Do's and Don'ts   | (none)              |

Sections use `##` (h2). An optional `#` (h1) may be used for document
titling but is not parsed as a section. Sections can be omitted, but
those present should appear in the order above. A duplicate section
heading is an error and the file is rejected.

## B.5 Valid Dimension Units

`px`, `em`, `rem` — anything else is rejected as a Dimension (though it
may still be accepted as a string value per the unknown-content table).

## B.6 Token Reference Syntax

- Wrapped in curly braces: `{path.to.token}`
- Object path through the YAML tree from the front-matter root
- Must point to a primitive value for non-component groups (e.g. allowed:
  `{colors.primary-60}`; not allowed: `{colors}`)
- Inside `components`, references to composite values are permitted
  (e.g. `{typography.label-md}`)

## B.7 Required vs Optional (Top-Level Frontmatter Keys)

| Key            | Required | Notes                                                                                      |
| :------------- | :------- | :----------------------------------------------------------------------------------------- |
| `version`      | optional | Current value: `"alpha"`.                                                                  |
| `name`         | required (per schema) | Design system name. Examples always include it.                                  |
| `description`  | optional | Free-form prose.                                                                           |
| `colors`       | optional | But: if any colors are defined, `primary` SHOULD exist (else `missing-primary` warning).   |
| `typography`   | optional | But: if `colors` exists and `typography` is empty → `missing-typography` warning.          |
| `rounded`      | optional | If absent and `colors` exists → `missing-sections` info.                                   |
| `spacing`      | optional | If absent and `colors` exists → `missing-sections` info.                                   |
| `components`   | optional | Each value is a map of sub-token name → value/reference.                                   |

Note: the frontmatter itself is OPTIONAL at the file level — a DESIGN.md
may be pure prose. The schema above only applies if frontmatter is
present.

---

# Appendix C: Spec Text vs Empirical Linter Behavior

> **Rule for the extractor skill author: read with tolerance, write with
> strictness.** Several values that the spec text disallows are silently
> accepted by the linter because the parser falls back to "store as
> string" per the unknown-content table. The canonical
> `examples/atmospheric-glass/DESIGN.md` itself uses many such values
> and produces 0 errors when linted. Verified by running
> `npx @google/design.md lint` on that file.

## C.1 Values the spec text disallows but the linter accepts

| Form                                      | Spec says                                          | Linter behavior                                              |
| :---------------------------------------- | :------------------------------------------------- | :----------------------------------------------------------- |
| `rgba(255, 255, 255, 0.1)` for a Color    | Must start with `#` + hex in sRGB.                 | Stored as opaque string; no `broken-ref` error.              |
| `transparent` keyword for a Color         | Same — `#` + hex only.                             | Stored as string; no error. Skips `contrast-ratio` check.    |
| `0 24px` for `padding` (CSS shorthand)    | Dimension = "number + unit" (singular).            | Stored as string; no error.                                  |
| Bare numbers without unit for Dimension   | Dimension is a string with a unit suffix.          | Accepted; spec table explicitly says "store as string".      |

**Implication:** when EXTRACTING from a website, the skill can faithfully
preserve `rgba()`, `transparent`, and CSS shorthand for `padding` and
the file will lint clean. But when EMITTING tokens intended for re-use
by an agent that re-resolves the schema strictly, prefer hex + alpha
emulation (`#FFFFFF1A` for 10% white) and single-Dimension `padding`.

## C.2 Empirical lint result of the canonical example

`npx @google/design.md lint examples/atmospheric-glass/DESIGN.md`
produces:

- **errors: 0**
- **warnings: 43** — all `orphaned-tokens` findings on MD3 surface /
  variant tokens. NONE are `broken-ref`, `contrast-ratio`,
  `missing-primary`, `missing-typography`, `missing-sections`, or
  `section-order`.
- **infos: 1** — the unavoidable `token-summary` line:
  `Design system defines 47 colors, 6 typography scales, 6 rounding
  levels, 5 spacing tokens, 10 components.`

The summary object uses the key `infos` (plural), even though
individual finding `severity` is `"info"` (singular). README and rule
sources are inconsistent here — trust the JSON output shape:

```json
"summary": { "errors": <n>, "warnings": <n>, "infos": <n> }
```

## C.3 Quoting and YAML form notes

- Hex color values are conventionally quoted: `"#1A1C1E"`. Unquoted
  works too because `#` is YAML's comment marker only at the start of a
  scalar context — most loaders treat `primary: #1A1C1E` as a comment.
  **Always quote hex strings** to be safe.
- Negative dimensions can be either quoted or unquoted in the source
  spec config (`letterSpacing: "-0.02em"` in `spec-config.yaml` example,
  `letterSpacing: -0.02em` in the spec.md example body). Both parse.
- `fontWeight`: bare number (`600`) and quoted string (`"600"`) are
  declared equivalent by the spec.
- `lineHeight`: bare number is a multiplier; quoted/unquoted Dimension
  with unit is an absolute value. The two are NOT equivalent.

## C.4 What strictness gains you

A "strict" DESIGN.md (hex-only colors, single-Dimension paddings, all
tokens referenced from at least one component, every component pair
contrast-checked) lints to:

- errors: 0
- warnings: 0
- infos: 1 (the unavoidable `token-summary`)

This is the target the extractor skill should aim for, even though
loose forms also pass.
