---
name: branded-design
description: Generate on-brand social media posts using a compositing pipeline — AI generates the visual, then real brand assets (logo PNGs, font TTFs, decorative elements) are layered on top using Pillow. Adapts to any brand archetype (photo-based, product, illustration, text-only, minimalist). The skill folder IS the brand template — brand assets live inside brand-kit/ and every generation uses pixel-perfect real assets, never AI-approximated ones. Use this skill whenever the user asks to create a social media post, brand post, branded design, Instagram post, LinkedIn visual, story design, promotional graphic, or any social media visual content. Also triggers when the user mentions creating branded content, designing posts, or generating marketing visuals. Supports self-improving learning from feedback.
---

# Branded Design

Generate on-brand social media posts using a **two-step compositing pipeline**:

1. **Nano Banana 2** generates the base visual (photo, illustration, or scene — without any brand assets baked in)
2. **Compositing pipeline** layers real brand assets on top: actual logo PNGs, actual font TTF rendering, actual decorative element PNGs

This approach exists because AI image generators re-draw everything from scratch — they approximate logos, invent fonts, and generate decorative elements that look close but aren't the real brand assets. Production brands need pixel-perfect fidelity, which only comes from compositing the actual files.

**The skill folder IS the brand.** The `brand-kit/` directory contains all brand assets. Copy this skill, fill in your brand-kit/, and you have a custom social media post generator.

---

## Brand Archetypes

Not every brand works the same way. During setup, the skill identifies which archetype fits and adapts the pipeline accordingly.

| Archetype | Background | Subject | Elements | Example Brands |
|-----------|-----------|---------|----------|----------------|
| **photo-person** | Solid color | People/portraits | Decorative shapes, bleeding edges | MeemAin, Nike, education brands |
| **photo-product** | Solid/gradient | Product photography | Minimal or none | Apple, food brands, e-commerce |
| **illustration** | Solid/textured | AI-generated illustration | May or may not have | Notion, Slack, tech blogs |
| **text-card** | Solid/gradient | None — text is the hero | Decorative or none | Quote cards, tips, stats |
| **editorial** | Full-bleed photo | Photo IS the background | Text overlay only | Fashion, travel, lifestyle |
| **minimal** | White/neutral | Clean product or icon | None | SaaS, fintech, enterprise |

Each archetype changes how the compositing pipeline works:

- **photo-person**: Full pipeline with rembg (person extracted, elements behind, z-ordering)
- **photo-product**: Simpler pipeline (product on bg, logo + text on top, no rembg needed)
- **illustration**: AI generates the illustration, logo + text composited on top
- **text-card**: No AI photo generation — just Pillow renders bg + text + logo + elements
- **editorial**: AI generates the full scene, logo + text overlaid with contrast treatment
- **minimal**: Clean layout, logo + text + maybe one accent element

---

## Step 0: First-Run Detection

**Check `brand-kit/brand.yaml`:**
- **Does NOT exist** → Run **Setup Mode** below.
- **Exists but invalid** → Run `scripts/validate_brand_kit.py brand-kit/` and show errors.
- **Exists and valid** → Skip to **Generation Workflow**.

---

## Setup Mode (First Run)

### Step S1: Install Core Dependencies

```bash
pip3 install Pillow
```

Additional dependencies are installed only if needed (determined during the interview):
- **Arabic/RTL text**: `pip3 install arabic-reshaper python-bidi`
- **Person-behind-elements z-ordering**: `pip3 install rembg`

### Step S2: Interview Questions

Ask these one by one (not all at once):

1. **"What's your brand name?"**

2. **"Show me 3-5 example posts from your brand."** This is the most important input — offer to read them from a folder, a URL, or have the user drop them into `brand-kit/examples/`. If the user has existing content (strategy doc, website, Canva exports), offer to analyze those too.

3. **"What archetype best describes your posts?"** Based on the examples, suggest the closest archetype. If uncertain, ask:
   > "Looking at your posts, they seem to be [archetype]. Does that feel right, or is it something else?"
   The user doesn't need to know the technical term — describe what each one looks like.

4. **"What are your brand colors?"** Ask for hex codes. Capture ALL colors, not just the standard 5:
   - Primary, secondary, accent, background, text
   - Any extra colors (most brands have 6-8). Store extras in `colors.extra`.

5. **"What font does your brand use?"**
   - Get the exact font name
   - Ask if it's the same for headings and body
   - Determine the script: Latin, Arabic, Hebrew, CJK, etc.

6. **"Describe your brand's tone and personality"** — or extract it from existing content if provided.

7. **"What visual style keywords describe your brand?"**

8. **Archetype-specific questions:**

   **For photo-person:**
   - "Are there cultural rules for how people should look?" (clothing, hijab, age, ethnicity)
   - "Do you use decorative elements? If so, where do they go?"
   - "Do elements go behind or in front of people?"
   
   **For photo-product:**
   - "Flat lay, studio, or lifestyle photography?"
   - "White background or branded color?"
   
   **For editorial:**
   - "How do you handle text on photos? Dark overlay? Bottom bar? Gradient fade?"
   
   **For text-card:**
   - "What's the typical layout? Centered? Left-aligned? Multi-section?"

9. **Logo placement** — Ask for default position and any rules for when it moves.

10. **Brand pillars/products** — Ask if there are distinct content categories that use different color coding.

### Step S3: Create Brand Config

Create `brand-kit/brand.yaml` with all collected data:

```yaml
name: "Brand Name"
tagline: "Tagline"
tone: "descriptive words"

archetype: "photo-person"  # or photo-product, illustration, text-card, editorial, minimal

colors:
  primary: "#hex"
  secondary: "#hex"
  accent: "#hex"
  background: "#hex"
  text: "#hex"
  extra: {}  # additional brand colors

fonts:
  heading: "Font Name"
  body: "Font Name"
  script: "latin"  # or "arabic", "hebrew", "cjk"

font_strategy: "exact"
logo_placement: "top-center"
logo_placement_rules: {}  # contextual rules

style_keywords: []
pillars: {}
cultural_rules: []

# Archetype-specific config
compositing:
  use_rembg: true           # only for photo-person with elements behind
  element_bleeding: true     # elements overflow canvas edge
  element_z_behind: true     # elements go behind subject
  text_contrast: "none"      # "none", "shadow", "overlay", "bar" (for editorial)
```

### Step S4: Font Setup

1. Check if font is on the system: `fc-list | grep -i "font-name"`
2. If found, copy Bold + Regular TTFs to `brand-kit/fonts/`
3. If not found and it's a Google Font, attempt to download
4. If the font uses Arabic/RTL script, install: `pip3 install arabic-reshaper python-bidi`

### Step S5: Install Archetype-Specific Dependencies

Based on the archetype and config:
- If `compositing.use_rembg: true` → `pip3 install rembg`
- If `fonts.script: "arabic"` → `pip3 install arabic-reshaper python-bidi`

Only install what the brand actually needs.

### Step S6: Guide Asset Placement

Tell the user what's needed based on their archetype:

**All archetypes need:**
- Logo files in `brand-kit/logo/`
- Font TTFs in `brand-kit/fonts/`
- At least 3 example posts in `brand-kit/examples/`

**photo-person and photo-product also need:**
- Reference photos in `brand-kit/photography/`

**Brands with decorative elements also need:**
- Element PNGs in `brand-kit/elements/` (the actual graphic files, not AI approximations)

### Step S7: Calibrate from Examples

After assets are added, measure proportions from example posts using Pillow:
- Logo width as % of canvas
- Logo margin from top
- Text size as % of canvas height per line
- Element scale and bleed amounts (if applicable)
- Text start position

Save to `brand-kit/calibration.yaml`. These calibrated values ensure every generated post matches the brand's existing proportions.

### Step S8: Validate and Rename

Run `scripts/validate_brand_kit.py brand-kit/` to confirm readiness.

Ask: **"Want to rename this skill to `{brand-name}-brain`?"** → `scripts/setup_brand.py --rename-skill`

---

## Generation Workflow

### Step 1: Collect Input

Ask the user for:
1. **Content text** — The text that appears ON the design
2. **Creative direction** — Post type, mood, context
3. **Platform & format** — See [references/platform-formats.md](references/platform-formats.md)

### Step 2: Read Brand Config

Read `brand-kit/brand.yaml`, `brand-kit/calibration.yaml`, and `brand-kit/learnings.yaml`.

Key decision: which **archetype pipeline** to run (from `brand.yaml` `archetype` field).

### Step 3: Generate Base Visual (Nano Banana)

What Nano Banana generates depends on the archetype:

**photo-person:**
```
{person_description}. {cultural_rules}.
Solid {background_color} background everywhere.
NO floor, NO ground, NO surface.
Person in lower 60% of frame, top 40% empty for text.
NO text, NO logos, NO decorative elements, NO watermarks.
```

**photo-product:**
```
{product_description} on {background_style}.
Clean studio lighting, {style_keywords}.
NO text, NO logos, NO watermarks.
Product centered, space around edges for text overlay.
```

**illustration:**
```
{illustration_description} in {style_keywords} style.
{background_color} background.
NO text, NO logos.
Leave space in {text_area} for text overlay.
```

**text-card:**
Skip Nano Banana entirely. The compositing pipeline creates everything from scratch using Pillow (solid/gradient background + text + logo + elements).

**editorial:**
```
{full_scene_description}.
Cinematic, {style_keywords}.
NO text, NO logos, NO watermarks.
{composition_guidance for text placement area}
```

**minimal:**
```
{subject_description} on {clean_background}.
Minimal, clean, {style_keywords}.
NO text, NO logos.
Generous whitespace for text.
```

Always pass 1-2 example posts as reference images with `-i` to guide visual style.

### Step 4: Composite Real Brand Assets

The compositing steps depend on the archetype:

---

#### Pipeline: photo-person (full z-ordering)

This is the most complex pipeline — elements go BEHIND the person.

```
Layer 1: Solid color background
Layer 2: Decorative elements (bleeding past edges)
Layer 3: Person (background removed via rembg)
Layer 4: Logo (real PNG)
Layer 5: Text (real font TTF via Pillow)
```

**Element bleeding:** Elements should NOT float fully visible inside the canvas. Position them so 30-55% extends beyond the canvas edge, creating a "peeking in" effect. Use negative coordinates.

**rembg extraction:** Remove the background from the AI photo to get just the person, then layer them on top of the elements.

---

#### Pipeline: photo-product (simpler)

```
Layer 1: Solid/gradient background
Layer 2: Product photo (may or may not need bg removal)
Layer 3: Decorative elements (if any, ON TOP)
Layer 4: Logo
Layer 5: Text
```

No rembg needed unless the product needs a transparent cutout.

---

#### Pipeline: illustration

```
Layer 1: AI-generated illustration (full canvas)
Layer 2: Logo
Layer 3: Text
```

The illustration IS the visual — just overlay logo and text.

---

#### Pipeline: text-card (no AI needed)

```
Layer 1: Solid/gradient background (Pillow-generated)
Layer 2: Decorative elements (if any)
Layer 3: Text blocks (headline, body, hashtags)
Layer 4: Logo
```

Everything is rendered by Pillow. No Nano Banana call needed.

---

#### Pipeline: editorial

```
Layer 1: Full-bleed AI photo
Layer 2: Contrast treatment (dark overlay, gradient fade, or bottom bar)
Layer 3: Text (white or light color)
Layer 4: Logo
```

The contrast treatment ensures text is readable over the photo.

---

#### Pipeline: minimal

```
Layer 1: Clean background
Layer 2: Subject/icon (small, centered or off-center)
Layer 3: Logo (subtle, small)
Layer 4: Text
```

---

### Compositing Constants

Use calibrated values from `brand-kit/calibration.yaml`. If not available, use these defaults:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `logo_width_pct` | 0.22 | Logo width as fraction of canvas |
| `logo_top_margin_pct` | 0.017 | Logo distance from top edge |
| `text_line_height_pct` | 0.09 | Each text line's height as fraction of canvas |
| `text_start_pct` | 0.15 | Text Y start position from top |
| `element_scale_pct` | 0.30 | Element size as fraction of canvas |
| `element_bleed_pct` | 0.50 | How much element overflows past edge |

### Text Rendering

For all archetypes, text is rendered with the real brand font:

```python
from PIL import ImageFont, ImageDraw
font = ImageFont.truetype("brand-kit/fonts/Font-Bold.ttf", size)
```

**For Arabic/RTL scripts**, reshape and reorder before rendering:
```python
import arabic_reshaper
from bidi.algorithm import get_display
display_text = get_display(arabic_reshaper.reshape(text))
```

**For Latin scripts**, render directly — no reshaping needed.

### Step 5: Show Result & Iterate

Present three options:

- **Accept** → Log and learn (Step 6)
- **Tweak** → For compositing changes (logo, text, elements), re-run only the compositing step. For photo changes, regenerate base + re-composite.
- **Redo** → Re-run from Step 3

### Step 6: Log & Learn

```bash
python scripts/log_and_learn.py \
  --brand-kit brand-kit \
  --content "{content}" \
  --direction "{direction}" \
  --platform "{platform}" \
  --aspect-ratio "{ratio}" \
  --references "{refs}" \
  --prompt-used "{prompt}" \
  --iterations '{iterations_json}' \
  --output-path "{output}"
```

The learnings system captures:
- What archetype pipeline was used
- Calibration adjustments from iterations
- Element positions and bleed values that worked
- Cultural/visual rules discovered

---

## Deep Review Mode

When the user asks to review learnings:
1. Analyze feedback logs for patterns
2. Update `calibration.yaml` with refined proportions
3. Update `learnings.yaml` with new rules
4. Suggest archetype adjustments if the brand has evolved

## Brand Kit Validation

```bash
python scripts/validate_brand_kit.py brand-kit/
```

Checks:
- `brand.yaml` exists with required fields (including `archetype`)
- Logo files exist
- Font TTFs exist (required for exact rendering)
- Example posts exist (minimum 1, recommend 3+)
- Archetype-specific assets (elements for photo-person, etc.)

## File Reference

- [references/brand-yaml-schema.md](references/brand-yaml-schema.md) — Full brand.yaml spec
- [references/prompt-patterns.md](references/prompt-patterns.md) — Base visual prompts per archetype
- [references/platform-formats.md](references/platform-formats.md) — Platform specs
