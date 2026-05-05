# Pillar Rubrics — Detailed Scoring Anchors

This file gives the model precise anchors for scoring each pillar 0-10. The
SKILL.md body has the headline standard for each pillar; this file has the
calibration detail so scoring is consistent across reviews.

**Glyph mapping** (used in sidecar review tables):
- `8-10` → ✓ (working)
- `5-7`  → ⚠ (partial / needs work)
- `0-4`  → ❌ (broken / missing)

**Calibration philosophy:** Tony is a critic, not a coach. Default to strict
scoring. A 7/10 means "actually working", not "good effort". A 10/10 is
extremely rare — it means the spec demonstrates mastery of the pillar with
specific evidence. Don't inflate scores to feel polite. The skill's value
comes from honest, sometimes uncomfortable verdicts.

---

## Pillar 1 · STORY-FIRST

**Standard:** A product without a story is a feature with a logo. The story
has to come first because it's the only thing the user, the team, and
investors carry with them. (Paraphrased from Build, "Why Storytelling Matters".)

**What to look for in the spec:**
- Read the first 3 paragraphs. Is there a *human* in them?
- Does the spec open with a *moment* (a specific user, in a specific situation,
  with a specific feeling)? Or with "this feature adds X"?
- Can you, after reading the opening, retell the spec to a stranger in 30
  seconds without looking at it?
- Does the WHY come before the WHAT?

**Score anchors:**

| Score | Description | Example signal |
|---|---|---|
| 10 | Opens with a named person in a specific moment of pain. Why → who → what flows naturally. A stranger could repeat the story back after one read. The story is the *first* thing in the spec, not buried after a feature list. | "Imagine Sarah, an English teacher in Riyadh, finishing a 30-minute MeemAin lesson..." |
| 8-9 | Opens with story but missing one element (e.g., named person but vague moment, or specific moment but no person). Recoverable with light editing. | "Teachers using MeemAin currently can't tell..." (no named person) |
| 7 | Story is present and clear but it's in paragraph 2 or 3, not paragraph 1. The opening hook is technical or a feature list. | "## Background\n\nMeemAin lessons are 30 minutes long...\n\n## Problem\n\nImagine Sarah..." |
| 5-6 | Has a problem statement somewhere, but it's buried after a feature list or behind technical setup. The "why" is implied, not said. | "## Features\n- Quizzes\n- Auto-grading\n\n## Why\nUsers want feedback faster." |
| 3-4 | Problem statement exists but is generic ("users would benefit from", "this would improve UX"). No specific human, no specific moment. | "Users find it hard to know if students understood." |
| 1-2 | Opens with "this feature does X" or "we want to add Y". No human in the first paragraph. Reads like a JIRA ticket or a feature list. | "We want to add a quiz feature to MeemAin." |
| 0 | No story anywhere in the spec. Pure feature list, technical proposal, or implementation doc dressed up as a spec. | (entire spec is bullet points of features) |

**Forcing question to include in the review:**
*"Tell me the story without using a single feature name. If you can't, the
story isn't there yet."*

**If you're scoring this pillar and unsure between two adjacent levels,
default down (stricter). Tony's posture is "the bar is high".**

---

## Pillar 2 · PAINKILLER vs VITAMIN

**Standard:** Vitamins are nice. People say they like them. People don't pay
for them when money is tight. Painkillers — people pay for those at 3 a.m.
in a parking lot. (Paraphrased from Build, recurring framing.)

**What to look for in the spec:**
- Is the pain *real, sharp, current*? Or *aspirational, vague, hypothetical*?
- Does the spec name the *workaround* the user is doing today to cope?
- Does it name the *cost* of that workaround (time, money, frustration,
  career impact)?
- Does it quote the user, or paraphrase what they actually said?

**Score anchors:**

| Score | Description | Example signal |
|---|---|---|
| 10 | Names specific user, specific pain, specific current workaround, AND specific cost (time, money, frustration). Often quotes the user. | "Sarah told us in a 30-min interview: 'I don't know what they understand.' She uses a Google Form, gets <40% response, two days late. Costs ~3 hours/week and still leaves her blind." |
| 8-9 | Has the pain + workaround + cost, but missing one element (e.g., no quote, or cost is generalized). | "Teachers spend hours every week trying to tell if students got the lesson. They use Google Forms but response rates are low." |
| 7 | Identifies pain and at least mentions a workaround, but the workaround or cost is generic. | "Teachers currently rely on manual grading, which takes time." |
| 5-6 | Identifies a problem but the evidence is hand-wavy ("users find it hard to..."). No quotes, no current workaround named, no cost. | "Users find it difficult to track lesson comprehension." |
| 3-4 | "Users would benefit from..." or "users want...". Hypothetical pain, not observed. | "Teachers would benefit from instant feedback on student understanding." |
| 1-2 | "It would be cool if..." or "modern apps have this". Pure feature thinking. | "Most learning platforms have quizzes; we should too." |
| 0 | No pain identified at all. Spec opens with the solution and never says what problem it solves. | (entire spec describes implementation, no problem statement) |

**Forcing question:**
*"Show me the workaround the user is doing today. If they're not doing one,
this isn't a painkiller — it's a curiosity."*

**Watch out for the vitamin trap:** Specs often dress vitamins as painkillers
by using emotional language ("frustrated users", "painful experience") without
specific evidence. Look for *evidence* of pain, not adjectives describing it.

---

## Pillar 3 · V1 PAINTED DOOR

**Standard:** V1 doesn't have to be perfect. V1 has to be USEFUL. V2 fixes
V1's mistakes. V3 polishes. If you're trying to ship V3 first, you'll never
ship anything. (Paraphrased from Build, "Three Generations".)

**What to look for in the spec:**
- Is there an explicit V1 / V2 / V3 split, or at least a V1 + "later" split?
- Is V1 small enough to ship in one heartbeat (typically 4-6 weeks)?
- Does V1 deliver the story's core promise without the polish?
- Are painted-door techniques (Wizard-of-Oz, hardcoded data, manual backend)
  explicit and accepted?
- Is "MVP" defined or just used as a buzzword?

**Score anchors:**

| Score | Description | Example signal |
|---|---|---|
| 10 | V1 is one sentence, one user-visible value, ships in <6 weeks. Manual/faked backend explicitly allowed (Wizard-of-Oz, hardcoded data). V2 and V3 are described separately with clear scope. | "V1 (Wk 1-3, painted door): A 3-question quiz appears at end of lesson. Backend hardcoded — we manually pick questions. Sarah sees one number: '22 out of 28'." |
| 8-9 | V1 is small and shippable, V2/V3 are mentioned but less detailed. Painted-door technique is implied. | "V1: quiz at end of lesson. V2: auto-generated questions. V3: per-student breakdown." |
| 7 | V1 exists and is roughly the right size, but V2/V3 are vague or the painted-door part is missing. | "V1 includes a quiz with manually written questions. Future versions will add automation." |
| 5-6 | V1 exists but is too big — "phase 1 includes A, B, C, D" where D is clearly V3 work. Sneaky scope creep. | "Phase 1: quizzes, auto-grading, per-student dashboard, teacher analytics." |
| 3-4 | "MVP" is mentioned but not defined. Or V1 is described abstractly. | "We'll start with an MVP and iterate." |
| 1-2 | "Out of scope" section exists (showing minimal scope-thinking) but no V1/V2/V3 generation split. Spec describes the finished product. | (spec lists features, has "Out of scope: per-component theming" but no V1) |
| 0 | No V1/V2/V3 split. Spec describes the cathedral. No mention of phasing, MVP, or shipping incrementally. | (spec describes the full product as one shipment) |

**Forcing question:**
*"What's the painted door? What can you fake on day one to test if anyone
walks through?"*

**Calibration note:** A spec with sophisticated phasing thinking (multiple
versions, painted door called out, scope explicitly cut) is rare. Most specs
score 0-4 on this pillar even when they're otherwise solid. Don't grade-inflate.

---

## Pillar 4 · HEARTBEATS

**Standard:** Heartbeats are not deadlines. Deadlines are things you miss.
Heartbeats are the rhythm of the team — every two weeks, every six weeks,
every quarter. Predictable, internal, and they make the team trust each
other. (Paraphrased from Build, "Heartbeats and Deadlines".)

**What to look for in the spec:**
- Is there a *cadence* (weekly, every-2-weeks, every-3-weeks)? Or just a
  launch date?
- Are there *internal* heartbeats (team sync, prototype review, eval gate,
  ship-to-friends, internal alpha) and *external* heartbeats (alpha, beta,
  GA)?
- Is there a "definition of done" for each heartbeat, or just dates?
- Does the team know what "this week's heartbeat" means after reading the spec?

**Score anchors:**

| Score | Description | Example signal |
|---|---|---|
| 10 | Explicit cadence (weekly internal, named milestones at week 1/3/6, definition of done for each). Mix of internal + external heartbeats. Reader knows what "this week" looks like. | "Wk 1: V1 painted door + 3 hand-curated questions for ONE teacher. Wk 2: 5 teachers, daily check-in. Wk 3: V1 ships to all 50 paid teachers. Wk 4-6: V2 auto-gen, weekly internal demo every Friday." |
| 8-9 | Cadence + named milestones, but missing definition-of-done per milestone or missing internal vs external split. | "Wk 1-3: V1. Wk 4-6: V2. Wk 7-9: V3." |
| 7 | Some milestones exist with rough timing, but no clear cadence or DOD. | "Phase 1 (3 weeks), Phase 2 (3 weeks), Phase 3 (TBD)." |
| 5-6 | Milestones exist but are randomly spaced or only described as "phase 1, phase 2" with no time estimate. | "First we'll do A. Then B. Then C." |
| 3-4 | One internal milestone + a launch date. Almost no cadence. | "We'll have a prototype in a few weeks, then ship in Q3." |
| 1-2 | Single launch date. "Ship by end of Q2." That's a deadline, not a heartbeat. | "Launch by end of Q3 2026." |
| 0 | "Ship when ready." Or no timing mentioned at all. The antithesis of a heartbeat. | "Ship when ready." (or: no timeline section at all) |

**Forcing question:**
*"What does week one look like? Week three? Week six? If you can't tell me,
you don't have a plan — you have a wish."*

**Watch for the deadline trap:** A long, single date ("ship by end of Q3")
sounds like planning but is actually the absence of planning. It tells the
team nothing about what happens this week.

---

## Pillar 5 · MAKE THE INVISIBLE VISIBLE

**Standard:** Nest's whole insight was that people don't think about energy.
So we showed them. The leaf icon, the monthly report, the savings number.
Suddenly the invisible became visible, and behavior changed. Every great
product takes something the user can't see and puts it in front of them.
(Paraphrased from Build, "Be Sticky" + Nest case studies.)

**What to look for in the spec:**
- What hidden state, hidden cost, hidden progress, or hidden benefit does
  the spec surface to the user?
- Is the *moment* of revelation named? (When does the user see this thing
  they couldn't see before?)
- Is the *visual treatment* described? (Leaf icon, score number, streak
  counter, badge, animation)
- Or is the product just a tool — inputs in, outputs out, no insight gained?

**Score anchors:**

| Score | Description | Example signal |
|---|---|---|
| 10 | Explicitly names the invisible thing (energy use, song count, comprehension rate, learning streak, brand-consistency score) AND describes the visual moment the user sees it. References the Nest leaf or iPod song count as the model. | "Sarah currently can't see lesson comprehension until grading time. The '22 out of 28' number makes the invisible visible in the last 90 seconds of every lesson — the moment she can still re-explain." |
| 8-9 | Names the invisible-made-visible thing and describes how it appears, but the moment is less precise. | "Teachers will see a comprehension score after every lesson, displayed as a percentage in the dashboard." |
| 7 | The product implies invisible-made-visible but doesn't name the visual moment. Reader has to infer. | "Teachers will get insight into how well students are understanding lessons." |
| 5-6 | Vague: "users will see their progress" or "the dashboard will show analytics". The principle is implicit but no specific invisible thing is named. | "Users can track their progress in the dashboard." |
| 3-4 | The product surfaces information, but it's information the user already had — just relocated. No new visibility. | "We'll show users their existing settings in a new sidebar." |
| 1-2 | Pure tool. Inputs in, outputs out. The user gets a result but learns nothing they couldn't already get elsewhere. | "Users upload a file, we process it, they get the result." |
| 0 | The spec doesn't surface anything to the user that wasn't already visible. There's no moment of revelation. | (spec describes a backend feature with no UI) |

**Forcing question:**
*"What does the user know after using this that they didn't know before?
Name the moment they see it."*

**Calibration note:** This pillar is the one most specs miss. Even strong
specs often score 5-7 here because the implementation is solid but the
*moment of revelation* isn't described. That's fine — the rewrite for this
pillar is to add one paragraph about the visual moment.

---

## Composite Score & Verdict Bands

`composite_score` = mean of the five pillar scores, rounded to 1 decimal.

| Composite | Verdict (use this verbatim in the sidecar review) |
|---|---|
| 8.0–10.0 | *"This is a product. Ship the V1. Don't admire it — ship it."* |
| 6.0–7.9  | *"You're close. Two pillars are weak. Fix them, then come back."* |
| 4.0–5.9  | *"This is a draft, not a spec. Rewrite, don't revise."* |
| 0.0–3.9  | *"Kill it or restart. This isn't a painkiller. It's not even a vitamin."* |

**Verdict variants** (pick one, all in Tony voice — vary across reviews so
the skill doesn't sound mechanical on repeat use):

8.0–10.0 alternates:
- *"This is a product. Ship the V1. Don't admire it — ship it."*
- *"You've got the bones. V1 in six weeks or less. Go."*
- *"This is what a real spec looks like. Build it."*

6.0–7.9 alternates:
- *"You're close. Two pillars are weak. Fix them, then come back."*
- *"Halfway home. Don't leave the other half on the table."*
- *"Almost. Rewrite the weak pillars, then we ship."*

4.0–5.9 alternates:
- *"This is a draft, not a spec. Rewrite, don't revise."*
- *"You're describing the cathedral, not the building site. Start over with V1."*
- *"There's a product in here. You haven't found it yet."*

0.0–3.9 alternates:
- *"Kill it or restart. This isn't a painkiller. It's not even a vitamin."*
- *"This is a feature waiting for a problem. Find the problem first."*
- *"I can't find the user in here. Without a user, there's no product."*

---

## How to apply this rubric

1. **Read the full spec first.** Don't score paragraph-by-paragraph.
2. **Score each pillar in isolation** before computing composite. Don't let
   a strong story-first carry a weak heartbeats score.
3. **Round generously to the nearest integer per pillar.** 6.5 → round to 7
   if the spec is closer to "working", 6 if closer to "needs work".
4. **Compute composite as mean rounded to 1 decimal.** Do not round the
   composite — it's informational, not categorical.
5. **Map composite to verdict band**, pick a verdict variant, write it
   verbatim in the sidecar.
6. **Default down when uncertain.** Tony's posture is strict.
