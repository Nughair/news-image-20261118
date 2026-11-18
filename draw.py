#!/usr/bin/env python3
"""Draw entry.png: the world news of Wednesday 18 November 2026 in one image.

This script runs on the builder's machine only (the grader never runs
it; main.py ships the finished PNG). It composes a newspaper-style
front page with Pillow: a masthead that names the day, one lead panel,
four story panels and a ticker strip. Every story was reported on
18 November 2026; STORIES.md lists them with their sources.

Design constraints, from the competition's judge criteria: the date
must be unmissable, each story recognisable from its picture plus a
short label, the selection broad across regions and fields, and the
text legible when the image is shrunk. So: flat pictogram icons, bold
short headlines, one-line captions, no photographs, no generated
imagery — and a strict vertical budget inside every panel, enforced
by fit_text below, so nothing can ever spill out of its card.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (246, 241, 231)
INK = (23, 32, 42)
MUTED = (90, 96, 104)
CARD = (255, 253, 247)
BORDER = (210, 202, 182)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = f"{FONT_DIR}/DejaVuSans-Bold.ttf"
REG = f"{FONT_DIR}/DejaVuSans.ttf"

_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        trial = f"{cur} {w_}".strip()
        if text_w(d, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_width(d, s, path, start_size, max_w, min_size=14):
    """Largest font size at which the single line fits max_w."""
    size = start_size
    while size > min_size and text_w(d, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def fit_lines(d, s, max_w, start_size, max_lines, min_size=16):
    """Shrink a bold font until the wrapped text fits max_lines."""
    size = start_size
    while size > min_size:
        f = font(BOLD, size)
        lines = wrap(d, s, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = font(BOLD, min_size)
    return f, wrap(d, s, f, max_w)


# ---------------------------------------------------------------- icons
# Every icon draws inside its box, scaled from the box height.

def icon_summit(d, box):
    """Skyline, a sun, and three pennant flags for the Shenzhen summit."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    d.ellipse([x1 - 74, y0 + 2, x1 - 14, y0 + 62], fill=(240, 178, 60))
    base = y1 - 4
    heights = [0.34, 0.55, 0.42, 0.66, 0.38, 0.5]
    bw = (x1 - x0 - 8) // len(heights)
    for i, hf in enumerate(heights):
        bx = x0 + 4 + i * bw
        d.rectangle([bx, base - h * hf, bx + bw - 5, base], fill=(70, 92, 116))
    cols = [(196, 48, 49), (227, 160, 8), (46, 95, 138)]
    for i, c in enumerate(cols):
        px = x0 + 26 + i * 52
        top = y0 + 8
        d.line([px, top, px, base - h * 0.62], fill=INK, width=4)
        d.polygon([(px, top), (px + 34, top + 10), (px, top + 22)], fill=c)


def icon_drone(d, box):
    """A quadcopter drone, a dashed arc, and an island in a strait."""
    x0, y0, x1, y1 = box
    cx, cy = x0 + 62, y0 + 20
    d.rounded_rectangle([cx - 17, cy - 8, cx + 17, cy + 8], 5, fill=INK)
    for dx, dy in [(-30, -12), (30, -12), (-30, 12), (30, 12)]:
        d.line([cx, cy, cx + dx, cy + dy], fill=INK, width=4)
        d.ellipse([cx + dx - 11, cy + dy - 4, cx + dx + 11, cy + dy + 4],
                  outline=INK, width=3)
    d.ellipse([cx - 5, cy + 7, cx + 5, cy + 15], fill=(176, 58, 46))
    tx, ty = x1 - 52, y1 - 26
    for i in range(13):
        t = i / 12
        px = cx + (tx - cx) * t
        py = cy + 16 + (ty - cy - 16) * t + math.sin(t * 3.0) * 5
        if i % 2 == 0:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(176, 58, 46))
    for ang in range(0, 360, 45):
        ex = tx + 11 * math.cos(math.radians(ang))
        ey = ty + 11 * math.sin(math.radians(ang))
        d.line([tx, ty, ex, ey], fill=(227, 120, 8), width=3)
    d.polygon([(x1 - 128, y1 - 4), (x1 - 66, y1 - 20), (x1 - 14, y1 - 16),
               (x1 - 6, y1 - 4)], fill=(146, 116, 66))
    for wx in range(x0 + 4, x1 - 140, 30):
        d.arc([wx, y1 - 12, wx + 21, y1], 0, 180, fill=(46, 95, 138), width=3)


def icon_bridge(d, box):
    """The Kerch Bridge: two towers, a deck, one span fallen into the sea."""
    x0, y0, x1, y1 = box
    deck_y = y0 + (y1 - y0) * 0.42
    mid = (x0 + x1) // 2
    for tx in (x0 + 34, x1 - 48):
        d.rectangle([tx, y0 + 4, tx + 11, deck_y + 14], fill=(70, 92, 116))
        d.line([tx + 5, y0 + 4, mid, deck_y - 4], fill=(70, 92, 116), width=3)
    d.rectangle([x0 + 4, deck_y, mid - 12, deck_y + 7], fill=INK)
    d.rectangle([mid + 92, deck_y, x1 - 4, deck_y + 7], fill=INK)
    fx, fy = mid - 2, deck_y + 13
    d.polygon([(fx, fy), (fx + 76, fy + 15), (fx + 73, fy + 23),
               (fx - 3, fy + 7)], fill=(176, 58, 46))
    for wx in range(x0 + 4, x1 - 18, 30):
        d.arc([wx, y1 - 13, wx + 21, y1 - 1], 0, 180,
              fill=(46, 95, 138), width=3)
    for dx in (fx + 16, fx + 42, fx + 66):
        d.line([dx, fy + 26, dx - 5, fy + 36], fill=(46, 95, 138), width=3)
        d.line([dx, fy + 26, dx + 5, fy + 36], fill=(46, 95, 138), width=3)


def icon_capitol(d, box):
    """The US Capitol: dome, columns and steps, scaled to the box."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    cx = (x0 + x1) // 2
    r = min(24, (x1 - x0) // 2 - 16)
    # spire and dome: a true semicircle of radius r sitting on the band
    d.ellipse([cx - 3, y0, cx + 3, y0 + 5], fill=(227, 160, 8))
    d.pieslice([cx - r, y0 + 4, cx + r, y0 + 4 + 2 * r], 180, 360,
               fill=(31, 58, 147))
    band_y = y0 + 4 + r
    d.rectangle([cx - r - 9, band_y, cx + r + 9, band_y + 5], fill=INK)
    col_top = band_y + 8
    col_bot = y1 - 5
    for i in range(4):
        colx = cx - r - 2 + i * (2 * r // 3)
        d.rectangle([colx, col_top, colx + 6, col_bot], fill=(70, 92, 116))
    d.rectangle([cx - r - 13, y1 - 3, cx + r + 13, y1], fill=INK)


def icon_virus(d, box):
    """A virus pictogram: spiked circle, for the Ebola surge."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = (y1 - y0) * 0.27
    for ang in range(0, 360, 36):
        ex = cx + (r + 11) * math.cos(math.radians(ang))
        ey = cy + (r + 11) * math.sin(math.radians(ang))
        d.line([cx, cy, ex, ey], fill=(176, 58, 46), width=5)
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(176, 58, 46))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(202, 111, 30))
    for dx, dy in [(-9, -6), (8, -10), (2, 7), (-6, 11), (11, 4)]:
        d.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3],
                  fill=(246, 241, 231))


def icon_cyclone(d, box):
    """A spiral storm with rain streaks, for Cyclone Xavier."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    cx, cy = (x0 + x1) // 2, y0 + h * 0.42
    # a true spiral: radius grows with angle, drawn as one polyline
    pts = []
    for i in range(90):
        theta = i / 89 * 4.4 * math.pi
        r = 2 + theta * (h * 0.46) / (4.4 * math.pi)
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    d.line(pts, fill=(108, 52, 131), width=5, joint="curve")
    for i in range(5):
        rx = x0 + (x1 - x0) * (0.18 + 0.16 * i)
        d.line([rx, y1 - 16, rx - 6, y1 - 2], fill=(46, 95, 138), width=4)


# ---------------------------------------------------------------- panels

def chip(d, x, y, text, colour, size=20):
    f = font(BOLD, size)
    w = text_w(d, text, f) + 20
    d.rounded_rectangle([x, y, x + w, y + size + 11], 6, fill=colour)
    d.text((x + 10, y + 4), text, font=f, fill=(255, 255, 255))
    return y + size + 11


def caption_lines(d, caption, max_w, size, max_lines):
    """Wrap a caption, truncating with an ellipsis if it cannot fit."""
    f = font(REG, size)
    lines = wrap(d, caption, f, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and text_w(d, last + "…", f) > max_w:
            last = last[:-1]
        lines[-1] = last + "…"
    return f, lines


def panel(d, box, colour, tag, icon, headline, caption, icon_h,
          head_size, cap_size):
    """A story card with a strict vertical budget: chip, icon, headline,
    caption — each sized so the next one still fits inside the card."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 10, fill=CARD, outline=BORDER, width=2)
    ty = chip(d, x0 + 14, y0 + 12, tag, colour)
    icon(d, [x0 + 14, ty + 5, x1 - 14, ty + 5 + icon_h])
    hy = ty + 5 + icon_h + 7
    max_w = x1 - x0 - 28
    # reserve at least one caption line before sizing the headline
    head_room = (y1 - 10) - hy - (cap_size + 6)
    max_head = max(1, head_room // (head_size + 5))
    f, lines = fit_lines(d, headline, max_w, head_size, max_head)
    for ln in lines:
        d.text((x0 + 14, hy), ln, font=f, fill=INK)
        hy += f.size + 5
    cap_room = (y1 - 8) - hy
    max_cap = max(1, cap_room // (cap_size + 5))
    cf, clines = caption_lines(d, caption, max_w, cap_size, max_cap)
    for ln in clines:
        d.text((x0 + 14, hy + 1), ln, font=cf, fill=MUTED)
        hy += cf.size + 5


def lead_panel(d, box, colour, tag, icon, headline, caption):
    """The lead story: chip and icon in a left column, text at the right,
    starting level with the chip so the full height is usable."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 10, fill=CARD, outline=BORDER, width=2)
    chip(d, x0 + 16, y0 + 14, tag, colour, size=19)
    icon(d, [x0 + 16, y0 + 62, x0 + 292, y1 - 14])
    tx = x0 + 318
    max_w = x1 - tx - 16
    hy = y0 + 16
    head_room = (y1 - 12) - hy - (22 + 6) * 2
    max_head = max(1, head_room // (38 + 6))
    f, lines = fit_lines(d, headline, max_w, 38, max_head)
    for ln in lines:
        d.text((tx, hy), ln, font=f, fill=INK)
        hy += f.size + 6
    cf, clines = caption_lines(d, caption, max_w, 22, 2)
    for ln in clines:
        d.text((tx, hy + 4), ln, font=cf, fill=MUTED)
        hy += cf.size + 5


# ---------------------------------------------------------------- build

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead: kicker, day name, the date fitted to the full width
    kf = font(BOLD, 27)
    kicker = "T H E   W O R L D   I N   O N E   P I C T U R E"
    d.text(((W - text_w(d, kicker, kf)) / 2, 20), kicker, font=kf, fill=INK)
    wf = font(BOLD, 37)
    day = "WEDNESDAY"
    d.text(((W - text_w(d, day, wf)) / 2, 54), day, font=wf,
           fill=(176, 58, 46))
    df = fit_width(d, "18 NOVEMBER 2026", BOLD, 116, W - 48)
    d.text(((W - text_w(d, "18 NOVEMBER 2026", df)) / 2, 96),
           "18 NOVEMBER 2026", font=df, fill=INK)
    rule_y = 96 + df.size + 14
    d.rectangle([30, rule_y, W - 30, rule_y + 6], fill=INK)
    sf = font(REG, 23)
    sub = "The day's biggest stories — diplomacy, conflict, politics, health, weather"
    d.text(((W - text_w(d, sub, sf)) / 2, rule_y + 12), sub, font=sf,
           fill=MUTED)
    top = rule_y + 48

    # lead story
    lead_panel(
        d, [30, top, 994, top + 224], (154, 123, 10),
        "DIPLOMACY · SHENZHEN", icon_summit,
        "XI & PUTIN MEET AS TRUMP ARRIVES FOR A THREE-WAY SUMMIT",
        "The US, Chinese and Russian leaders gather for APEC talks — "
        "Ukraine, Iran and trade top the agenda.")

    # middle row
    mid = top + 238
    panel(
        d, [30, mid, 502, mid + 232], (176, 58, 46), "CONFLICT · MIDDLE EAST",
        icon_drone,
        "US STRIKES IRAN'S QESHM ISLAND; IRAN FIRES DRONES AT BAHRAIN & KUWAIT",
        "Tit-for-tat strikes around the Strait of Hormuz threaten Gulf "
        "shipping and oil.", icon_h=58, head_size=25,
        cap_size=19)
    panel(
        d, [522, mid, 994, mid + 232], (46, 95, 138), "WAR · EUROPE",
        icon_bridge,
        "UKRAINE HITS THE CRIMEA BRIDGE AGAIN — A ROAD SPAN FALLS",
        "A second straight day of strikes on the Kerch Bridge, Russia's "
        "lifeline to occupied Crimea.", icon_h=58, head_size=25,
        cap_size=19)

    # bottom row
    bot = mid + 246
    panel(
        d, [30, bot, 341, bot + 180], (31, 58, 147), "POLITICS · USA",
        icon_capitol,
        "DEMOCRATS TAKE THE SENATE, 56-44",
        "Peltola flips Alaska to seal it.",
        icon_h=48, head_size=20, cap_size=15)
    panel(
        d, [357, bot, 668, bot + 180], (17, 120, 100), "HEALTH · DR CONGO",
        icon_virus,
        "EBOLA CASES DOUBLE IN CONGO",
        "11,000+ cases, 5,400 dead — UN.",
        icon_h=48, head_size=20, cap_size=15)
    panel(
        d, [684, bot, 994, bot + 180], (108, 52, 131), "WEATHER · PACIFIC",
        icon_cyclone,
        "CYCLONE XAVIER SLAMS THE COOK ISLANDS",
        "A Category 5 landfall in the north.",
        icon_h=48, head_size=20, cap_size=15)

    # ticker
    tick_y = bot + 192
    d.rectangle([0, tick_y, W, H], fill=INK)
    line1 = "ALSO TODAY — MARKETS SLIDE: DAX -2.1% · CAC 40 -1.6% · FTSE 100 DOWN"
    tf = fit_width(d, line1, BOLD, 23, W - 56)
    d.text((30, tick_y + 12), line1, font=tf, fill=(240, 178, 60))
    line2 = ("MEASLES-FREE STATUS LOST AFTER 26 YEARS · NVIDIA REVENUE "
             "DOUBLES · SIBERIA PLANE CRASH KILLS 19")
    cf2 = fit_width(d, line2, REG, 21, W - 56)
    d.text((30, tick_y + 48), line2, font=cf2, fill=(246, 241, 231))

    img.save("entry.png", optimize=True)
    print("entry.png written")


if __name__ == "__main__":
    build()
