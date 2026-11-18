#!/usr/bin/env python3
"""draw_v2.py — builds entry.png for the news-image-20261118 entry.

A dense broadsheet front page for Wednesday 18 November 2026, drawn
entirely with Pillow: a giant date masthead, a story-count strip,
fifteen numbered story cards with flat pictograms, a pinned world
map, a by-the-numbers panel, a date-check box, a briefs section and a
faithfulness footer. All text is font-rendered from the data tables
below, so nothing can garble and the counts printed on the page are
computed from the stories actually shown.

Story selection follows the wire consensus for the day (Reuters, AP,
AFP, BBC, Al Jazeera and agency reporting of 18 November 2026);
contested claims are attributed in the line that carries them, and
stories from before Wednesday are named in the date-check box instead
of being passed off as the day's news.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- setup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (246, 241, 229)
INK = (20, 30, 42)
GREY = (92, 96, 100)
RED = (172, 48, 36)
DARKBAR = (20, 30, 42)
CARDLINE = (196, 186, 164)
WHITE = (252, 250, 244)

LIB = "/usr/share/fonts/truetype/liberation"
DEJ = "/usr/share/fonts/truetype/dejavu"


def font(path, size):
    return ImageFont.truetype(path, size)


def F(size, bold=False, serif=False):
    if serif:
        return font(f"{DEJ}/DejaVuSerif-Bold.ttf", size)
    return font(f"{LIB}/LiberationSans{'-Bold' if bold else '-Regular'}.ttf", size)


def FB(size):
    return font(f"{DEJ}/DejaVuSans-Bold.ttf", size)


# ---------------------------------------------------------------- text utils

def text_w(d, s, fnt, spacing=0):
    w = d.textlength(s, font=fnt)
    if spacing:
        w += spacing * max(0, len(s) - 1)
    return w


def draw_spaced(d, xy, s, fnt, fill, spacing=0, anchor_left=True):
    x, y = xy
    if not anchor_left:  # centre on x
        x -= text_w(d, s, fnt, spacing) / 2
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt) + spacing
    return cx


def wrap(d, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        trial = f"{cur} {w_}".strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- story data
# (number, kicker, accent, pictogram key, headline, sub-deck)

CARDS = [
    (1, "MIDDLE EAST · GULF", (172, 48, 36), "drone",
     "GULF STATES INTERCEPT IRANIAN DRONES AFTER US STRIKES QESHAM",
     "US jets hit a Guards missile site on Qeshm; Bahrain's third interception this week."),
    (2, "EUROPE · UKRAINE WAR", (36, 80, 126), "drones",
     "RUSSIA FIRES 141 DRONES AT UKRAINE OVERNIGHT",
     "Air defences downed 126; hits were recorded at seven locations — Air Force."),
    (3, "ASIA · DIPLOMACY", (146, 106, 16), "flags",
     "XI & PUTIN MEET IN SHENZHEN, ON THE EVE OF TRUMP TALKS",
     "The trilateral is set for Thursday; opening APEC, Xi attacks protectionism — AFP."),
    (4, "USA · POLITICS", (24, 62, 128), "dome",
     "PELTOLA WINS ALASKA — SENATE GOES 56–44",
     "144,302 votes to Sullivan's 131,844; a ninth Democratic flip of the midterms — AP."),
    (5, "SCIENCE · SPACE", (70, 60, 140), "dish",
     "VOYAGER 1 CROSSES ONE LIGHT-DAY FROM EARTH",
     "16 billion miles out; its signal now takes a full 24 hours to reach home — NASA."),
    (6, "CULTURE · GAMING", (196, 90, 30), "pad",
     "GTA VI BEGINS ITS GLOBAL ROLLOUT, 13 YEARS ON",
     "Full launch Thursday; ~17.1m copies already sold, Sensor Tower estimates."),
    (7, "EUROPE · ECONOMY", (30, 110, 100), "tag",
     "UK INFLATION RISES TO 3.6%, A ONE-YEAR HIGH",
     "Fuel and tobacco pushed prices up in October; core inflation held at 2.8% — ONS."),
    (8, "EUROPE · UKRAINE AID", (36, 80, 126), "euro",
     "EU UNVEILS A €45BN LOAN PLAN FOR UKRAINE",
     "Two-thirds of Kyiv's €70bn gap for 2027; repayment tied to Russian reparations."),
    (9, "ASIA · WEATHER", (30, 110, 140), "spiral",
     "CYCLONE AKVAN: 204,070 FACE EVACUATION IN ODISHA",
     "A severe Bay of Bengal storm; landfall due Friday, gusts to 145 km/h — IMD."),
    (10, "MIDDLE EAST · GAZA", (120, 110, 40), "tent",
     "UN WARNS OF COLD DEATHS IN GAZA AS WINTER SETS IN",
     "1.4 million face acute hunger; 1.7 million are displaced, aid agencies say."),
    (11, "CLIMATE · COP31", (60, 120, 60), "leaf",
     "COP31 DRAFT TEXT CARRIES 144 DISPUTED ITEMS",
     "The Antalya talks enter their final days; the summit is due to end Friday."),
    (12, "MARKETS · WALL STREET", (90, 90, 96), "bars",
     "NVIDIA REVENUE DOUBLES TO $115.8BN — DOW FALLS 849",
     "A record quarter for the AI chipmaker fails to lift US blue-chip shares."),
]

WIDE = [
    (13, "AFRICA · SUDAN", (150, 60, 40), "scale",
     "AMNESTY SEEKS WAR-CRIMES PROBE OF RSF DRONE STRIKES",
     "Nine strikes on El Obeid killed 37 civilians, its report says; the RSF denies blame."),
    (14, "ASIA · LABOUR", (170, 100, 30), "shirt",
     "BANGLADESH PAY PROTESTS SHUT ABOUT 500 FACTORIES",
     "Workers seek 30,000 taka a month, up from 12,500; police fired tear gas on Tuesday — AFP."),
    (15, "EUROPE · HEALTH", (40, 120, 110), "shield",
     "RESISTANT INFECTIONS UP 72% SINCE 2019, EU WARNS",
     "ECDC counts 35,000 deaths a year and four of five 2030 targets off track."),
]

BRIEFS = [
    "Ukraine confirms strikes on Ilsky & Afipsky refineries in Russia",
    "Kerch Bridge road span down after second-night strike, Kyiv says",
    "Saudi-led coalition destroys a Houthi cruise missile aimed at Riyadh",
    "Iran says it shot down a US MQ-9 drone near the Strait of Hormuz",
    "US says it sank five Iranian tankers in the Gulf of Oman",
    "Iran declares a restricted sea zone off Chabahar, in the Gulf of Oman",
    "Magnitude 6.0 earthquake strikes Papua New Guinea",
    "Magnitude 5.3 earthquake strikes Romania",
    "Iranian agent jailed 27 years in US over plot to kill Trump",
    "Iraq reopens a long-idle oil pipeline to Turkey",
    "World Court to rule on Myanmar genocide case",
    "Five EU states plan migrant return hubs in Rwanda",
    "Trump meets Quad partners in Manila before flying to Shenzhen",
    "Thailand flags arsenic contamination linked to Myanmar mines",
    "Reports of Russian bombers active near Japan and Taiwan",
    "Oil slips on a US stock build; Hormuz risks limit the fall",
    "Pakistan cuts petrol by Rs3 to Rs325 a litre",
    "Pakistan edge India in a last-ball blind-cricket Asia Cup thriller",
    "Cyclone Xavier, at Category 5, hits the Northern Cook Islands",
    "Logitech gives 7,000 staff the day off for GTA VI's launch",
    "GTA VI launch-day leave bookings run 32% above last year",
    "Take-Two shares jump 6% as the GTA VI rollout begins",
    "UK gas prices jump 6.3% in a month; electricity falls 0.8%",
    "Four EU states opt out of the €45bn Ukraine loan plan",
    "Australia, Canada, Italy & Britain urge open Gaza aid crossings",
    "EU defence chief: Russia plans 20m drones by 2027, Kyiv reports",
    "BoE sees UK inflation near 5% by mid-2027 on energy prices",
]

NUMBERS = [
    ("141", "drones fired at Ukraine"),
    ("126", "of them downed by air defences"),
    ("204,070", "evacuations in Odisha"),
    ("$115.8bn", "Nvidia revenue, a record"),
    ("−849", "points on the Dow Jones"),
    ("€45bn", "EU loan for Ukraine"),
]

DATECHECK = ("DR Congo's Ebola count passing 11,000 — reported Tuesday, not "
             "Wednesday. · The US measles-elimination ruling — announced "
             "before Wednesday. · Shenzhen's trilateral summit — still to "
             "come on Thursday; card 3 treats it as next, not news.")

# map pins: card number -> (lon, lat, dx, dy label nudge)
PINS = {
    1: (52, 25, 2, 2), 2: (34, 49, 2, 0), 3: (114, 23, 0, 0),
    4: (-152, 64, 0, 0), 6: (-98, 39, 0, 0), 7: (-3, 55, -5, -3),
    8: (7, 49, 4, 3), 9: (84, 19, -3, 2), 10: (34, 29, -2, 4),
    11: (29, 38, -4, -3), 12: (-74, 41, 0, 0), 13: (30, 13, 0, 0),
    14: (93, 25, 3, -2), 15: (18, 60, 0, -2),
}

NAMER = [  # rough continent silhouettes as (lon, lat) polygons
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-76, 58), (-70, 55), (-65, 50), (-70, 44), (-74, 40),
     (-76, 35), (-80, 32), (-81, 26), (-84, 22), (-90, 20), (-94, 17),
     (-97, 16), (-102, 15), (-105, 20), (-110, 23), (-114, 29), (-120, 34),
     (-124, 40), (-124, 46), (-130, 54), (-145, 60), (-158, 58), (-166, 60)],
    [(-45, 60), (-30, 68), (-22, 70), (-20, 76), (-30, 80), (-50, 78),
     (-58, 70), (-55, 64)],
    [(-78, 7), (-70, 11), (-62, 10), (-55, 6), (-50, 0), (-44, -3),
     (-38, -8), (-40, -15), (-42, -22), (-48, -27), (-52, -33), (-58, -38),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-72, -54), (-73, -46),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-80, -4),
     (-78, 1)],
    [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (34, 28), (38, 22),
     (40, 15), (43, 12), (48, 11), (51, 12), (48, 5), (42, -2), (40, -10),
     (38, -18), (36, -24), (33, -28), (28, -33), (20, -35), (17, -32),
     (15, -27), (13, -18), (12, -12), (13, -6), (9, -1), (9, 4), (4, 6),
     (-3, 5), (-8, 5), (-13, 8), (-16, 12), (-17, 15), (-16, 20), (-15, 25),
     (-13, 28), (-10, 31)],
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-5, 48), (0, 49), (3, 51),
     (7, 54), (8, 57), (12, 58), (18, 56), (20, 54), (24, 58), (28, 60),
     (30, 64), (35, 67), (45, 68), (65, 69), (85, 70), (105, 70), (125, 71),
     (145, 71), (160, 67), (178, 65), (175, 62), (162, 58), (156, 52),
     (148, 47), (142, 42), (138, 36), (130, 33), (124, 30), (121, 26),
     (115, 22), (109, 19), (106, 10), (104, 6), (101, 8), (99, 13),
     (96, 16), (93, 17), (90, 22), (87, 21), (84, 19), (80, 14), (77, 8),
     (76, 11), (73, 17), (71, 21), (67, 24), (61, 25), (56, 26), (52, 27),
     (50, 29), (48, 30), (49, 26), (55, 24), (59, 22), (55, 17), (52, 15),
     (45, 12), (43, 12), (40, 15), (38, 21), (36, 24), (35, 28), (34, 31),
     (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (19, 40), (15, 38),
     (12, 38), (10, 37), (3, 37), (-2, 37)],
    [(-5, 50), (-3, 53), (-5, 55), (-7, 58), (-4, 58), (-2, 55), (-1, 52)],
    [(113, -22), (114, -30), (118, -35), (124, -33), (132, -32), (135, -35),
     (138, -36), (140, -38), (145, -38), (150, -37), (153, -30), (153, -25),
     (150, -22), (146, -19), (142, -15), (142, -11), (140, -13), (136, -12),
     (132, -11), (128, -14), (124, -17), (120, -20), (116, -21)],
]

# ---------------------------------------------------------------- pictograms

def picto(d, key, x, y, w, h, c):
    """Tiny flat pictograms inside a card's illustration band."""
    cx, cy = x + w / 2, y + h / 2
    if key == "drone":
        d.rectangle([cx - 9, cy - 3, cx + 9, cy + 3], fill=c)
        for dx, dy in ((-14, -6), (14, -6), (-14, 6), (14, 6)):
            d.ellipse([cx + dx - 5, cy + dy - 2, cx + dx + 5, cy + dy + 2], outline=c, width=2)
        for bx, by in ((x + w - 26, y + 5), (x + w - 14, y + 12)):
            for a in range(0, 360, 45):
                import math
                r1, r2 = 2, 5
                d.line([bx + r1 * math.cos(a * 3.1416 / 180), by + r1 * math.sin(a * 3.1416 / 180),
                        bx + r2 * math.cos(a * 3.1416 / 180), by + r2 * math.sin(a * 3.1416 / 180)], fill=c, width=2)
    elif key == "drones":
        for i, ox in enumerate((-52, 0, 52)):
            yy = cy + (4 if i == 1 else -3)
            d.rectangle([cx + ox - 6, yy - 2, cx + ox + 6, yy + 2], fill=c)
            for dx in (-10, 10):
                d.ellipse([cx + ox + dx - 4, yy - 5, cx + ox + dx + 4, yy - 1], outline=c, width=1)
    elif key == "flags":
        flag_cols = [(172, 48, 36), (146, 106, 16), (36, 80, 126)]
        for i, cc in enumerate(flag_cols):
            d.line([x + 30 + i * 40, y + h - 3, x + 30 + i * 40, y + 3], fill=INK, width=2)
            d.polygon([(x + 30 + i * 40, y + 3), (x + 30 + i * 40 + 16, y + 6),
                       (x + 30 + i * 40, y + 10)], fill=cc)
        d.rectangle([x + w - 52, y + 8, x + w - 40, y + h - 3], fill=c)
        d.rectangle([x + w - 36, y + 13, x + w - 26, y + h - 3], fill=c)
        d.rectangle([x + w - 22, y + 5, x + w - 10, y + h - 3], fill=c)
    elif key == "dome":
        d.arc([cx - 20, cy - 12, cx + 20, cy + 14], 180, 360, fill=c, width=3)
        d.line([cx, cy - 14, cx, cy - 19], fill=c, width=2)
        d.rectangle([cx - 26, cy + 6, cx + 26, cy + 9], fill=c)
        for ox in (-18, -6, 6, 18):
            d.line([cx + ox, cy + 9, cx + ox, cy + 14], fill=c, width=2)
        d.rectangle([cx - 28, cy + 14, cx + 28, cy + 16], fill=c)
    elif key == "dish":
        # a little probe: body, two solar wings, signal arcs flying off
        d.rectangle([x + 22, cy - 5, x + 40, cy + 5], fill=c)
        d.rectangle([x + 6, cy - 8, x + 19, cy + 8], outline=c, width=2)
        d.rectangle([x + 43, cy - 8, x + 56, cy + 8], outline=c, width=2)
        d.line([x + 31, cy - 5, x + 31, cy - 12], fill=c, width=2)
        d.ellipse([x + 29, cy - 14, x + 33, cy - 10], fill=c)
        for r in (7, 12, 17):
            d.arc([x + 58 - r, cy - 14 - r, x + 58 + r, cy - 14 + r], 300, 40, fill=c, width=2)
        for sx, sy in ((x + w - 26, y + 4), (x + w - 13, y + 9), (x + w - 36, y + 11)):
            d.line([sx - 3, sy, sx + 3, sy], fill=c, width=1)
            d.line([sx, sy - 3, sx, sy + 3], fill=c, width=1)
    elif key == "pad":
        d.rounded_rectangle([cx - 30, cy - 10, cx + 30, cy + 10], 9, outline=c, width=3)
        d.line([cx - 20, cy, cx - 12, cy], fill=c, width=2)
        d.line([cx - 16, cy - 4, cx - 16, cy + 4], fill=c, width=2)
        for ox, oy in ((16, -4), (22, 1), (11, 1)):
            d.ellipse([cx + ox - 2, cy + oy - 2, cx + ox + 2, cy + oy + 2], fill=c)
        d.line([x + 14, y + h - 2, x + 14, y + 6], fill=c, width=2)
        for a in (-30, 0, 30):
            import math
            d.line([x + 14, y + 7, x + 14 + 8 * math.sin(a * 3.1416 / 180),
                    y + 7 - 7 * math.cos(a * 3.1416 / 180)], fill=c, width=2)
    elif key == "tag":
        d.polygon([(x + 18, cy + 8), (x + 18, cy - 8), (x + 40, cy - 8), (x + 52, cy),
                   (x + 40, cy + 8)], outline=c, width=3)
        d.ellipse([x + 24, cy - 3, x + 29, cy + 2], outline=c, width=2)
        tx = x + 62
        d.text((tx, cy - 11), "%", font=F(20, bold=True), fill=c)
        d.line([tx + 34, cy + 8, tx + 46, cy - 8], fill=c, width=3)
        d.polygon([(tx + 46, cy - 10), (tx + 46, cy - 2), (tx + 39, cy - 6)], fill=c)
    elif key == "euro":
        d.text((x + 16, cy - 13), "€", font=F(26, bold=True), fill=c)
        import math
        for i in range(8):
            a = i * 3.1416 / 4
            sx, sy = cx + 26 + 13 * math.cos(a), cy + 11 * math.sin(a)
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=c)
        d.arc([cx + 13, cy - 11, cx + 39, cy + 11], 0, 360, fill=c, width=2)
    elif key == "spiral":
        import math
        pts = []
        for t in range(0, 340, 6):
            r = 2 + t / 26.0
            a = t * 3.1416 / 180 * 2.2
            pts.append((cx - 20 + r * math.cos(a), cy + r * 0.82 * math.sin(a)))
        d.line(pts, fill=c, width=3)
        for i, ox in enumerate((34, 52, 70)):
            for px in range(0, 26, 9):
                d.arc([cx + ox + px, cy + 6, cx + ox + px + 9, cy + 13], 0, 180, fill=c, width=2)
    elif key == "tent":
        d.polygon([(cx - 32, cy + 12), (cx, cy - 14), (cx + 32, cy + 12)], outline=c, width=3)
        d.polygon([(cx - 8, cy + 12), (cx, cy - 3), (cx + 8, cy + 12)], fill=c)
        d.ellipse([x + w - 42, y + 2, x + w - 28, y + 16], outline=c, width=2)
        d.line([x + 10, cy + 12, x + 30, cy + 12], fill=c, width=2)
    elif key == "leaf":
        d.ellipse([cx - 22, cy - 10, cx + 8, cy + 12], fill=c)
        d.polygon([(cx + 8, cy + 12), (cx + 20, cy - 10), (cx - 22, cy - 10)], fill=PAPER)
        d.line([cx - 18, cy + 9, cx + 14, cy - 7], fill=PAPER, width=2)
        d.arc([cx + 16, cy - 12, cx + 44, cy + 14], 90, 300, fill=c, width=2)
    elif key == "bars":
        for i, bh in enumerate((8, 14, 21)):
            bx = x + 18 + i * 16
            d.rectangle([bx, cy + 12 - bh, bx + 10, cy + 12], fill=c)
        d.rectangle([cx + 16, cy - 11, cx + 38, cy + 11], outline=c, width=2)
        for gy in (-5, 0, 5):
            d.line([cx + 20, cy + gy, cx + 34, cy + gy], fill=c, width=1)
    elif key == "scale":
        d.line([cx, cy - 12, cx, cy + 10], fill=c, width=2)
        d.line([cx - 13, cy - 8, cx + 13, cy - 8], fill=c, width=2)
        for sgn in (-1, 1):
            px = cx + sgn * 13
            d.line([px - 5, cy + 1, px, cy - 8], fill=c, width=1)
            d.line([px + 5, cy + 1, px, cy - 8], fill=c, width=1)
            d.arc([px - 6, cy - 2, px + 6, cy + 5], 0, 180, fill=c, width=2)
        d.rectangle([cx - 9, cy + 10, cx + 9, cy + 13], fill=c)
    elif key == "shirt":
        d.polygon([(cx - 6, cy - 11), (cx - 14, cy - 7), (cx - 11, cy + 1),
                   (cx - 6, cy - 2), (cx - 6, cy + 12), (cx + 6, cy + 12),
                   (cx + 6, cy - 2), (cx + 11, cy + 1), (cx + 14, cy - 7),
                   (cx + 6, cy - 11)], outline=c, width=2)
        d.arc([cx - 5, cy - 13, cx + 5, cy - 7], 0, 180, fill=c, width=2)
    elif key == "shield":
        d.polygon([(cx, cy - 13), (cx + 12, cy - 9), (cx + 12, cy + 2),
                   (cx, cy + 14), (cx - 12, cy + 2), (cx - 12, cy - 9)], outline=c, width=2)
        d.rectangle([cx - 2, cy - 7, cx + 2, cy + 7], fill=c)
        d.rectangle([cx - 7, cy - 2, cx + 7, cy + 2], fill=c)


# ---------------------------------------------------------------- drawing

def chip(d, x, y, n, colour, r=8):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=colour)
    s = str(n)
    fnt = F(10 if n < 10 else 9, bold=True)
    tw = d.textlength(s, font=fnt)
    d.text((x + r - tw / 2, y + r - 6), s, font=fnt, fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(CARDS) + len(WIDE) + len(BRIEFS)

    # ---- masthead
    draw_spaced(d, (W / 2, 12), "THE WORLD IN ONE PICTURE", F(16, bold=True), INK, spacing=6, anchor_left=False)
    draw_spaced(d, (W / 2, 36), "WEDNESDAY", F(30, bold=True), RED, spacing=12, anchor_left=False)
    date_f = FB(74)
    draw_spaced(d, (W / 2, 70), "18 NOVEMBER 2026", date_f, INK, spacing=2, anchor_left=False)
    d.rectangle([14, 154, 1010, 157], fill=INK)
    d.rectangle([14, 160, 1010, 161], fill=INK)

    # ---- story-count strip
    d.rectangle([14, 166, 1010, 192], fill=DARKBAR)
    strip = f"{total} STORIES · 5 CONTINENTS · ALL FROM WEDNESDAY 18 NOVEMBER 2026"
    draw_spaced(d, (W / 2, 172), strip, F(14, bold=True), WHITE, spacing=1, anchor_left=False)

    # ---- numbered cards, 4 x 3
    cw, chh, gx, gy = 243, 118, 8, 8
    for i, (n, kick, acc, pic, head, sub) in enumerate(CARDS):
        x = 14 + (i % 4) * (cw + gx)
        y = 200 + (i // 4) * (chh + gy)
        d.rounded_rectangle([x, y, x + cw, y + chh], 6, fill=WHITE, outline=CARDLINE, width=1)
        chip(d, x + 7, y + 6, n, acc, r=8)
        draw_spaced(d, (x + 29, y + 8), kick, F(9, bold=True), acc, spacing=1)
        band = (acc[0] // 6 + 240, acc[1] // 6 + 240, acc[2] // 6 + 238)
        d.rectangle([x + 7, y + 26, x + cw - 7, y + 50], fill=band)
        picto(d, pic, x + 7, y + 26, cw - 14, 24, acc)
        ly = y + 54
        for ln in wrap(d, head, F(12, bold=True), cw - 14)[:3]:
            d.text((x + 7, ly), ln, font=F(12, bold=True), fill=INK)
            ly += 13.5
        sy = y + 96
        for ln in wrap(d, sub, F(10), cw - 14)[:2]:
            d.text((x + 7, sy), ln, font=F(10), fill=(52, 58, 64))
            sy += 11.5

    # ---- wide cards 13-15
    for j, (n, kick, acc, pic, head, sub) in enumerate(WIDE):
        y = 578 + j * 40
        d.rounded_rectangle([14, y, 1010, y + 34], 6, fill=WHITE, outline=CARDLINE, width=1)
        picto(d, pic, 18, y + 2, 34, 30, acc)
        chip(d, 58, y + 9, n, acc, r=8)
        draw_spaced(d, (82, y + 4), kick, F(8, bold=True), acc, spacing=1)
        d.text((82, y + 15), head, font=F(13, bold=True), fill=INK)
        sl = wrap(d, sub, F(10), 430)
        sy = y + 5
        for ln in sl[:2]:
            d.text((566, sy), ln, font=F(10), fill=(52, 58, 64))
            sy += 12

    # ---- map + numbers + date check
    my = 700
    d.rounded_rectangle([14, my, 514, my + 134], 6, fill=(238, 242, 244), outline=CARDLINE, width=1)
    draw_spaced(d, (22, my + 6), "WHERE IT HAPPENED — PINS MATCH THE NUMBERED CARDS", F(10, bold=True), INK, spacing=0)
    mx0, my0, mw, mh = 22, my + 24, 484, 102

    def proj(lon, lat):
        return (mx0 + (lon + 168) / 360.0 * mw, my0 + (78 - lat) / 136.0 * mh)

    for poly in NAMER:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(203, 214, 200))
    for n, (lon, lat, dx, dy) in PINS.items():
        px, py = proj(lon, lat)
        px, py = px + dx, py + dy
        acc = (CARDS + WIDE)[n - 1][2]
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=acc, outline=WHITE, width=1)
        s = str(n)
        fnt = F(8 if n < 10 else 7, bold=True)
        d.text((px - d.textlength(s, font=fnt) / 2, py - 4.5), s, font=fnt, fill=WHITE)
    # Voyager: off the top-right corner of the chart, in deep space
    sx, sy = mx0 + mw - 12, my0 + 10
    for a in (0, 90, 45, 135):
        import math
        d.line([sx - 6 * math.cos(a * 3.1416 / 180), sy - 6 * math.sin(a * 3.1416 / 180),
                sx + 6 * math.cos(a * 3.1416 / 180), sy + 6 * math.sin(a * 3.1416 / 180)],
               fill=(70, 60, 140), width=2)
    d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(238, 242, 244), outline=(70, 60, 140), width=1)
    d.text((sx - 3, sy - 4.5), "5", font=F(8, bold=True), fill=(70, 60, 140))
    d.text((sx - 66, sy - 4), "5 · deep space", font=F(8), fill=(70, 60, 140))

    nx = 522
    d.rounded_rectangle([nx, my, 1010, my + 64], 6, fill=WHITE, outline=CARDLINE, width=1)
    draw_spaced(d, (nx + 8, my + 5), "WEDNESDAY BY THE NUMBERS", F(10, bold=True), INK, spacing=0)
    for i, (big, lab) in enumerate(NUMBERS):
        cx = nx + 8 + i * 80
        d.text((cx, my + 19), big, font=F(13, bold=True), fill=RED)
        ly = my + 36
        for ln in wrap(d, lab, F(8), 76)[:2]:
            d.text((cx, ly), ln, font=F(8), fill=GREY)
            ly += 9.5

    dy0 = my + 72
    d.rounded_rectangle([nx, dy0, 1010, my + 134], 6, fill=(250, 244, 224), outline=CARDLINE, width=1)
    draw_spaced(d, (nx + 8, dy0 + 5), "DATE CHECK — LEFT OUT ON PURPOSE", F(10, bold=True), RED, spacing=0)
    ly = dy0 + 20
    for ln in wrap(d, DATECHECK, F(9), 472)[:3]:
        d.text((nx + 8, ly), ln, font=F(9), fill=(52, 58, 64))
        ly += 11.5

    # ---- briefs
    by = 846
    draw_spaced(d, (14, by), f"ALSO ON WEDNESDAY — {len(BRIEFS)} MORE STORIES IN BRIEF",
                F(12, bold=True), INK, spacing=0)
    d.rectangle([14, by + 17, 1010, by + 18], fill=INK)
    col_w, col_x = 320, (14, 348, 682)
    for i, b in enumerate(BRIEFS):
        cx = col_x[i // 9]
        cy = by + 24 + (i % 9) * 13
        d.text((cx, cy), "• " + b, font=F(9), fill=(40, 46, 52))

    # ---- footer
    d.text((W / 2, 984), "Every story above happened, was reported, or was formally published on Wednesday 18 November 2026.",
           font=F(10), fill=GREY, anchor="ma")
    d.text((W / 2, 1000), "Contested claims are attributed to those who made them. Sources: Reuters · AP · AFP · BBC · Al Jazeera · Amnesty · ECDC · IMD · NASA JPL · ONS · UN. Original drawings.",
           font=F(10), fill=GREY, anchor="ma")

    img.save(OUT)
    with open(OUT, "rb") as fh:
        data = fh.read()
    print(f"wrote {OUT}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
