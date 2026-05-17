---
name: designmd-ripper
description: |
  Generate a 100% spec-compliant Google DESIGN.md file from any public website URL. Deeply extracts the live design system via Playwright (colors, typography, spacing, components, layout, fonts, shadows), proposes subpages for user approval, then synthesizes a DESIGN.md conforming to the canonical Google design.md schema with zero lint errors. Portable to Stitch, Tailwind, Figma.

  Use aggressively whenever the user provides a website URL and asks for: DESIGN.md, design.md, design-md, design system extraction, design tokens, design spec, brand spec, "extract the design", "capture the visual identity", "make a design system from this site", "what is this site's design system", or anything implying turning a live site into a structured design contract. Also fires on mentions of the Stitch design.md format or @google/design.md CLI.

  Do NOT use for: generating site code (use `cloning`); design critiques (use `design-review`).
metadata:
  model: opus
  context: fork
  effort: max
---

# Website to DESIGN.md

Turn any public website into a **spec-correct Google DESIGN.md** that anyone
(or any agent — Stitch, Tailwind theme generator, Figma importer) can use
to rebuild a site aligned with the original's visual identity.

The output is one markdown file with YAML frontmatter (design tokens) +
body sections (rationale prose). It MUST lint clean against the canonical
linter: 0 errors, 0 warnings, 1 info (the unavoidable `token-summary`).

---

## Reference files (read on demand, in this order)

1. `references/spec.md` — the full canonical DESIGN.md specification.
   **Read this in full before writing any DESIGN.md.** It defines the
   frontmatter schema, section order, and every accepted token shape.
2. `references/synthesis-guide.md` — the mapping layer from raw
   extraction signals to spec-correct fields, plus a 12-item strictness
   checklist. **Read this every time** before composing the file.
3. `references/linting-rules.md` — all 8 lint rules with trigger
   conditions. **Consult when a lint run reports findings.**
4. `references/canonical-example.md` — the official "Atmospheric Glass"
   example. **Read once** to see what a complete, real DESIGN.md looks
   like. Do not copy its tokens — copy its structure and density.
5. `references/cli.md` — `@google/design.md` CLI reference. Consult only
   if the lint step misbehaves.

---

## Inputs the user provides

- A **primary URL** (required). Anything reachable over public HTTP/HTTPS.
- An optional **output path** for the DESIGN.md (defaults below).

That's it. The skill discovers everything else.

---

## Workflow

### Step 1 — Extraction (Playwright, in a subagent)

CLAUDE.md is explicit: **never run Playwright tools in the main session**.
That rule targets the `mcp__playwright__*` tool surface — direct browser
control by the model. `extract.py` is a Python subprocess that uses the
`playwright` package as a library, not as an MCP tool, so running it via
the Bash tool is allowed even in the main session.

That said, the cleanest pattern is still to dispatch via the Agent tool
when available: the subagent's transcript stays out of your context, the
extraction can run while you do other things, and the boundary is
unmistakable. If the Agent tool is not available in the current
environment (e.g. some Claude.ai contexts), run `extract.py` directly
via Bash — that is the supported fallback.

The script wraps the `cloning` skill's `clone_orchestrator.py`, which is
the already-battle-tested Playwright pipeline that captures
multi-viewport screenshots, computed CSS tokens, fonts (with @font-face
URLs), layout primitives, components, and animations.

Spawn it like this:

```text
Agent({
  description: "Extract design data from <URL>",
  subagent_type: "general-purpose",
  prompt: "Run this command and report the resulting extraction directory:\n\n  python3 /Users/osamakhalil/.claude/skills/designmd-ripper/scripts/extract.py <URL>\n\nThe command prints a JSON summary on stdout when done. Read the summary, then return the value of `extraction_dir` and the full `candidate_subpages` array. Do NOT run any other commands. Do NOT analyze the output."
})
```

The subagent's only job is to invoke the extraction so the main session
never touches Playwright tools directly. Pass `--no-video` if the site is
huge or the user is impatient.

### Step 2 — Propose subpages and get approval

The extractor surfaces up to 20 candidate same-origin links from the
primary page's navigation, secondary nav, and main content links.

Show the user the list with `AskUserQuestion` (multiSelect) so they can
pick which subpages, if any, should also be extracted. Most sites benefit
from including 2–3 subpages (e.g., a pricing page reveals card components
the homepage hides; an "about" page often has secondary brand colors).

If the user picks zero, skip to Step 4. If they pick some, return to
Step 1 with the chosen URLs passed via `--include-subpages url1,url2,...`.

If the candidate list is empty (rare — usually a single-page app with
JS-driven routing), tell the user no subpages were detected and proceed
without subpages. Do not invent subpages.

### Step 3 — Render the synthesis brief

Once all approved pages have been extracted, run:

```bash
python3 /Users/osamakhalil/.claude/skills/designmd-ripper/scripts/render_brief.py <extraction_dir>
```

This produces `<extraction_dir>/synthesis-brief.md` — a compact, readable
summary of every signal the extractor captured, organized by DESIGN.md
section. It is your primary source of truth from here on out.

### Step 4 — Write DESIGN.md (this is where the judgment lives)

Read, in this order:

1. The synthesis brief from Step 3.
2. `references/spec.md` (skim if you have read it recently; read in full
   otherwise).
3. `references/synthesis-guide.md` — the 12-item strictness checklist
   and the field-by-field mapping rules. Apply these rules.
4. `references/canonical-example.md` — recall what good looks like.
5. At least the primary mobile + desktop screenshots from the extraction
   directory (look at the actual images — the JSON loses character).

Then write DESIGN.md. Start from `assets/template.md` if useful; replace
its placeholders with real tokens and prose.

**Default output path** (when the user didn't specify one):

```text
~/Desktop/designmd-ripper/<host>-<timestamp>/DESIGN.md
```

`extract.py` already creates that directory and drops the extraction artifacts (screenshots, JSON, synthesis brief) there. Save `DESIGN.md` at the same path so everything lives in one place.

Always print the absolute path to the user when you save.

### Step 5 — Lint and tighten

Validate immediately:

```bash
bash /Users/osamakhalil/.claude/skills/designmd-ripper/scripts/lint.sh <path/to/DESIGN.md>
```

The target is:

- `errors: 0`
- `warnings: 0`
- `infos: 1`   (the unavoidable `token-summary`)

If `npx`/Node is missing, fall through and use the manual checklist at
the top of `references/synthesis-guide.md`.

If errors or warnings appear, **DO NOT ship the file**. Open
`references/linting-rules.md`, find the rule, apply the fix, and re-lint.
Common fixes:

| Finding              | Fix                                                                                                                       |
| :------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| `broken-ref` error   | A `{path.to.token}` doesn't resolve. Either define the token or change the reference to one that does.                    |
| `broken-ref` warning | A component uses a property outside the 8-token closed set. Move it to prose, or remove it.                               |
| `missing-primary`    | Add `primary:` to `colors:`.                                                                                              |
| `missing-typography` | Add at least one typography token.                                                                                        |
| `missing-sections`   | Add `spacing:` and `rounded:` (even minimal scales).                                                                      |
| `contrast-ratio`     | Bad WCAG pair on a component. Swap the `textColor` for a lighter/darker variant defined in `colors`.                      |
| `orphaned-tokens`    | Reference the unused color from at least one component, OR rename it to fit the MD3 family system, OR delete it.          |
| `section-order`      | Reorder the `##` headings to: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts. |

Re-lint after each fix. Stop only when the target counts are hit.

### Step 6 — Report back

In your final message:

1. The absolute path to the saved DESIGN.md.
2. The lint summary (`errors / warnings / infos`).
3. One sentence on what the design system "is" in plain English ("Linear's
   design system is a dark-first developer-tool aesthetic anchored by Inter
   and a near-black canvas, with a single purple/blue gradient as the
   brand accent").
4. The extraction directory, in case the user wants to re-run synthesis
   without re-scraping.

Keep it under ~6 lines.

---

## Behavior rules

- **Never skip the lint step.** A DESIGN.md that doesn't lint is not done.
- **Never invent tokens to be "thorough".** The smallest set of tokens
  that captures the visual identity is correct; padding the file with
  fake values triggers `orphaned-tokens` and dilutes the spec.
- **Always quote hex values** in YAML (`primary: "#1A1C1E"`). Unquoted
  hex is a YAML comment in many loaders.
- **Component sub-tokens are a CLOSED SET of 8**: `backgroundColor`,
  `textColor`, `typography`, `rounded`, `padding`, `size`, `height`,
  `width`. Anything else belongs in prose, not in the component map.
- **Read with tolerance, write with strictness.** Source sites use
  `rgba()`, `transparent`, CSS shorthand `padding`. Convert to hex and
  single-Dimension on the way out — even though the linter would accept
  the loose forms.
- **Playwright stays in subagents.** No exceptions, per CLAUDE.md.
- **If extraction fails** (site requires login, blocks bots, never
  finishes loading): say so plainly. Offer to retry with `--no-video`,
  with a different subagent, or to extract a partial output. Do not
  fabricate tokens.

---

## What this skill is NOT

- Not a website cloner — it does not produce HTML/CSS/React code. For
  that, use the `cloning` skill (which shares the extraction pipeline).
- Not a design critique — it captures what IS, not what should be.
- Not a generic markdown writer — every DESIGN.md must conform to the
  canonical schema in `references/spec.md`. Free-form designer notes
  belong elsewhere.

---

## Quick command crib

```bash
# 1. Extract (run inside subagent)
python3 <SKILL>/scripts/extract.py https://example.com

# 1b. Extract with subpages
python3 <SKILL>/scripts/extract.py https://example.com \
  --include-subpages https://example.com/pricing,https://example.com/about

# 2. Render brief
python3 <SKILL>/scripts/render_brief.py ~/Desktop/designmd-ripper/example.com-<ts>

# 3. After writing DESIGN.md, lint
bash <SKILL>/scripts/lint.sh /path/to/DESIGN.md
```

Where `<SKILL>` = `/Users/osamakhalil/.claude/skills/designmd-ripper`.
