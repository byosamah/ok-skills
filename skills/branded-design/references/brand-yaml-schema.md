# brand.yaml Schema Reference

Complete specification for the `brand-kit/brand.yaml` file that drives every branded-design generation.

---

## Required Fields

### `name`
- **Type:** `string`
- **Description:** The brand name. Used for text overlays, watermarks, and prompt context. Should match the exact casing and spelling you want displayed on posts.

### `tone`
- **Type:** `string`
- **Description:** The overall voice and personality of the brand. Informs prompt construction and copy generation. Use 2-4 descriptive words separated by commas.
- **Examples:** `"bold, playful"`, `"minimal, premium, sophisticated"`, `"warm, approachable, educational"`

### `colors`
- **Type:** `object` (all sub-fields required)
- **Description:** The brand's core color palette. Used for backgrounds, text, accents, and color-matching in generated visuals.

| Sub-field      | Type     | Description                                                        |
|----------------|----------|--------------------------------------------------------------------|
| `primary`      | `string` | Main brand color. Used for headlines, buttons, key UI elements.    |
| `secondary`    | `string` | Supporting color. Used for contrast elements, secondary text.      |
| `accent`       | `string` | Highlight/pop color. Used for CTAs, badges, emphasis.              |
| `background`   | `string` | Default background color for posts.                                |
| `text`         | `string` | Default body text color. Should have strong contrast vs background. |

All color values must be valid CSS colors: hex (`#FF5733`), RGB (`rgb(255,87,51)`), or named (`white`). Hex is recommended for consistency.

### `style_keywords`
- **Type:** `list[string]`
- **Description:** Visual style descriptors that get injected into every image generation prompt. These shape the aesthetic of every post. Use 3-8 keywords that capture the brand's visual identity.
- **Examples:** `["flat illustration", "geometric", "vibrant"]`, `["photography", "dark moody", "cinematic lighting"]`

---

## Optional Fields

### `tagline`
- **Type:** `string`
- **Default:** None (omitted from posts if not set)
- **Description:** Brand tagline or slogan. Can be placed on posts as subtitle text.

### `fonts`
- **Type:** `object`
- **Description:** Typography preferences for the brand.

| Sub-field | Type     | Description                                              |
|-----------|----------|----------------------------------------------------------|
| `heading` | `string` | Font family for headlines and titles.                    |
| `body`    | `string` | Font family for body text, captions, and descriptions.   |

If omitted, the skill uses system defaults (Inter for body, a bold sans-serif for headings).

### `font_strategy`
- **Type:** `string` (enum: `"reference"` | `"exact"`)
- **Default:** `"reference"`
- **Description:** Controls how fonts are handled in generation.
  - `"reference"` -- The font names are used as style guidance in the prompt. The AI model approximates the typographic feel. Best for most cases.
  - `"exact"` -- Font files must exist in `brand-kit/fonts/`. They get composited onto the final image in a post-processing step. Use when pixel-perfect typography is required.

### `logo_placement`
- **Type:** `string` (enum: `"top-left"` | `"top-right"` | `"bottom-left"` | `"bottom-right"` | `"center"` | `"none"`)
- **Default:** `"bottom-right"`
- **Description:** Where the logo gets composited onto generated posts. Requires a logo file in `brand-kit/logo.png` (or `.svg`). Set to `"none"` to skip logo placement entirely.

---

## Complete Example

A real-world brand configuration with all fields:

```yaml
name: "Volteria"
tagline: "Energy for the bold"
tone: "bold, futuristic, premium"

colors:
  primary: "#6C3BF5"
  secondary: "#1A1A2E"
  accent: "#00F0FF"
  background: "#0D0D1A"
  text: "#EAEAEA"

fonts:
  heading: "Space Grotesk"
  body: "Inter"

font_strategy: "reference"
logo_placement: "bottom-right"

style_keywords:
  - "dark futuristic"
  - "neon accents"
  - "glassmorphism"
  - "tech startup"
  - "clean geometric"
  - "gradient overlays"
```

---

## Minimal Example

Only required fields -- the smallest valid `brand.yaml`:

```yaml
name: "Bloom Cafe"
tone: "warm, cozy, handcrafted"

colors:
  primary: "#5B3A29"
  secondary: "#F5E6D3"
  accent: "#E07A5F"
  background: "#FFF8F0"
  text: "#2C1810"

style_keywords:
  - "watercolor illustration"
  - "earthy tones"
  - "organic shapes"
```

---

## Field Behavior Summary

| Field            | Required | Type          | Default          | Used In                        |
|------------------|----------|---------------|------------------|--------------------------------|
| `name`           | Yes      | string        | --               | Prompts, text overlays         |
| `tagline`        | No       | string        | None             | Subtitle text on posts         |
| `tone`           | Yes      | string        | --               | Prompt construction            |
| `colors.primary` | Yes      | string (CSS)  | --               | Headlines, key elements        |
| `colors.secondary`| Yes     | string (CSS)  | --               | Supporting elements            |
| `colors.accent`  | Yes      | string (CSS)  | --               | CTAs, highlights               |
| `colors.background`| Yes    | string (CSS)  | --               | Post background                |
| `colors.text`    | Yes      | string (CSS)  | --               | Body text                      |
| `fonts.heading`  | No       | string        | System default   | Headline typography            |
| `fonts.body`     | No       | string        | System default   | Body typography                |
| `font_strategy`  | No       | `"reference"` / `"exact"` | `"reference"` | Font rendering method |
| `logo_placement` | No       | position enum | `"bottom-right"` | Logo compositing position      |
| `style_keywords` | Yes      | list[string]  | --               | Image generation prompts       |

---

## Directory Structure

The `brand.yaml` file lives inside the skill's `brand-kit/` directory alongside other brand assets:

```
brand-kit/
  brand.yaml          # This file
  logo.png            # Brand logo (optional, required if logo_placement != "none")
  reference/          # Reference images for style matching
    post-example-1.png
    post-example-2.png
  fonts/              # Font files (only needed if font_strategy: "exact")
    SpaceGrotesk.woff2
    Inter.woff2
```

---

## Validation Rules

1. `name` must be non-empty.
2. `tone` must be non-empty.
3. All five `colors` sub-fields must be present and valid CSS color values.
4. `style_keywords` must contain at least one item.
5. If `font_strategy` is `"exact"`, corresponding font files must exist in `brand-kit/fonts/`.
6. If `logo_placement` is anything other than `"none"`, a logo file must exist in `brand-kit/`.
7. Color contrast: `text` vs `background` should have a contrast ratio of at least 4.5:1 (WCAG AA).
