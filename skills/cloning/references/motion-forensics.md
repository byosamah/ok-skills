# Motion Forensics

How to recover a site's real motion instead of inferring it from a video, and
how to verify motion without producing false failures.

## Contents

- [Why this exists](#why-this-exists)
- [The recovery ladder](#the-recovery-ladder)
- [What survives minification](#what-survives-minification)
- [Reading the report](#reading-the-report)
- [Verifying motion](#verifying-motion)
- [The noise floor](#the-noise-floor)
- [Worked example](#worked-example)

## Why this exists

Video inference is the weakest way to reproduce motion, because a recording only
shows you the result. It cannot tell you the easing function, the stagger
interval, the scrub value, or whether a carousel uses a spring or a tween. You
end up approximating a curve you could have simply installed.

Almost every site hands you better evidence than the video, if you look. The
order below is worth following strictly, because each rung is dramatically more
reliable than the one under it.

## The recovery ladder

**Rung 1 - source maps.** If the site publishes them, you get the original
unminified source, with real variable names, real file names and often comments.
This is the whole answer when it is available. Check for `//# sourceMappingURL=`
at the end of each bundle.

**Rung 2 - library identity plus exact version.** This is the rung that matters
most in practice, because rung 1 is usually absent and rung 3 is usually
unpleasant. If the original animates with `gsap@3.15.0`, then installing
`gsap@3.15.0` reproduces its easing curves exactly, for free. If its carousel is
`smooothy`, installing `smooothy` gives you the real physics rather than your
best guess at momentum and snapping. Reimplementing a physics library by eye is
the single largest source of motion drift in a clone.

**Rung 3 - beautified bundles.** Minified code with mangled names is not worth
transcribing line by line, but running it through a formatter makes the control
flow followable. Reading the actual order of calls still beats guessing that
order from a recording.

**Rung 4 - video inference.** Legitimate only for motion that none of the above
explains: bespoke choreography written directly in the site's own code, with no
map and no recognisable library.

`scripts/recover_motion_source.py` walks all four rungs and tells you which one
you landed on.

## What survives minification

The reason rung 2 works is that a minifier is not free to remove everything. It
must preserve anything the running program compares against a string or reads
from the DOM. That leaves fingerprints:

| Trace | Example | Why it survives |
|---|---|---|
| Runtime warning strings | `Missing plugin? gsap.registerPlugin()` | Printed to the console at runtime |
| Public API names | `ScrollTrigger`, `scrollerProxy`, `toggleActions` | Part of the external contract |
| DOM attribute hooks | `[data-smooothy]`, `[data-barba]`, `[data-scroll]` | Matched against real markup |
| Embedded version literals | `.version="3.15.0"` | A string, not an identifier |
| CSS class conventions | `swiper-slide`, `embla__container` | Matched against real markup |

What does **not** survive, and therefore must never be your detection strategy:
bare import specifiers. When a bundler inlines a library, the string `"gsap"`
disappears entirely. A scan that looks for quoted module names reports nothing on
exactly the sites you most want to analyse.

Version literals deserve special attention. `.version="3.15.0"` gives you an
exact install target. Confirm it resolves with `npm view gsap@3.15.0 version`
before pinning, since a bundle can contain more than one version string.

## Reading the report

`motion-source/motion-source-report.json` has a `strategy` field naming the rung
you reached:

- `source-maps` - read `motion-source/sources/` and transcribe the real logic.
- `install-and-read` - run the install commands, then read
  `motion-source/pretty/` for the choreography the libraries do not supply.
- `infer-from-video` - nothing recoverable; the videos are now justified.

The `libraries` array carries a `confidence` field. `high` means at least two
independent fingerprints matched, which is strong evidence. `low` means a single
generic word matched and should be treated as a lead, not a fact.

Install every `high` confidence package before writing any animation code. It is
much easier to delete a library you turned out not to need than to discover
halfway through the refinement loop that your hand-rolled easing will never
converge on the original.

## Verifying motion

Two mistakes make motion verification untrustworthy. Both are easy to make and
both produce confident, wrong answers.

**Never compare at the same clock time.** Screenshotting both sites "three
seconds after load" compares two different moments in the animation. Intro
timelines usually start on an event rather than on page load, and
`document.fonts.ready` is the common one. Fonts resolve far sooner from
localhost than over a network, so the clone is routinely further through its
timeline than the original at any fixed moment. A correct clone looks broken.

Compare at the same **phase** instead. Wait until the page stops changing, then
measure. `scripts/compare_motion.py` polls element geometry until it holds still
across six consecutive samples, which puts both sides at the same point in the
timeline regardless of how long each took to get there.

Watch the reported settle times. Seeing the clone settle at 8785ms while the
original settles at 6200ms is normal and is precisely why fixed waits fail.

**Never treat every difference as a defect.** See below.

## The noise floor

Physics-driven motion does not settle to the same sub-pixel position twice.
Inertial carousels, smooth scroll and spring animations all land slightly
differently on each load. Diffing a clone against an original therefore always
produces differences, and a refinement loop that treats them as defects will
chase them forever without converging.

The fix is to measure the clone against **itself** across two loads before
comparing it to anything. That disagreement is your noise floor. Differences at
or below it carry no information about the original.

This is not a theoretical concern. On one real clone, a character-level DOM
comparison showed 19 of 263 elements differing from the original, which looked
like a genuine defect list. The same clone compared against itself differed by
24 of 263 elements. The apparent defects were smaller than the measurement's own
variance, and every one of them was noise.

The noise floor also solves a problem the refinement loop otherwise has no answer
to: when to stop. "Up to three passes" is arbitrary. "Keep fixing until the
remaining differences are inside the clone's own run-to-run variance" is a real
stop condition, because it is the point past which the measurement can no longer
distinguish better from worse.

If the noise floor comes back at zero, the settle logic is doing its job and the
comparison is deterministic. That is a good result, not a broken one, but confirm
the probe actually captured elements before believing it.

## Worked example

A portfolio site built with Astro, animated with GSAP, scrolled with Lenis, with
a drag carousel.

```bash
# Rung 1 and 2: what can be recovered?
python scripts/recover_motion_source.py https://example.com /tmp/clone-artifacts \
    --routes "/,/about,/lab"
```

Output:

```
STRATEGY: install-and-read
  Install these instead of reimplementing their behaviour:
    npm i gsap@3.15.0 (exact version confirmed on npm)
        - gsap: timeline engine; easing curves and durations come from here
        - gsap/ScrollTrigger: scroll-driven timelines; ships inside the gsap package
        - gsap/Observer: unified wheel/touch/pointer input; ships inside gsap
    npm i lenis
        - lenis: smooth scroll with inertia; shifts every scroll-linked value
    npm i smooothy
        - smooothy: physics-based drag carousel (three o's); do not reimplement
```

`smooothy` is the finding that matters. It was detected only through the
`[data-smooothy]` attribute in the markup, since the bundle inlines the library
and never names it. Without that detection the carousel gets reimplemented by
eye, and its momentum and snapping never quite match.

Then verify, after building:

```bash
python scripts/compare_motion.py --original https://example.com \
    --clone http://localhost:4321 --routes "/,/about"
python scripts/verify_head.py --original https://example.com \
    --clone http://localhost:4321 --routes "/,/about,/lab"
```

The head check is separate because nothing else can see it. Titles, descriptions
and social tags are invisible to pixel comparison, SSIM and DOM geometry alike. A
clone can match the original exactly on screen while shipping a title the
generator invented, which is a defect that reaches delivery with every visual
check passing.
