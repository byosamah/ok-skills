# Writing the gauntlet prompt

## The original

This is the entire prompt that produced Claude of Duty. Nothing was added, nothing was steered afterwards.

```
I want you to build a first-person shooter at the level of the most recent Call of Duty games. It should be utterly perfect, visually beautiful, with every single thing done at AAA quality—from textures to physics to anything you could think of.

Fan out sub-agents and have sub-agents tackle each one individually so that the game is utterly perfect. You should /loop on each item and have a separate sub-agent check it visually to ensure it looks triple A. That separate sub-agent should be a really harsh critic, and if it doesn't look triple A, it should keep going.

Don't stop until each sub-agent is utterly wowed with the quality when compared with the actual Call of Duty game. It should literally compare them side by side blind and say which one looks better. Do this in ThreeJS. /loop until it's utterly perfect. Fan out sub-agents and ultracode.
```

Read what is *not* there. No file layout. No systems list. No renderer design. No round count. No phases. The single implementation word in it is "ThreeJS", and that was a genuine constraint about where the game had to run.

## The template

```
I want you to build <GOAL> at the level of <BAR>. It should be utterly perfect,
with every single part done at that quality.

The bar is in ./reference/. Look at it before you start, and keep looking at it.
<one line: what winning means, from BAR.md>

Fan out sub-agents. Break this into the smallest pieces that can be improved and
judged on their own, and give each piece its own builder. Loop on every piece,
and have a SEPARATE sub-agent judge it: a harsh critic with fresh context that
has never seen the builder's reasoning and only ever looks at the real output.
It compares ours against the reference blind, side by side, and says which is
better. When ours loses, it names the single biggest remaining gap and sends it
back for another round.

Don't stop until every critic is genuinely wowed comparing ours against <BAR>.

Keep a live progress page at ./progress.html and update it as you work. Show how
the work is evolving using whatever makes sense: screenshots, clips, drafts, test
results.

<hard constraints, if any>

Loop until it's utterly perfect. Fan out sub-agents and ultracode.
```

Slot in the four blanks, drop the constraints line if there are none, and stop.

## Phrases that carry weight

Keep these close to verbatim. They are doing real work.

| Phrase | What it prevents |
|---|---|
| "at the level of `<BAR>`" | anchors quality to a thing, not an adjective |
| "utterly perfect" | denies the model a "good enough" exit |
| "a SEPARATE sub-agent", "fresh context" | the builder grading its own homework |
| "has never seen the builder's reasoning" | the critic being talked into a pass |
| "only ever looks at the real output" | critiquing a builder's summary instead of the artifact |
| "blind, side by side" | scoring by loyalty instead of quality |
| "the single biggest remaining gap" | vague critique the builder can't act on |
| "sends it back for another round" | one-shot criticism with no loop |
| "Don't stop until" | a self-declared finish line |
| "ultracode" | effort level, and the harness keyword that unlocks multi-agent workflows |

## What never goes in

- Architecture, folder structure, module boundaries, state management
- The decomposition itself. Naming the pieces is the lead agent's job and it will do it better than you, because it will have looked at the reference first.
- A number of rounds, phases, or waves. Any number is an invitation to stop there.
- Preferences dressed as constraints. "I like dark mode" is a preference. "Must be readable in direct sunlight" is a constraint, and notice it leaves the route open.
- Anything the reference folder already says. If `BAR.md` covers it, the prompt does not repeat it.

## Worked adaptations

**Product landing page**

> I want you to build the landing page for <product> at the level of Linear and Stripe. It should be utterly perfect, with every single part done at that quality. The bar is in ./reference/: full-page captures at three viewports plus interaction notes. Winning means a critic holding ours next to theirs at the same viewport cannot tell which one shipped from a real design team.
>
> Fan out sub-agents. Break this into the smallest pieces that can be improved and judged on their own, and give each piece its own builder. Loop on every piece, and have a SEPARATE sub-agent judge it: a harsh critic with fresh context that has never seen the builder's reasoning and only ever looks at the rendered page. It compares ours against the reference blind, side by side, and says which is better. When ours loses, it names the single biggest remaining gap and sends it back.
>
> Don't stop until every critic is genuinely wowed comparing ours against Linear and Stripe. Keep a live progress page at ./progress.html and update it as you work.
>
> Must work at 390px and be readable in direct sunlight.
>
> Loop until it's utterly perfect. Fan out sub-agents and ultracode.

**Backend service**

> I want you to build <service> at the level of the bar in ./reference/. Winning is mechanical: `./reference/bar-tests` all pass, `./reference/bench.sh` reports p99 under 40ms at 2000rps, and `./reference/chaos.sh` recovers cleanly every time.
>
> Fan out sub-agents ... have a SEPARATE sub-agent judge it: a harsh critic with fresh context that runs the commands itself and never trusts a builder's report of a passing run. One of the critics is an attacker: it tries to break what the others built.
>
> Don't stop until all three commands pass cleanly from a cold start, repeatedly.
>
> Loop until it's utterly perfect. Fan out sub-agents and ultracode.

**Long-form essay**

> I want you to write <piece> at the level of the paragraphs in ./reference/paragraphs.md. Winning means a critic reading one of our paragraphs against one of theirs, not knowing which is which, picks ours as the clearer of the two. Match the clarity, not the voice.
>
> Fan out sub-agents. The argument, the opening, each section, each example and each transition can be improved and judged separately. Loop on every piece, and have a SEPARATE sub-agent judge it: a harsh critic with fresh context that reads the actual prose, compares blind, and when ours loses, names the single biggest gap and sends it back.
>
> Don't stop until every critic picks ours. Keep a live progress page at ./progress.html showing drafts over time.
>
> Loop until it's utterly perfect. Fan out sub-agents and ultracode.

## Provenance: the article's meta-prompt

Shumer's own generator, for reference. This skill does what it describes, with the bar-capture and clean-room steps added.

```
I want to run a Gauntlet Loop for this goal:

[GOAL]

Possible references or quality bars:

[OPTIONAL REFERENCES]

Choose the strongest concrete bar that an agent can actually inspect and compare its work against. If I have not supplied one, propose a useful comp or measurement that plays the same role for this task that real Call of Duty screenshots played for Matt Shumer's Claude of Duty game (read the prompt: https://github.com/mshumer/Claude-of-Duty/blob/main/prompt.md). Explain the bar in one sentence.

Then write a short prompt for Claude Code or Codex in the style of Matt's prompt (minimal is better here, we want the agent to decide the specifics!).

Give the lead agent the goal and the bar, but let it choose the approach. Tell it to divide the goal into the smallest pieces that can be improved and judged independently. For each important piece, it should fan out a builder and a separate critic with fresh context.

Each critic must inspect the real output, compare it directly with the bar—using a blind A/B comparison when possible—identify the biggest remaining gap, and send it back for another round. Keep looping until our output wins or I stop the run.

Have the lead agent maintain a simple live progress page that shows the work evolving over time.

Have it use subagents and ultracode. Do not prescribe the architecture, exact decomposition, or a fixed number of rounds. Keep the final prompt short, just like Matt's.
```
