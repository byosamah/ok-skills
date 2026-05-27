# Platform Formats Reference

Complete platform specifications for social media post generation. Includes aspect ratios, recommended resolutions, and platform-specific considerations.

---

## Instagram

### Feed Post
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Square       | 1:1          | 1080 x 1080 px | Classic grid format. Most consistent look on profile grid. |
| Portrait     | 4:5          | 1080 x 1350 px | Takes up more screen real estate in feed. Best for engagement. |

**Tips:**
- 4:5 is the recommended default -- it occupies the maximum feed area without cropping.
- Grid preview always crops to 1:1 center square. Keep critical elements centered.
- Maximum file size: 30MB. JPEG or PNG.
- Alt text field supports up to 100 characters -- always fill it.

### Story / Reel
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Vertical     | 9:16         | 1080 x 1920 px | Full-screen vertical. Standard for stories and reels. |

**Tips:**
- Safe zone for text: keep within 1080 x 1420 px centered area (avoid top 250px and bottom 250px where UI overlays appear).
- Stories auto-advance after 15 seconds. Reels can be up to 90 seconds.
- Reel cover images are cropped to 1:1 on the profile grid -- center your key visual.
- Sticker zones: leave the bottom third open for polls, questions, and link stickers.

### Carousel
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Square       | 1:1          | 1080 x 1080 px | All slides must share the same aspect ratio. |
| Portrait     | 4:5          | 1080 x 1350 px | Can also use portrait for carousel slides. |

**Tips:**
- Up to 10 slides per carousel.
- First slide determines the aspect ratio for all subsequent slides.
- Edge-to-edge design with visual continuity between slides drives swipe-through.
- Last slide should always have a CTA ("Save this", "Follow for more", "Link in bio").

---

## LinkedIn

### Feed Post
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Square       | 1:1          | 1080 x 1080 px | Works well for infographics and quote cards. |
| Landscape    | 16:9         | 1200 x 675 px  | Standard link preview and shared image format. |

**Tips:**
- Square images get more engagement on LinkedIn than landscape.
- LinkedIn compresses images aggressively -- export at maximum quality.
- Professional tone expected. Bright neon colors and meme formats underperform.
- Document posts (PDF carousels) get 3x more reach than image posts.

### Article Header
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Landscape    | 16:9         | 1200 x 675 px  | Header image for LinkedIn articles.       |

**Tips:**
- Keep text minimal on article headers -- the article title displays below.
- Use brand colors and subtle imagery. Overly designed headers look like ads.

---

## Twitter / X

### Post Image
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Landscape    | 16:9         | 1200 x 675 px  | Standard in-feed image. Most common format. |
| Portrait     | 2:3          | 1080 x 1620 px | Takes more vertical space. Good for infographics. |

**Tips:**
- Images expand on click but preview is cropped. Critical content must be visible in the crop.
- 16:9 is the safest default -- previews without cropping on desktop and mobile.
- Maximum 4 images per tweet. Multi-image tweets use square crops for preview.
- GIFs autoplay in feed and drive significantly higher engagement than static images.
- Maximum file size: 5MB for images, 15MB for GIFs.

### Profile Header
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Ultra-wide   | 3:1          | 1500 x 500 px  | Banner image at top of profile.           |

**Tips:**
- Center-weighted design. Left side gets partially covered by avatar on mobile.
- Avoid text in the bottom-left quadrant -- profile photo overlaps there.
- Looks different on desktop vs mobile vs app. Test across devices.

---

## Facebook

### Feed Post
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Landscape    | 16:9         | 1200 x 675 px  | Standard shared image format.             |
| Square       | 1:1          | 1080 x 1080 px | Works well and takes up more feed space.  |

**Tips:**
- Facebook's algorithm favors native content over links. Upload images directly.
- Text overlay rule: posts with less than 20% text coverage get better distribution.
- Recommended image width: minimum 1200px for sharp rendering on retina displays.
- Maximum file size: 30MB.

### Cover Photo
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Landscape    | 16:9         | 1640 x 924 px  | Page cover photo. Displays differently on desktop vs mobile. |

**Tips:**
- Desktop displays full width. Mobile crops to center.
- Keep the most important content in a 640 x 360 px safe zone at center.
- Avoid text near edges -- cropping varies by device.
- Cover photos can be video (20-90 seconds, minimum 1080p).

---

## Pinterest

### Standard Pin
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Portrait     | 2:3          | 1000 x 1500 px | Optimal pin format. Dominates the feed.   |
| Tall         | 3:4          | 1000 x 1333 px | Slightly shorter alternative.             |

**Tips:**
- Vertical pins outperform square and landscape by a wide margin.
- Pinterest is a search engine. Include keyword-rich text overlays.
- Bright, warm-toned images get more saves than dark or cool images.
- Step-by-step, list-style, and infographic pins drive the highest engagement.
- Avoid faces as the primary element -- product/lifestyle imagery performs better on Pinterest.
- Maximum aspect ratio: 1:2.1 (taller gets truncated in feed).

---

## TikTok

### Video / Cover
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Vertical     | 9:16         | 1080 x 1920 px | Full-screen vertical. Only format.        |

**Tips:**
- TikTok is video-first. Static images get posted as photo carousels (up to 35 photos).
- Safe zone: avoid top 150px (username/music info) and bottom 270px (caption/buttons).
- Cover image is cropped to 1:1 on profile grid. Center the key visual.
- First frame matters -- it's the thumbnail. Design it intentionally.
- Letterboxed (horizontal video with black bars) content gets suppressed by the algorithm.

---

## YouTube

### Thumbnail
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Landscape    | 16:9         | 1280 x 720 px  | Video thumbnail. Minimum 1280px width.    |

**Tips:**
- Faces with exaggerated expressions + bold text = highest CTR formula.
- 3 elements maximum: face, text, one object. More than that is cluttered at small sizes.
- Test readability at 168 x 94 px -- that's the smallest it renders (mobile suggestions).
- Use contrasting colors that stand out against YouTube's white/dark background.
- Avoid red and white -- they blend with YouTube's UI elements.
- Maximum file size: 2MB. JPG, PNG, or GIF (non-animated).

---

## WhatsApp

### Status
| Format       | Aspect Ratio | Resolution     | Notes                                    |
|--------------|--------------|----------------|------------------------------------------|
| Vertical     | 9:16         | 1080 x 1920 px | Full-screen status image or video.        |

**Tips:**
- Status images display for 30 seconds by default (user-configurable).
- No clickable links. Use QR codes or "message us" CTAs instead.
- Status has limited reach -- only contacts who have your number saved see it.
- Keep designs simple. WhatsApp's audience expects personal, not polished.
- Overlaid text should be large (minimum 24pt equivalent) for readability on small screens.
- Video statuses: maximum 30 seconds, up to 16MB.

---

## Quick Reference Table

All formats at a glance:

| Platform     | Format         | Ratio  | Resolution       | Primary Use          |
|--------------|----------------|--------|------------------|----------------------|
| Instagram    | Feed (square)  | 1:1    | 1080 x 1080 px   | Grid-consistent post |
| Instagram    | Feed (portrait)| 4:5    | 1080 x 1350 px   | Maximum feed area    |
| Instagram    | Story / Reel   | 9:16   | 1080 x 1920 px   | Full-screen vertical |
| Instagram    | Carousel       | 1:1    | 1080 x 1080 px   | Multi-slide content  |
| LinkedIn     | Feed (square)  | 1:1    | 1080 x 1080 px   | Professional content |
| LinkedIn     | Feed (landscape)| 16:9  | 1200 x 675 px    | Link previews        |
| LinkedIn     | Article        | 16:9   | 1200 x 675 px    | Article header       |
| Twitter/X    | Post (landscape)| 16:9  | 1200 x 675 px    | Standard tweet image |
| Twitter/X    | Post (portrait)| 2:3    | 1080 x 1620 px   | Infographics         |
| Twitter/X    | Header         | 3:1    | 1500 x 500 px    | Profile banner       |
| Facebook     | Post (landscape)| 16:9  | 1200 x 675 px    | Shared image         |
| Facebook     | Post (square)  | 1:1    | 1080 x 1080 px   | Feed engagement      |
| Facebook     | Cover          | 16:9   | 1640 x 924 px    | Page cover           |
| Pinterest    | Pin (standard) | 2:3    | 1000 x 1500 px   | Standard pin         |
| Pinterest    | Pin (tall)     | 3:4    | 1000 x 1333 px   | Alternative pin      |
| TikTok       | Video / Cover  | 9:16   | 1080 x 1920 px   | Full-screen vertical |
| YouTube      | Thumbnail      | 16:9   | 1280 x 720 px    | Video thumbnail      |
| WhatsApp     | Status         | 9:16   | 1080 x 1920 px   | Status update        |

---

## Cross-Platform Defaults

When the user doesn't specify a platform, use these defaults:

| Scenario                           | Default Format         | Reasoning                              |
|------------------------------------|------------------------|----------------------------------------|
| "Make me a post"                   | 1:1 at 1080 x 1080 px | Universal. Works everywhere.           |
| "Make me a story"                  | 9:16 at 1080 x 1920 px | Standard vertical format.             |
| "Make me a banner"                 | 16:9 at 1200 x 675 px | Works on most platforms.               |
| "Make me a pin"                    | 2:3 at 1000 x 1500 px | Pinterest standard.                    |
| "Make me a thumbnail"             | 16:9 at 1280 x 720 px | YouTube standard.                      |

---

## File Format Guidelines

| Format | Best For                     | Max Size        | Notes                           |
|--------|------------------------------|------------------|---------------------------------|
| PNG    | Graphics, text-heavy, logos  | 30MB (varies)    | Lossless. Larger files. Best quality. |
| JPEG   | Photography, gradients       | 30MB (varies)    | Lossy. Smaller files. Export at 90%+ quality. |
| WebP   | Web use only                 | Varies           | Not supported on all platforms for upload. |
| GIF    | Simple animations            | 15MB (Twitter)   | Limited colors. Use for short loops. |

**Recommendation:** Export as PNG for graphics with text, JPEG at 95% quality for photographic content.
