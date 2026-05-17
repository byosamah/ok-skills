# DESIGN.md Linting Rules — Complete Reference

> Sources cross-checked:
> - `README.md` (Linting Rules section)
> - `packages/cli/src/linter/linter/rules/index.ts` (rule order and registry)
> - `packages/cli/src/linter/linter/rules/<rule>.ts` (per-rule descriptor, severity, message templates, trigger logic)
>
> **Note on rule count:** The README says "seven rules" but lists eight in
> its table, and the source registry (`DEFAULT_RULE_DESCRIPTORS`)
> enumerates eight. Trust the source: there are **8 active rules**.
>
> **Auto-fix:** None of the rules are auto-fixable. The CLI has no
> `--fix` flag and the linter only emits findings (a `fixer/` directory
> exists in source but is not wired into the public CLI). Resolution is
> manual.

## Severity legend

- `error` — File has structural problems an agent cannot safely consume.
  Causes `lint` to exit with code `1`.
- `warning` — File is parseable but a quality/consistency concern an
  author would want to know about. Does NOT cause non-zero exit on
  `lint`. (Does cause non-zero exit on `diff` if warning count increases
  vs the "before" file.)
- `info` — Diagnostic / summary. Never causes non-zero exit.

## Rule registry (execution order)

The linter runs the rules in this exact order:

1. `broken-ref`
2. `missing-primary`
3. `contrast-ratio`
4. `orphaned-tokens`
5. `token-summary`
6. `missing-sections`
7. `missing-typography`
8. `section-order`

## Complete rule table

| # | Rule name          | Severity  | Auto-fix | What it checks                                                                                                                            |
| - | ------------------ | --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | `broken-ref`       | `error`   | no       | Unresolved `{path.to.token}` references inside `components.*`. Also flags unknown component sub-tokens (downgraded to `warning`).         |
| 2 | `missing-primary`  | `warning` | no       | At least one color is defined but no `primary` token exists. Agents will auto-generate a primary, reducing author control.                |
| 3 | `contrast-ratio`   | `warning` | no       | A component defines BOTH `backgroundColor` and `textColor` AND their resolved hex pair has WCAG contrast ratio below **4.5:1** (AA).      |
| 4 | `orphaned-tokens`  | `warning` | no       | A color token is defined but never referenced by any component, AND not part of an in-use Material Design 3 family (see exemption rules). |
| 5 | `token-summary`    | `info`    | no       | Always emits one summary line: "Design system defines N colors, N typography scales, N rounding levels, N spacing tokens, N components."  |
| 6 | `missing-sections` | `info`    | no       | `colors` is defined but `spacing` and/or `rounded` is empty. Notes that agent defaults will be used.                                      |
| 7 | `missing-typography` | `warning` | no     | `colors` is defined but no typography tokens exist. Agents will fall back to default font choices.                                        |
| 8 | `section-order`    | `warning` | no       | Markdown `##` section headings appear in an order that violates the canonical 1–8 sequence (after alias resolution).                      |

## Per-rule detail

### 1. `broken-ref` — error

**Description (verbatim from source):**
> Broken/circular references and unknown component sub-tokens.

**What triggers it:**
- For each component `comp`, for each unresolved token reference in
  `comp.unresolvedRefs`: emit at `components.<compName>`.
- For each property name in `comp.properties` not in
  `VALID_COMPONENT_SUB_TOKENS`: emit at `components.<compName>.<propName>`.

**Message templates:**
- Unresolved reference (severity `error`):
  `Reference {<path>} does not resolve to any defined token.`
- Unknown sub-token (severity downgraded to `warning`):
  `'<propName>' is not a recognized component sub-token. Valid sub-tokens: backgroundColor, textColor, typography, rounded, padding, size, height, width.`

**Valid sub-token list** (closed set): `backgroundColor`, `textColor`,
`typography`, `rounded`, `padding`, `size`, `height`, `width`.

**Note:** "Circular references" appears in the description string but
the loop only walks `unresolvedRefs` — cycle detection is performed
upstream in the resolver, not in this rule.

---

### 2. `missing-primary` — warning

**Description (verbatim from source):**
> Missing primary color — warns when colors are defined but no 'primary' exists.

**What triggers it:**
- `state.colors.size > 0` AND `state.colors.has('primary')` is false.

**Message (verbatim):**
> No 'primary' color defined. The agent will auto-generate key colors, reducing your control over the palette.

**Path:** `colors`

---

### 3. `contrast-ratio` — warning

**Description (verbatim from source):**
> WCAG contrast ratio — warns when component backgroundColor/textColor pairs fall below the AA minimum of 4.5:1.

**What triggers it:**
- For each component, if BOTH `backgroundColor` and `textColor` resolve
  to actual color values (after token resolution), compute the WCAG
  contrast ratio. If `ratio < 4.5` → finding.
- Components missing one of the two properties are skipped (no finding).
- Components whose color references can't resolve to a color are
  skipped (no finding from this rule — `broken-ref` handles that).

**Message template:**
> textColor (<#hex>) on backgroundColor (<#hex>) has contrast ratio <X.XX>:1, below WCAG AA minimum of 4.5:1.

**Path:** `components.<compName>`

**Constants:** `WCAG_AA_MINIMUM = 4.5`. The rule does NOT check the
WCAG AAA threshold (7:1) and does NOT distinguish large vs normal text
(WCAG allows 3:1 for large text; the rule applies 4.5:1 uniformly).

---

### 4. `orphaned-tokens` — warning

**Description (verbatim from source):**
> Orphaned tokens — tokens defined but never referenced by any component.

**What triggers it:**
1. If `state.components.size === 0` → emit nothing (early return).
2. Build `referencedPaths` = set of YAML paths pointed to by any
   component property reference.
3. Build `referencedFamilies` from `referencedPaths` using MD3 family
   collapsing (strip `on-`, `inverse-` prefixes; strip `-container*`,
   `-fixed*`, `-dim`, `-bright`, `-tint`, `-variant` suffixes).
4. For each `colors.<name>`:
   - skip if its path is directly referenced
   - skip if its family is in `referencedFamilies`
   - skip if its family is in `MD3_STANDARD_FAMILIES = {primary,
     secondary, tertiary, error, surface, background, outline}`
   - otherwise → finding.

**Message template:**
> '<tokenName>' is defined but never referenced by any component.

**Path:** `colors.<tokenName>`

**Implication for the extractor skill:** custom palette tokens like
`brand-blue` or `accent-magenta` WILL be flagged if no component
references them. MD3-style tokens (`on-primary-container`, etc.) will
not, even if unreferenced, as long as their family root is in use OR is
a standard MD3 family.

---

### 5. `token-summary` — info

**Description (verbatim from source):**
> Token count summary — emits an info diagnostic summarizing how many tokens are defined.

**What triggers it:** Always emits one finding when at least one token
section is non-empty.

**Message template (built from non-empty sections, comma-joined):**
> Design system defines N color(s), N typography scale(s), N rounding level(s), N spacing token(s), N component(s).

Pluralization on each part is automatic.

**Path:** unset (top-level diagnostic).

---

### 6. `missing-sections` — info

**Description (verbatim from source):**
> Missing sections — notes when optional sections (spacing, rounded) are absent.

**What triggers it:** For each of `spacing` and `rounded` independently:
- the section is empty (`size === 0`) AND
- `state.colors.size > 0`
→ emit one finding for each absent section.

**Message templates:**
> No 'spacing' section defined. Layout spacing will fall back to agent defaults.
> No 'rounded' section defined. Corner rounding will fall back to agent defaults.

**Paths:** `spacing` or `rounded`.

**Note:** `typography` absence is handled by the separate
`missing-typography` rule (warning, not info).

---

### 7. `missing-typography` — warning

**Description (verbatim from source):**
> Missing typography — warns when colors are defined but no typography tokens exist.

**What triggers it:** `state.typography.size === 0` AND
`state.colors.size > 0`.

**Message (verbatim):**
> No typography tokens defined. Agents will use default font choices, reducing your control over the design system's typographic identity.

**Path:** `typography`

---

### 8. `section-order` — warning

**Description (verbatim from source):**
> Section order — warns when sections are out of canonical order.

**What triggers it:**
1. Extract the list of `##` headings from the markdown body.
2. Resolve each through `SECTION_ALIASES` (Brand & Style → Overview,
   Layout & Spacing → Layout, Elevation → Elevation & Depth).
3. Filter to only known canonical sections (unknown headings are
   ignored).
4. For each adjacent pair `(current, next)` in the filtered list, if
   `index(current) > index(next)` in the canonical order → emit one
   finding and break (only the first violation is reported).

**Message template:**
> Section '<current>' appears before '<next>', which is out of order. Expected order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts

**Path:** unset.

**Note:** Duplicate section headings are NOT detected by this rule —
they are caught earlier by the parser and the file is rejected (per
spec's unknown-content table).

## How findings are serialized

Each finding is a JSON object:

```json
{
  "severity": "error" | "warning" | "info",
  "path": "<dotted-path>",            // optional; unset for whole-file findings
  "message": "<human-readable string>"
}
```

The `lint` command output shape:

```json
{
  "findings": [ ... ],
  "summary": { "errors": <n>, "warnings": <n>, "info": <n> }
}
```

## Cheat sheet for the extractor skill

To produce a DESIGN.md that lints clean (zero `errors`, zero `warnings`,
only the unavoidable `token-summary` info finding):

1. Define a `primary` color (avoids `missing-primary`).
2. Define typography tokens (avoids `missing-typography`).
3. Define both `spacing` AND `rounded` (avoids `missing-sections` infos).
4. Make sure every `{path.to.token}` resolves — only reference tokens
   you actually define (avoids `broken-ref` errors).
5. Only use the 8 known component sub-tokens (`backgroundColor`,
   `textColor`, `typography`, `rounded`, `padding`, `size`, `height`,
   `width`) — anything else gets a `broken-ref`-warning.
6. For any component with both `backgroundColor` and `textColor`,
   ensure resolved contrast ratio >= 4.5:1 (avoids `contrast-ratio`).
7. Reference every color you define from at least one component, OR
   keep your token names inside the MD3 family system (avoids
   `orphaned-tokens`).
8. Order `##` headings as: Overview → Colors → Typography → Layout →
   Elevation & Depth → Shapes → Components → Do's and Don'ts (avoids
   `section-order`). Aliases are allowed in either direction.
