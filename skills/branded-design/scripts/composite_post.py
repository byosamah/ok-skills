#!/usr/bin/env python3
"""
MeemAin Post Compositing Pipeline v2
Composites real brand assets (logo, text, elements) onto an AI-generated base image.

Proportions calibrated from 27 real MeemAin posts:
- Logo: ~30% canvas width, 2% from top
- Text: starts ~15% from top, each line ~9% of canvas
- Elements: 25-35% of canvas, BLEED 40-60% past canvas edge
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False
    print("WARNING: arabic-reshaper or python-bidi not installed.")


SKILL_DIR = Path(__file__).resolve().parent.parent
BRAND_KIT = SKILL_DIR / "brand-kit"
FONTS_DIR = BRAND_KIT / "fonts"

FONT_BOLD = FONTS_DIR / "IBMPlexSansArabic-Bold.ttf"
FONT_SEMIBOLD = FONTS_DIR / "IBMPlexSansArabic-SemiBold.ttf"
FONT_REGULAR = FONTS_DIR / "IBMPlexSansArabic-Regular.ttf"


def parse_color(color_str):
    color_str = color_str.strip().lstrip("#")
    if len(color_str) == 6:
        return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))
    elif len(color_str) == 8:
        return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4, 6))
    raise ValueError(f"Invalid color: #{color_str}")


def reshape_arabic(text):
    if not HAS_BIDI:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def load_font(weight="bold", size=80):
    font_map = {"bold": FONT_BOLD, "semibold": FONT_SEMIBOLD, "regular": FONT_REGULAR}
    font_path = font_map.get(weight, FONT_BOLD)
    if not font_path.exists():
        print(f"WARNING: Font not found at {font_path}, using default")
        return ImageFont.load_default()
    return ImageFont.truetype(str(font_path), size)


def place_logo(canvas, logo_path, position="top-center", scale_pct=0.30):
    """
    Place logo. Calibrated from real posts:
    - Logo width = ~30% of canvas
    - Top margin = ~2% of canvas height
    """
    logo = Image.open(logo_path).convert("RGBA")

    target_width = int(canvas.width * scale_pct)
    ratio = target_width / logo.width
    new_size = (target_width, int(logo.height * ratio))
    logo = logo.resize(new_size, Image.LANCZOS)

    lw, lh = logo.size
    top_margin = int(canvas.height * 0.02)
    side_margin = int(canvas.width * 0.04)

    positions = {
        "top-center": ((canvas.width - lw) // 2, top_margin),
        "top-left": (side_margin, top_margin),
        "top-right": (canvas.width - lw - side_margin, top_margin),
        "bottom-center": ((canvas.width - lw) // 2, canvas.height - lh - top_margin),
    }
    pos = positions.get(position, positions["top-center"])
    canvas.paste(logo, pos, logo)
    return pos[1] + lh  # Return Y bottom of logo


def render_text_block(canvas, text, y_start, text_color=(255, 255, 255),
                      accent_text=None, accent_color=(255, 74, 89),
                      font_size=None, align="center", margin_pct=0.06):
    """
    Render Arabic text. Calibrated from real posts:
    - Font size auto-calculated to fill ~9% of canvas height per line
    - Line spacing = 15% of line height
    """
    draw = ImageDraw.Draw(canvas)
    margin = int(canvas.width * margin_pct)

    # Auto-calculate font size if not provided: each line ~9% of canvas height
    if font_size is None:
        font_size = int(canvas.height * 0.09)

    font = load_font("bold", font_size)
    lines = text.split("\n") if "\n" in text else [text]
    y = y_start

    for line in lines:
        display_line = reshape_arabic(line)
        bbox = draw.textbbox((0, 0), display_line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        if align == "center":
            x = (canvas.width - tw) // 2
        elif align == "right":
            x = canvas.width - tw - margin
        else:
            x = margin

        # Check if this line contains accent text
        if accent_text and accent_text in line:
            # First render entire line in default color
            draw.text((x, y), display_line, fill=text_color, font=font)

            # Then overlay accent portion
            # For RTL: accent text at end of source = LEFT side of display
            accent_display = reshape_arabic(accent_text)
            accent_bbox = draw.textbbox((0, 0), accent_display, font=font)
            accent_w = accent_bbox[2] - accent_bbox[0]

            # Calculate where accent sits in the rendered line
            # In bidi display, the last word of RTL text appears on the LEFT
            rest_text = line.replace(accent_text, "").strip()
            if rest_text:
                rest_display = reshape_arabic(rest_text)
                rest_bbox = draw.textbbox((0, 0), rest_display, font=font)
                rest_w = rest_bbox[2] - rest_bbox[0]
                # Accent is on the LEFT of the displayed line (RTL end = visual left)
                accent_x = x
            else:
                accent_x = x

            draw.text((accent_x, y), accent_display, fill=accent_color, font=font)
        else:
            draw.text((x, y), display_line, fill=text_color, font=font)

        line_spacing = int(th * 0.15)
        y += th + line_spacing

    return y


def place_element(canvas, element_path, position="bottom-left", scale_pct=0.30, bleed_pct=0.50):
    """
    Place decorative element with edge bleeding.
    Calibrated from real posts:
    - Element size: 25-35% of canvas width
    - Bleed: 40-60% of element extends BEYOND canvas edge
    - Creates the "peeking in from the edge" effect
    """
    elem = Image.open(element_path).convert("RGBA")

    # Scale element to percentage of canvas
    new_w = int(canvas.width * scale_pct)
    ratio = new_w / elem.width
    new_h = int(elem.height * ratio)
    elem = elem.resize((new_w, new_h), Image.LANCZOS)

    ew, eh = elem.size
    bleed_x = int(ew * bleed_pct)
    bleed_y = int(eh * bleed_pct)

    # Positions: negative values = bleeding past the edge
    positions = {
        "top-left": (-bleed_x, -bleed_y),
        "top-right": (canvas.width - ew + bleed_x, -bleed_y),
        "bottom-left": (-bleed_x, canvas.height - eh + bleed_y),
        "bottom-right": (canvas.width - ew + bleed_x, canvas.height - eh + bleed_y),
        "mid-left": (-bleed_x, (canvas.height - eh) // 2),
        "mid-right": (canvas.width - ew + bleed_x, (canvas.height - eh) // 2),
    }
    pos = positions.get(position, positions["bottom-left"])

    # Create a temporary layer for the element (handles negative coords)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(elem, pos, elem)
    canvas.alpha_composite(layer)


def generate_solid_base(width=2048, height=2048, color="#c1e153"):
    rgb = parse_color(color)
    return Image.new("RGBA", (width, height), rgb + (255,))


def composite_post(args):
    """Main compositing pipeline with layered z-ordering."""
    # Load or create base
    if args.base:
        canvas = Image.open(args.base).convert("RGBA")
        print(f"Base loaded: {args.base} ({canvas.size[0]}x{canvas.size[1]})")
    else:
        canvas = generate_solid_base(args.width, args.height, args.bg_color)
        print(f"Solid base: {args.bg_color} ({args.width}x{args.height})")

    # Layer 1: Elements BEHIND person (if base has person, elements go first)
    if args.elements:
        for elem_spec in args.elements:
            parts = elem_spec.split(":")
            elem_path = parts[0]
            elem_pos = parts[1] if len(parts) > 1 else "bottom-left"
            elem_scale = float(parts[2]) if len(parts) > 2 else 0.30
            elem_bleed = float(parts[3]) if len(parts) > 3 else 0.50
            place_element(canvas, elem_path, position=elem_pos,
                         scale_pct=elem_scale, bleed_pct=elem_bleed)
            print(f"Element: {Path(elem_path).name} → {elem_pos} (scale={elem_scale}, bleed={elem_bleed})")

    # Layer 2: Logo
    logo_bottom_y = int(canvas.height * 0.10)
    if args.logo:
        logo_bottom_y = place_logo(
            canvas, args.logo,
            position=args.logo_position,
            scale_pct=args.logo_scale or 0.30
        )
        print(f"Logo: {args.logo_position} (scale={args.logo_scale or 0.30})")

    # Layer 3: Text (on top of everything)
    if args.text:
        text_color = parse_color(args.text_color)
        accent_color = parse_color(args.accent_color) if args.accent_color else (255, 74, 89)

        # Default: text starts 15% from top
        text_y = args.text_y if args.text_y else int(canvas.height * 0.15)

        render_text_block(
            canvas, args.text,
            y_start=text_y,
            text_color=text_color,
            accent_text=args.accent_text,
            accent_color=accent_color,
            font_size=args.font_size,
            align=args.text_align,
        )
        print(f"Text: '{args.text[:40]}' (size={args.font_size or 'auto'})")

    # Save
    output_path = args.output
    canvas = canvas.convert("RGB")
    canvas.save(output_path, quality=95)
    print(f"\nSaved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="MeemAin Post Compositing Pipeline v2")

    parser.add_argument("--base", "-b", help="Base image path")
    parser.add_argument("--bg-color", default="#c1e153", help="Solid bg color (no base)")
    parser.add_argument("--width", "-W", type=int, default=2048)
    parser.add_argument("--height", "-H", type=int, default=2048)

    parser.add_argument("--logo", "-l", help="Logo image path")
    parser.add_argument("--logo-position", default="top-center",
                        choices=["top-center", "top-left", "top-right",
                                 "bottom-center", "bottom-left", "bottom-right"])
    parser.add_argument("--logo-scale", type=float, default=None,
                        help="Logo width as fraction of canvas (default: 0.30)")

    parser.add_argument("--text", "-t", help="Main Arabic text (use \\n for newlines)")
    parser.add_argument("--text-color", default="#ffffff")
    parser.add_argument("--accent-text", help="Text portion to highlight")
    parser.add_argument("--accent-color", default="#ff4a59")
    parser.add_argument("--font-size", type=int, default=None,
                        help="Font size in px (default: auto ~9%% of canvas)")
    parser.add_argument("--text-align", default="center", choices=["center", "right", "left"])
    parser.add_argument("--text-y", type=int, default=None,
                        help="Y position for text (default: 15%% from top)")

    parser.add_argument("--elements", "-e", action="append",
                        help="'path:position[:scale[:bleed]]' — scale/bleed are 0-1 fractions")

    parser.add_argument("--output", "-o", default="output.png")

    args = parser.parse_args()
    composite_post(args)


if __name__ == "__main__":
    main()
