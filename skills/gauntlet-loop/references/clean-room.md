# The clean room

## Why

The article does not call for this. It follows from rule one.

"Give it the goal, not your implementation" is the load-bearing instruction, and every installed skill and MCP server is an implementation sitting in the agent's context waiting to be chosen. A gauntlet agent that can see a cloning skill clones. One that can see a design system MCP reaches for the design system. Neither one *decides*, which is the entire source of the quality.

The second reason is contamination of the critics. Rules in a global CLAUDE.md about tone, length, formatting or persona propagate into every builder and every critic that gets spawned. A critic told to be entertaining is not a harsh critic.

The third is context. Long runs spawn a large fleet of sub-agents. Every tool definition in scope is paid for repeatedly, in every one of them.

You cannot strip any of this from a session that is already running. MCP config edits race against live sessions and lose. It only works at launch.

## The launch

```bash
"<skill-dir>/scripts/launch-gauntlet.sh" <run-dir> [permission-mode] [model]
```

`<skill-dir>` is wherever this skill is installed: `~/.claude/skills/gauntlet-loop` personally, somewhere under `~/.claude/plugins/` as part of a plugin. Resolve it before handing the command to anyone.

Which runs:

```bash
cd <run-dir>
claude \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --disable-slash-commands \
  --setting-sources project,local \
  --effort xhigh \
  --permission-mode auto \
  --model opus \
  "$(cat GAUNTLET.md)"
```

| Flag | Effect |
|---|---|
| `--strict-mcp-config --mcp-config '{"mcpServers":{}}'` | ignores every configured MCP server and loads an empty set. Zero MCP tools. |
| `--disable-slash-commands` | disables all skills. Built-in CLI commands like `/config` and `/model` still work. |
| `--setting-sources project,local` | drops user-level settings and the global `~/.claude/CLAUDE.md`. Project settings still load, so run in a fresh directory. |
| `--effort xhigh` | the effort half of ultracode. |
| `--permission-mode auto` | classifier-gated approval. Doesn't stall on every Bash call the way `acceptEdits` does, doesn't blanket-bypass the way `bypassPermissions` does. |
| `--model opus` | Opus for visual and creative work, per the article. |
| `"$(cat GAUNTLET.md)"` | starts interactive with the prompt already sent, so the user can watch and stop it. |

## Verified

Running that combination and asking the session to enumerate itself returns:

- Global CLAUDE.md persona rules: absent
- Skills available: 0
- MCP tools: 0
- Tools present: Agent, Workflow, Bash, Read, Write, Edit, WebFetch, WebSearch, Task\*, plus the rest of the built-ins

Everything a gauntlet needs, nothing that would make its decisions for it.

To re-verify after a Claude Code update:

```bash
cd /tmp && claude -p --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --disable-slash-commands --setting-sources project,local --effort low \
  "List the exact names of every tool available to you, one per line, and say how many skills you have."
```

## What you give up

**The `/loop` skill.** Disabling skills disables it, and Shumer's original prompt used `/loop` by name. This costs nothing. The article is explicit that the slash command is not the point:

> Claude Code includes a /loop skill for repeated agent work, but the more important idea is that there should be no arbitrary final round.

Prose looping plus the Workflow tool covers it, and Workflow's loop-until-dry constructs are a better fit for gauntlets than a fixed-interval wake-up anyway. Say "loop", "keep going", "don't stop until" in the prompt and it loops.

**Domain skills.** Deliberate. If a skill genuinely contains knowledge the gauntlet needs (a house font pipeline, an internal API), copy the relevant text into the run directory as a file the agent can read, rather than re-enabling skills. A file is inert; a skill actively competes for the route.

## ultracode

`ultracode` is not a CLI value. It is `xhigh` effort plus a standing opt-in to dynamic multi-agent workflows.

The launcher covers both halves: `--effort xhigh` for effort, and the literal word `ultracode` at the end of `GAUNTLET.md` for the workflow keyword trigger. Keeping Shumer's closing line intact is functional, not decorative.

One-time check before the first gauntlet: open `/config` and confirm dynamic workflows are enabled. Ultracode requires it. This is a persistent setting, so it only needs doing once.

## Do not use `--bare`

It looks perfect for this and it is a trap. `--bare` reads authentication strictly from `ANTHROPIC_API_KEY`, never from OAuth or the keychain, so a Max or Pro subscription cannot authenticate and the run either fails or bills to a separate API balance.

## Permission modes

| Mode | Use when |
|---|---|
| `auto` | default. Genuine walk-away runs. A classifier approves routine work and holds the rest. |
| `acceptEdits` | supervised runs. File edits are automatic, Bash still prompts, so a long unattended run will sit blocked. |
| `bypassPermissions` | only in a directory that contains nothing you would mind losing. Nothing is gated. Never point this at `$HOME` or a real repository. |

## Troubleshooting

**It stopped after one pass.** The bar was reachable, or it was prose rather than files. Check that `reference/` has real artifacts in it and that the critic had something to lose to. Raise the bar and relaunch.

**Critics keep passing everything.** The critic is probably reading builder summaries instead of the artifact. Confirm the prompt says the critic looks only at real output, and that the output is actually inspectable from the run directory: a game that doesn't render in a headless browser gives its critic nothing to see.

**The pieces are individually good and collectively incoherent.** Expected with many parallel agents. Add the smoothing-pass sentence: one fresh agent per wave inspects the whole result and reconciles it before the next wave.

**Workspace trust dialog on launch.** First run in a new directory. Accept it once.

**It burned hours and produced little.** Usually decomposition that was too coarse. "Make the game better" is not a piece. "Make this one tree beat the reference tree" is. The lead agent chooses this, so the fix is upstream: a sharper, more specific bar produces a sharper decomposition.
