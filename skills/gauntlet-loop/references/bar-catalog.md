# Sourcing and capturing the bar

The bar is the whole method. Everything else is scaffolding around it.

## What qualifies

A bar has to survive three tests:

1. **Inspectable.** The critic can open it, run it, or measure it. A URL mentioned in prose is not inspectable. A PNG in `reference/` is.
2. **Comparable.** The critic can put ours and the reference next to each other and pick a winner without knowing which is which. "World-class" fails this. Four annotated frames pass it.
3. **Out of reach.** If the agent can plausibly match it in a few hours, it will match it and stop. Call of Duty was never going to be beaten in a browser tab, which is exactly why it worked.

## The yardstick rule

References are a standard to be measured against, never source material to be lifted. Assets, characters, copy, trade dress and brand marks stay in the reference folder. Only the *quality level* crosses over.

Say this in `BAR.md` explicitly. Critics read it, and it stops a builder from "closing the gap" by copying.

## Capture now, not later

Capture the bar in the interview session, which still has browser automation, MCP servers and web access. The clean room has none of them and will not be able to fetch anything visual.

Delegate any Playwright or browser work to a subagent rather than driving it in the main session.

---

## Visual: games, 3D, real-time graphics

**Bar:** the actual shipped game, at the specific quality dimension you care about.

**Capture:** 4 to 8 stills at the target resolution, pulled from gameplay footage or press kits. Get *variety of subject*, not variety of scene: one lighting frame, one weapon or character close-up, one foliage or environment frame, one UI/HUD frame, one motion-blur or particle frame. A critic comparing "our tree" needs a reference tree, not a reference vista.

**Critic compares:** rendered screenshot of ours versus reference still, same subject, blind.

**Raise it by:** picking the most recent title rather than the one you played, and by cropping in. A cropped reference gun barrel is a far harsher bar than a wide gameplay shot.

Files: `reference/lighting-01.png`, `reference/weapon-closeup.png`, ...

---

## Web and product UI

**Bar:** 3 to 5 best-in-class real sites in the category. Linear, Stripe, Vercel, Arc, Raycast are the usual suspects for product; pick category-appropriate ones and say why.

**Capture:** full-page screenshots at three viewports (1440, 768, 390) via a Playwright subagent. Add a short `reference/interaction-notes.md` covering motion, easing and hover behavior, since screenshots cannot carry those.

**Critic compares:** ours rendered at the same viewport versus reference, blind. Separate critics for typography, spacing rhythm, motion, and empty/loading states, because they fail independently.

**Raise it by:** including one reference that is genuinely better than the goal deserves. A landing page held to Stripe's spacing discipline gets a better landing page.

Files: `reference/linear-1440.png`, `reference/stripe-390.png`, `reference/interaction-notes.md`

---

## Writing: essays, long-form, docs

**Bar:** 6 to 12 paragraphs from writers who have the specific property you want. Clarity and compression: Paul Graham. Structural argument: Scott Alexander. Technical precision: Rich Hickey transcripts. Product narrative: Fadell, Rams.

**Capture:** paste the paragraphs into `reference/paragraphs.md`, each labelled with the property it demonstrates.

**Critic compares:** paragraph against paragraph, blind, on one question only: which is clearer per word. Not which sounds better, not which is more like the reference. Voice is not the bar; clarity is.

**Raise it by:** picking the reference author's *best* paragraphs, not representative ones.

Files: `reference/paragraphs.md`

---

## Backend, systems, engineering

**Bar:** something executable. This domain is the easiest to get a hard bar in and the most commonly wasted.

Options, best first:

- A test suite the build must pass, including the tests it will fail today.
- A latency or throughput target with the measuring command written down.
- A failure-injection script: kill the database mid-write, drop the network, corrupt a message, and require correct recovery.
- A reference implementation to diff behavior against.
- A security checklist a fresh critic runs as an attacker.

**Capture:** the tests, the benchmark command, the injection script, all runnable from the run directory.

**Critic compares:** runs the command. There is no aesthetic judgment here and that is the strength of this domain: the bar cannot be argued with.

**Raise it by:** setting the number where it hurts. p99 under 40ms is a bar. "Fast" is not.

Files: `reference/bar-tests/`, `reference/bench.sh`, `reference/chaos.sh`

---

## Marketing and campaigns

**Bar:** real campaigns with real outcomes, plus the number they hit.

**Capture:** the creative itself (ad images, landing page screenshots, email screenshots, video stills) into `reference/`, and the performance claim into `BAR.md`.

**Critic compares:** ours against the reference on the specific job the creative does. Stopping the scroll is one critic. Making the offer legible in three seconds is another. Do not let one critic judge "is this good marketing."

**Raise it by:** using the category leader's current work rather than a case study from four years ago.

---

## Research and analysis

**Bar:** a published piece of work at the depth you want, plus a falsifiability standard.

**Capture:** the reference report as PDF or markdown, and a `reference/standard.md` requiring every claim to carry a source the critic can open and check.

**Critic compares:** picks claims at random, follows the source, and fails the piece if the source does not say what the claim says. This one critic catches more than any stylistic comparison will.

**Raise it by:** requiring the piece to state what would change its conclusion.

---

## Audio, video, motion

**Bar:** a specific reference cut, not a genre.

**Capture:** frames as a contact sheet, because sub-agents read images and not video. `ffmpeg -i ref.mp4 -vf "fps=2,scale=480:-1,tile=4x4" reference/ref-filmstrip.png`. Add the numbers separately: duration, cut rhythm, loudness, frame rate.

**Critic compares:** our filmstrip against the reference filmstrip, plus the numeric telemetry. Never hand a critic a video file and expect it to watch it.

**Raise it by:** matching the cut rhythm, not just the look.

---

## When the user has no bar

Do not ask them to define what good means, and do not let the agent decide for itself. Go find one, then confirm it in a sentence.

The article's own instruction for this case:

> Find a concrete comparison or measurement that plays the same role for this task that real Call of Duty screenshots played for the game in Matt Shumer's Claude of Duty project. Explain why it is a useful bar, then judge every round against it.

Research 3 candidates, present them with one line each on why that bar is harsh in the right direction, and recommend one.
