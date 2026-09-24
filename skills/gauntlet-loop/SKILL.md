---
name: gauntlet-loop
description: Run Matt Shumer's Gauntlet Loop, the prompting method behind Claude of Duty, to build something at a quality level normal prompting never reaches. Interviews the user for a goal and a real inspectable quality bar, captures that bar as files on disk, writes a short Shumer-style prompt, and hands over a clean-room Claude Code session (no MCP servers, no other skills, no global CLAUDE.md) where a lead agent splits the work, pairs every piece with an independent harsh critic, and loops on blind A/B against the bar until the user stops it. Use this whenever someone wants a thing built to an ambitious standard rather than merely working: they name a real thing to match or beat ("as good as Call of Duty", "like Linear", "Stripe-quality", "reads like Paul Graham"), or say AAA, world-class, utterly perfect, best in the world, "don't stop until", "one-shot this", "let it run for hours", "go all out". Use it for games, products, sites, campaigns, research, or long-form writing where quality is the entire point. Also use on any mention of gauntlet loop, gauntlet, Claude of Duty, Shumer's method, builder-critic loop, or blind A/B against a reference. Do not use for small fixes, single features, debugging, or anything wanted in minutes.
---

# Gauntlet Loop

The method behind [Claude of Duty](https://github.com/mshumer/Claude-of-Duty): one prompt, many hours, ~55,000 lines, every texture and sound generated from scratch, no human steering. Source article: https://somethingbig.ai/gauntlet-loop

## Why it works

A model stops when nothing tells it that it isn't done. "Make it amazing" gives it no way to lose, so it produces one decent result and declares victory.

A Gauntlet Loop removes the stopping condition. You hand the agent something real that is *better than what it just made*, and an independent critic whose only job is to say "the reference won, here is the biggest gap." Now the agent can lose. It keeps going because there is always another gap.

Everything in this skill exists to serve that: give it a bar it cannot talk its way around, split the work small enough to attack, never let the builder grade itself, and keep looping longer than anyone else would.

## The one thing that kills it

**You are about to want to write a spec. Don't.**

The instinct when someone says "build me a racing game" is to interview them into an architecture: engine, physics library, state model, file layout, phase plan. Every one of those decisions replaces the model's judgment with yours, and the model's judgment is currently better than yours at deciding how to attack a large goal. Shumer's original prompt contained no architecture at all.

Hold this distinction the whole way through:

- **The route is the model's.** Architecture, decomposition, tech choices, how many rounds, which pieces run in parallel. Never prescribe these. Never ask about them.
- **The method is yours.** The bar, builder/critic separation, blind comparison, "name one gap", looping without a final round, the live progress page. Never trim these to sound brief.

Minimal means minimal about the route. It never means dropping the method.

## Phase 1: Frame the goal

Restate what they want in one sentence, at the level of a destination rather than a route.

- Good: "A browser-playable kart racer that feels like Mario Kart 8."
- Bad: "A Three.js kart racer with a physics loop, four tracks, and an ECS architecture."

If their request already contains architecture, gently strip it and confirm: "I'm going to hand the agent the goal and let it pick the approach, because that's where this method gets its quality. Losing the Three.js requirement, unless it's a hard constraint?"

## Phase 2: Interview

One `AskUserQuestion` call, four questions. Nothing about implementation.

1. **The bar.** "What real thing already exists at the quality you want?" Offer 3 concrete candidates you researched for their domain plus an option for you to pick one. This is the most important answer you will get.
2. **How winning is judged.** What does the critic actually look at to decide ours lost? Rendered pixels side by side / playing it / reading it aloud / a test suite passing / a measured number. Different answers produce very different critics.
3. **Hard constraints.** Real ones only, the kind that change what "done" means: must run in a browser tab with no install, must be RTL Arabic, must work on a phone, no external assets, must ship by Friday. Preferences are not constraints and do not go in the prompt.
4. **Walk-away mode.** Whether they want a true unattended run (`auto` permission mode, they check the progress page from their phone) or a supervised one they watch in the terminal.

If they already answered something in their opening message, don't re-ask it. Confirm it in a line instead.

## Phase 3: Materialize the bar

This is where the skill earns its keep, and where most people running this method fail. A bar written in prose is not a bar. The critic cannot lose to a sentence.

**A bar is a file the critic can open, or a command it can run.** Nothing else counts.

Create the run directory (`~/dev/gauntlet-<slug>/` unless they name one) and fill `reference/` with 3 to 8 real artifacts. Read `references/bar-catalog.md` for how to source and capture the bar in each domain: visual and 3D, web and product UI, writing, backend and systems, marketing, research, audio and video.

Capture the bar *now*, in this session, because this session still has browser automation, MCP servers and web access. The clean room deliberately has none of that. Delegate Playwright work to a subagent; claude-in-chrome runs inline, per the global CLAUDE.md.

Then write `reference/BAR.md`: one sentence naming the bar, one sentence on why it is the right yardstick, and the literal comparison instruction the critic will follow.

Two calibration rules from the article:

- **Unreachable is correct.** Claude of Duty never beat Call of Duty. Shumer stopped the run while it was still improving. The bar's job is to supply direction and deny the agent a moment where it can call the work "pretty good for AI." If the bar looks achievable in a few hours, it is too low. Raise it.
- **Comparable beats aspirational.** "Better than every racing game" is not inspectable. Four annotated frames from Mario Kart 8 are.

## Phase 4: Write the prompt

Write `GAUNTLET.md` in the run directory. Target 120 to 200 words. If it is longer than Shumer's original, you are specifying the route.

Read `references/prompt-patterns.md` for the original prompt, the fill-in template, worked adaptations across domains, and the exact phrases that carry weight.

Every prompt needs these seven elements and nothing else:

1. The goal, one sentence, at destination level.
2. The bar, named, with the path to `reference/`.
3. Fan out sub-agents, each owning one piece.
4. A **separate** critic per piece with fresh context that never sees the builder's reasoning.
5. Blind side-by-side against the reference; when ours loses, name the single biggest gap and send it back.
6. A live progress page, updated as it works, contents left to the agent.
7. Loop with no final round. End on the literal word `ultracode`, which is both the effort signal and the harness keyword that opens up multi-agent workflows.

Optionally add one sentence about a smoothing pass between waves. When many agents improve separate parts, the parts get individually good and collectively incoherent. One fresh agent per wave, inspecting the whole and reconciling it, fixes that. The article calls this optional and it is: it is polish on the loop, not part of it.

Show the user the finished prompt before launching. It is short enough to read in twenty seconds, and they should recognize their own goal in it.

## Phase 5: Hand off to the clean room

The gauntlet runs in a **fresh session with nothing else loaded**. Not because the article says so, it doesn't, but because rule one is "let it choose the route" and every installed skill and MCP server is a pre-chosen route sitting in the agent's context. A gauntlet agent that can see a cloning skill will clone instead of deciding. Personality and style rules in a global CLAUDE.md leak into every builder and every critic.

You cannot strip these mid-session. It only works at launch.

```bash
"<skill-dir>/scripts/launch-gauntlet.sh" <run-dir> [permission-mode] [model]
```

`<skill-dir>` is this skill's own directory, which the harness prints when the skill loads. It is `~/.claude/skills/gauntlet-loop` for a personal install and a path under `~/.claude/plugins/` for a plugin install, so resolve it rather than assuming. Give the user the fully resolved command, not the placeholder.

Defaults to `auto` permission mode and Opus. Verified to produce: zero MCP servers, zero skills, no global CLAUDE.md, with Agent, Workflow, Bash, Read, Write, Edit, WebFetch and WebSearch all intact.

Hand the user the command, tell them where the progress page will be, and tell them how to stop it. Do not launch it for them; starting a multi-hour run is their call.

Read `references/clean-room.md` for what each flag does, how to verify the isolation held, the one-time `/config` check that ultracode needs, and what you give up by disabling skills.

## Phase 6: While it runs

The run is unattended by design. The progress page is what replaces you asking for updates. Tell the user plainly:

- Open the progress page in a browser, including from their phone.
- The run does not have a natural end. They stop it when they like the result, when improvements stop mattering, or when they have spent as much compute as they want to spend.
- Stop with Esc in the gauntlet terminal.
- It will still be improving when they stop it. That is the method working, not a failure.

When they come back with the result, treat any follow-up as a new goal against the same bar rather than a patch. The loop is the unit of work.

## Reference files

- `references/bar-catalog.md`: sourcing and capturing a real bar, per domain
- `references/prompt-patterns.md`: the original prompt, the template, worked adaptations
- `references/clean-room.md`: launch flags, verification, tradeoffs, troubleshooting
- `scripts/launch-gauntlet.sh`: the clean-room launcher
