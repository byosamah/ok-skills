---
version: alpha
name: REPLACE_ME
description: One or two sentences describing the brand personality.
colors:
  primary: "#000000"
  # secondary: "#000000"
  # tertiary: "#000000"
  # neutral: "#FFFFFF"
  # surface: "#FFFFFF"
  # on-surface: "#000000"
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.02em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: 4px
  md: 8px
  lg: 16px
  full: 9999px
spacing:
  unit: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 12px
    height: 44px
---

## Overview

One paragraph on the brand personality, the target user, the emotional response the UI should evoke, and the "house style" in 2–3 words.

## Colors

Two to four sentences on the color strategy, then bullet points naming each palette role with hex inline.

- **Primary (#XXXXXX):** Role and rationale.
- **Secondary (#XXXXXX):** Role and rationale.

## Typography

Name the fonts, describe each role, note any treatments (uppercase labels, tabular numerals, variable-axis settings).

## Layout

Grid model (fluid / fixed-max-width / asymmetric), base unit, breakpoint strategy, container padding behavior.

## Elevation & Depth

How visual hierarchy is achieved. For flat designs, describe the alternatives (borders, tonal layers). For elevated designs, describe shadow levels.

## Shapes

One sentence on the shape language. Per-element radius application.

## Components

Brief paragraph per component family describing behavior, states, and rationale. Reference tokens by name rather than restating values.

## Do's and Don'ts

- Do …
- Don't …
- Do …
- Don't …
