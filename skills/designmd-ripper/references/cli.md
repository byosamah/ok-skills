# `@google/design.md` CLI — Complete Reference

> Sources cross-checked:
> - `README.md` (CLI Reference section)
> - `packages/cli/package.json` (bin entries, dependencies, build config)
> - `packages/cli/src/index.ts` (subcommand registry)
> - `packages/cli/src/commands/{lint,diff,export,spec}.ts` (per-command
>   args, flags, defaults, exit codes)

## Package identity

- **npm package:** [`@google/design.md`](https://www.npmjs.com/package/@google/design.md)
- **Current version (at research time):** `0.1.1`
- **Format version:** `alpha`
- **License:** Apache-2.0
- **Description:** "Bridging design systems and code: a linter and
  exporter for the DESIGN.md format" — published as
  `@google/design.md` with `design.md` and `designmd` bin aliases.
- **Runtime:** Node.js (built with Bun; ships as ESM JS).
- **Stability:** alpha — spec, schema, and CLI under active development.

## Installation

```bash
npm install @google/design.md
```

On **Windows** (PowerShell, some terminals) quote the package name
because `@` may be treated specially:

```bash
npm install "@google/design.md"
```

Or run without installing (always resolves from the public npm registry):

```bash
npx @google/design.md lint DESIGN.md
```

### Bin aliases

The package installs **two** identical executables (per
`package.json#bin`):

| Bin name    | Use when                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------- |
| `design.md` | Normal Unix / npx invocation.                                                                     |
| `designmd`  | Inside a `package.json` script on Windows — the `.md` suffix collides with Markdown file assoc.   |

```jsonc
// package.json — Windows-safe form
{
  "scripts": {
    "design:lint": "designmd lint DESIGN.md"
  }
}
```

### Common install error: `ENOVERSIONS`

`npm error ENOVERSIONS` ("No versions available for @google/design.md")
almost always means npm is not querying the public registry. Causes:

- Custom `registry=` in `.npmrc`
- Corporate mirror that has not synced this package
- Misconfigured `@google:registry` scope override

Check effective registry:

```bash
npm config get registry
# expected: https://registry.npmjs.org/
```

After fixing the config, retry. If a stale 404 was cached:

```bash
npm cache clean --force
```

## Global invocation conventions

- All commands accept a positional **file path** or `-` (single hyphen)
  to read from stdin.
- Output defaults to **JSON** for `lint`, `diff`, `export`. The `spec`
  command defaults to **Markdown**.
- All commands accept `--format <value>`; `spec` adds `--rules` and
  `--rules-only`.
- Exit code is `0` on success, `1` on failure conditions (per-command,
  see below).

```bash
# file argument
npx @google/design.md lint DESIGN.md

# stdin
cat DESIGN.md | npx @google/design.md lint -
```

## Top-level CLI shape

```
design.md <subcommand> [args...] [--flags]
```

Subcommands (registered in `src/index.ts`):

| Subcommand | Purpose                                                     |
| ---------- | ----------------------------------------------------------- |
| `lint`     | Validate a DESIGN.md file for structural correctness.       |
| `diff`     | Compare two DESIGN.md files and report token-level changes. |
| `export`   | Export tokens to Tailwind v3/v4 or W3C DTCG.                |
| `spec`     | Output the spec (and/or rules table) for prompt injection.  |

CLI tagline (meta description in `index.ts`):
> "Agent-first CLI for DESIGN.md — the hands and eyes for design system work."

---

## `lint` — validate a DESIGN.md

### Synopsis

```bash
npx @google/design.md lint <file> [--format <json>]
npx @google/design.md lint --format json DESIGN.md
cat DESIGN.md | npx @google/design.md lint -
```

### Arguments and flags

| Option     | Type            | Default | Required | Description                                       |
| ---------- | --------------- | ------- | -------- | ------------------------------------------------- |
| `file`     | positional      | —       | yes      | Path to DESIGN.md, or `-` for stdin.              |
| `--format` | string          | `json`  | no       | Output format. Source declares `json` or `text`.  |

Note: the README's CLI Reference table shows `--format` type as
literally `json`. The command source accepts any string but only `json`
is currently implemented in `formatOutput`.

### Output shape (JSON)

```json
{
  "findings": [
    {
      "severity": "warning",
      "path": "components.button-primary",
      "message": "textColor (#ffffff) on backgroundColor (#1A1C1E) has contrast ratio 15.42:1 — passes WCAG AA."
    }
  ],
  "summary": { "errors": 0, "warnings": 1, "info": 1 }
}
```

(The README example wording — "passes WCAG AA" — is illustrative; the
actual rule only emits findings when the ratio is BELOW 4.5:1. See
linting-rules.md for the verbatim message template.)

### Exit code

- `0` — `summary.errors === 0`.
- `1` — `summary.errors > 0`.

Warnings and info findings do NOT change the exit code.

---

## `diff` — compare two DESIGN.md files

### Synopsis

```bash
npx @google/design.md diff <before> <after> [--format <json>]
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

### Arguments and flags

| Option     | Type        | Default | Required | Description                                |
| ---------- | ----------- | ------- | -------- | ------------------------------------------ |
| `before`   | positional  | —       | yes      | Path to the "before" DESIGN.md.            |
| `after`    | positional  | —       | yes      | Path to the "after" DESIGN.md.             |
| `--format` | string      | `json`  | no       | Output format.                             |

Neither `before` nor `after` accepts `-` (stdin) — both require file
paths because two streams cannot be read from one stdin.

### Output shape (JSON)

```json
{
  "tokens": {
    "colors":     { "added": [...], "removed": [...], "modified": [...] },
    "typography": { "added": [...], "removed": [...], "modified": [...] },
    "rounded":    { "added": [...], "removed": [...], "modified": [...] },
    "spacing":    { "added": [...], "removed": [...], "modified": [...] },
    "components": { "added": [...], "removed": [...], "modified": [...] }
  },
  "findings": {
    "before": { "errors": N, "warnings": N, "info": N },
    "after":  { "errors": N, "warnings": N, "info": N },
    "delta":  { "errors": N, "warnings": N }
  },
  "regression": <boolean>
}
```

### Regression definition

`regression: true` when either:

- `after.summary.errors   > before.summary.errors`, OR
- `after.summary.warnings > before.summary.warnings`.

`info` count is tracked but does not trigger regression.

### Exit code

- `0` — `regression === false`.
- `1` — `regression === true`.

---

## `export` — convert tokens to other formats

### Synopsis

```bash
npx @google/design.md export --format <fmt> <file>

npx @google/design.md export --format json-tailwind DESIGN.md > tailwind.theme.json
npx @google/design.md export --format css-tailwind  DESIGN.md > theme.css
npx @google/design.md export --format dtcg          DESIGN.md > tokens.json
```

### Arguments and flags

| Option     | Type                                                       | Default | Required | Description                                  |
| ---------- | ---------------------------------------------------------- | ------- | -------- | -------------------------------------------- |
| `file`     | positional                                                 | —       | yes      | Path to DESIGN.md, or `-` for stdin.         |
| `--format` | one of `css-tailwind`, `json-tailwind`, `tailwind`, `dtcg` | —       | yes      | Output format (no default — must specify).   |

### Format matrix

| `--format`        | Output type | Description                                                                                              |
| ----------------- | ----------- | -------------------------------------------------------------------------------------------------------- |
| `json-tailwind`   | JSON        | Tailwind v3 `theme.extend` config object (drop into `tailwind.config.js`).                               |
| `tailwind`        | JSON        | Alias for `json-tailwind` (backwards-compatible).                                                        |
| `css-tailwind`    | CSS         | Tailwind v4 `@theme { ... }` block with CSS custom properties.                                           |
| `dtcg`            | JSON        | W3C Design Tokens Format Module (`tokens.json`).                                                         |

### Tailwind v4 CSS variable namespaces

`css-tailwind` emits CSS custom properties under these v4 namespaces:

- `--color-*`
- `--font-*`
- `--text-*`
- `--leading-*`
- `--tracking-*`
- `--font-weight-*`
- `--radius-*`
- `--spacing-*`

### Exit code

- `1` — invalid `--format` value, emitter failure, OR
  `lint(content).summary.errors > 0`.
- `0` — otherwise.

(I.e. files with lint errors are still emittable in some cases but the
process ends with code 1; check the actual `stderr` for the error
message in the JSON `{"error": "..."}` shape.)

---

## `spec` — print the spec for prompt injection

### Synopsis

```bash
npx @google/design.md spec
npx @google/design.md spec --rules
npx @google/design.md spec --rules-only --format json
```

### Arguments and flags

| Option          | Type    | Default    | Description                                                              |
| --------------- | ------- | ---------- | ------------------------------------------------------------------------ |
| `--rules`       | boolean | `false`    | Append the active linting rules table after the spec body.               |
| `--rules-only`  | boolean | `false`    | Output ONLY the active linting rules table (skips the spec body).        |
| `--format`      | string  | `markdown` | One of `markdown`, `json`.                                               |

(No positional file argument — this command emits static content.)

### Output shape

- `--format markdown` (default): the contents of `docs/spec.md`,
  optionally with `## Active Linting Rules\n\n<table>` appended.
- `--format json` with `--rules-only`:
  ```json
  { "rules": [ { "name": "...", "severity": "...", "description": "..." }, ... ] }
  ```
- `--format json` without flags:
  ```json
  { "spec": "<full spec markdown as string>" }
  ```
- `--format json --rules`:
  ```json
  { "spec": "...", "rules": [ ... ] }
  ```

### Exit code

Always `0` (no failure conditions).

---

## Programmatic API

The linter is also exposed as a library import:

```typescript
import { lint } from '@google/design.md/linter';

const report = lint(markdownString);

console.log(report.findings);       // Finding[]
console.log(report.summary);        // { errors, warnings, info }
console.log(report.designSystem);   // Parsed DesignSystemState
```

Type-only re-exports of interest (per `package.json#exports.linter` and
the rule registry):

- `Finding` — `{ severity, path?, message }`
- `LintRule` — `(state: DesignSystemState) => Finding[]`
- `DEFAULT_RULE_DESCRIPTORS` — full rule list with name + severity +
  description + run function.
- `TailwindEmitterHandler`, `TailwindV4EmitterHandler`,
  `serializeTailwindV4` — used by `export`.
- `DtcgEmitterHandler` — used by `export --format dtcg`.

## Dependency snapshot

From `packages/cli/package.json` (cross-format awareness for the
extractor skill author):

- `unified`, `remark-parse`, `remark-frontmatter`, `remark-mdx`,
  `remark-stringify`, `unist-util-visit` — Markdown / MDX parsing.
- `yaml` — YAML frontmatter parsing.
- `zod` — Schema validation.
- `citty` — CLI framework (powers the subcommand registration).
- `ink`, `react`, `@json-render/core`, `@json-render/ink` — TTY render.
- `mdast`, `@types/mdast` — Markdown AST types.
- Build target: `node`, ESM only.
- Spec sync: build step copies `spec-config.yaml` and `docs/spec.md`
  into `dist/linter/` so the published package is fully self-contained
  (no network fetch at runtime).

## One-liner cheat sheet

```bash
# Validate
npx @google/design.md lint DESIGN.md

# Validate from stdin
echo "$content" | npx @google/design.md lint -

# Detect regressions vs baseline
npx @google/design.md diff baseline.md current.md

# Generate Tailwind v3 config
npx @google/design.md export --format json-tailwind DESIGN.md > theme.json

# Generate Tailwind v4 @theme block
npx @google/design.md export --format css-tailwind DESIGN.md > theme.css

# Generate W3C DTCG tokens.json
npx @google/design.md export --format dtcg DESIGN.md > tokens.json

# Print spec for prompt injection
npx @google/design.md spec

# Print just the lint rules as JSON
npx @google/design.md spec --rules-only --format json
```
