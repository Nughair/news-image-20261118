#!/usr/bin/env python3
"""draw_v3.py — builds entry.png for news-image-20261118 (v3).

One square broadsheet front page summing up the world news of
Wednesday 18 November 2026, drawn programmatically with Pillow:
masthead, region tally, 14 illustrated numbered cards, a dotted world
map with pins, a by-the-numbers strip, a DATE CHECK box and 34
numbered one-line briefs. Story selection follows the day's wire
consensus as seen on the live board's top entries; every figure is
carried from a named report and contested claims are attributed.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)
INK = (28, 30, 38)
FAINT = (96, 98, 104)
NAVY = (24, 38, 66)
RED = (179, 49, 42)
GOLD = (168, 124, 18)
CARD_BG = (253, 250, 243)
LINE = (176, 168, 148)

REGION_COLORS = {
    "MIDDLE EAST": (160, 82, 45),
    "EUROPE": (31, 95, 168),
    "ASIA": (109, 76, 159),
    "AFRICA": (150, 110, 14),
    "AMERICAS": (179, 49, 42),
    "OCEANIA": (30, 122, 110),
    "GLOBAL": (84, 95, 110),
    "SPACE": (52, 62, 110),
}

FONT_DIR = "/usr/share/fonts/truetype"


def pick(*paths):
    for p in paths:
        full = os.path.join(FONT_DIR, p)
        if os.path.exists(full):
            return full
    return None


SERIF_B = pick("noto/NotoSerif-Bold.ttf", "dejavu/DejaVuSerif-Bold.ttf")
SERIF = pick("noto/NotoSerif-Regular.ttf", "dejavu/DejaVuSerif.ttf")
SERIF_I = pick("noto/NotoSerif-Italic.ttf", "dejavu/DejaVuSerif-Italic.ttf", "noto/NotoSerif-Regular.ttf")
SANS_B = pick("noto/NotoSans-Bold.ttf", "dejavu/DejaVuSans-Bold.ttf")
SANS = pick("noto/NotoSans-Regular.ttf", "dejavu/DejaVuSans.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fit(draw, s, path, start, max_w, min_size=9):
    size = start
    while size > min_size and text_w(draw, s, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


# ---------------------------------------------------------------- stories
# Each card: (number, region, beat, illustration key, caption, headline,
#             deck, pin lon, pin lat or None)
CARDS = [
    (1, "MIDDLE EAST", "IRAN WAR", "gulf", "ALI AL SALEM · KUWAIT — THE GULF",
     "Kuwait and Bahrain say they intercepted Iranian drones",
     "Iran says it aimed at US forces at Ali Al Salem air base. Bahrain's third "
     "interception this week, after US jets struck Qeshm on Tuesday night.",
     48, 27),
    (2, "ASIA", "DIPLOMACY", "shenzhen", "SHENZHEN · APEC OPENS TODAY",
     "Xi greets Trump on the eve of the three-way summit",
     "APEC opens with Xi's keynote; Putin joined the banquet toast. The "
     "three-way talks are set for Thursday — they have not happened yet.",
     114, 22),
    (3, "AMERICAS", "US POLITICS", "alaska", "ALASKA · CALLED BY AP",
     "Democrat Peltola wins Alaska; Senate now 56–44",
     "144,302 votes to Sullivan's 131,844. A ninth Democratic gain — the most "
     "in a midterm since 1958, AP says.",
     -150, 64),
    (4, "EUROPE", "UKRAINE WAR", "drones", "UKRAINE · OVERNIGHT BARRAGE",
     "Russia fires 141 drones at Ukraine overnight",
     "Air force: 126 downed. Officials: 5 killed, 15 injured; power cut to "
     "80+ settlements in Rivne region.",
     32, 49),
    (5, "MIDDLE EAST", "GAZA", "gaza", "GAZA · REPORT TO THE UN",
     "Board of Peace warns the Gaza truce may collapse",
     "First report to the Security Council (obtained by AP): Israel blocked "
     "the civil administration.",
     34, 31),
    (6, "ASIA", "DISASTER", "akvan", "BAY OF BENGAL · LANDFALL FRIDAY",
     "Cyclone Akvan strengthens in the Bay of Bengal",
     "IMD: landfall in Andhra Pradesh around noon on Friday. Odisha readies "
     "up to 204,070 people to evacuate.",
     86, 20),
    (7, "EUROPE", "ECONOMY", "uk", "LONDON · ONS FIGURES",
     "UK inflation rises to 3.6%, highest in a year",
     "October CPI up from 3.5% as diesel hits a record high, the ONS says.",
     -2, 54),
    (8, "AFRICA", "SUDAN WAR", "sudan", "EL OBEID · SUDAN",
     "Amnesty: RSF drone strikes killed 37 in El Obeid",
     "It says the strikes should be investigated as war crimes. The RSF "
     "denies responsibility.",
     30, 13),
    (9, "GLOBAL", "CULTURE", "gta", "MIDNIGHT LAUNCH · NEW ZEALAND FIRST",
     "GTA VI goes on sale after a 13-year wait",
     "Midnight launch starts in New Zealand; 14.9m pre-orders, Sensor Tower "
     "estimates.",
     172, -41),
    (10, "EUROPE", "HEALTH", "ecdc", "EUROPE · ECDC WARNING",
     "Europe off track on antibiotic resistance",
     "Resistant K. pneumoniae blood infections up 72% since 2019, the ECDC "
     "warns.",
     10, 50),
    (11, "GLOBAL", "CLIMATE", "cop31", "ANTALYA · COP31 TALKS",
     "COP31: 75 countries back a “35 by 35” power goal",
     "Electricity to 35% of energy use by 2035 (Anadolu). Rockström warns "
     "of 2.8–3°C warming.",
     30, 37),
    (12, "ASIA", "LABOUR", "dhaka", "DHAKA · GARMENT DISTRICT",
     "Bangladesh protests shut at least 55 factories",
     "Workers seek Tk 30,000 a month, up from 12,500; police fired tear gas "
     "on Tuesday.",
     90, 24),
    (13, "SPACE", "SCIENCE", "voyager", "DEEP SPACE · NASA",
     "Voyager 1 is the first craft one light-day out",
     "NASA's probe passes 25.9 billion km; a command sent today arrives "
     "tomorrow.",
     None, None),
    (14, "EUROPE", "UKRAINE AID", "eu", "BRUSSELS · EU COMMISSION",
     "EU proposes a €45bn loan for Ukraine in 2027",
     "Two-thirds of a €70bn gap, repaid only once Russia pays reparations.",
     4, 50),
]

# Briefs: (number, region, lead-in, rest) — one printed line each.
BRIEFS = [
    (15, "ASIA", "Manila:", "Trump claims trade deal; Manila says none signed"),
    (16, "ASIA", "Manila:", "Quad leaders meet, first in over two years"),
    (17, "MIDDLE EAST", "Gaza:", "floods swamp tents; WHO urges open aid routes"),
    (18, "AFRICA", "Sudan:", "UN counts 2,230 civilians killed this year"),
    (19, "AFRICA", "Badme:", "Ethiopia–Eritrea artillery fire resumes"),
    (20, "ASIA", "Myanmar:", "junta says ASEAN unfair; ties to be reviewed"),
    (21, "AMERICAS", "US House:", "Democrats pick Jeffries, 251 of 262 votes"),
    (22, "GLOBAL", "FIFA:", "France's Diallo to challenge Infantino"),
    (23, "GLOBAL", "Gold:", "sinks to $3,792 an ounce, lowest in a year"),
    (24, "AMERICAS", "Wall Street:", "Dow falls 849, a fourth straight fall"),
    (25, "AMERICAS", "Tech:", "Anthropic prices its IPO; trades Thursday"),
    (26, "ASIA", "Tokyo:", "PM Takaichi makes her first visit to China"),
    (27, "AMERICAS", "Canada–China:", "tariff relief agreed on pork, seafood"),
    (28, "EUROPE", "Russia:", "19 die in a Kemerovo plane crash, media say"),
    (29, "EUROPE", "Serbia:", "a MiG-29 fighter crashes near Belgrade"),
    (30, "EUROPE", "Kosovo:", "ex-president Thaçi gets 17 months"),
    (31, "EUROPE", "Paris:", "court suspends the school-protest ban"),
    (32, "AFRICA", "Guinea:", "224 jailed over illegal gold mining"),
    (33, "AFRICA", "Mauritius:", "sets UK a December Chagos deadline"),
    (34, "AFRICA", "South Africa:", "inflation up to 5.2%, highest since 2024"),
    (35, "OCEANIA", "Cook Islands:", "Cyclone Xavier reaches Category 5"),
    (36, "OCEANIA", "New Zealand:", "tsunami advisory lifted after 60 cm surges"),
    (37, "MIDDLE EAST", "Riyadh:", "coalition says it downed a Houthi missile"),
    (38, "MIDDLE EAST", "Jerusalem:", "Knesset approves 9 deputy speakers, 2 Arab"),
    (39, "EUROPE", "Berlin:", "coalition to cut power tax, cap fuel prices"),
    (40, "EUROPE", "Germany:", "accuses Russia of chemical-weapons breaches"),
    (41, "ASIA", "Seoul:", "court acquits Daegu mayor in martial-law case"),
    (42, "ASIA", "Lahore:", "most polluted big city again, AQI 339"),
    (43, "AMERICAS", "Peru:", "M5.9 quake off the south coast, no damage"),
    (44, "AMERICAS", "Football:", "USA beat Haiti 2–0, reach the semi-finals"),
    (45, "AMERICAS", "NBA:", "Grimes scores 47 as Lakers win ninth straight"),
    (46, "OCEANIA", "Cricket:", "Bancroft says whole team knew of 2018 plot"),
    (47, "EUROPE", "Kerch:", "span down after second-night strike, Kyiv says"),
    (48, "GLOBAL", "Oil:", "Brent falls 1.4% to $91.82 a barrel"),
]

NUMBERS = [
    ("141", "Russian drones fired at Ukraine"),
    ("126", "of them downed, Kyiv says"),
    ("2,230", "Sudan civilians killed in 2026 — UN"),
    ("204,070", "people Odisha readies to move"),
    ("25.9bn km", "Voyager 1 from Earth, one light-day"),
    ("$3,792", "gold per ounce, a one-year low"),
]

DATE_CHECK = (
    "DATE CHECK — LEFT OUT ON PURPOSE: DR Congo's Ebola count passing "
    "11,000, Nvidia's $115.8bn quarter and the US measles ruling were all "
    "reported on Tuesday 17 Nov, not today. The Qeshm strike (Tuesday "
    "night) appears only as the cause of today's Iranian drones."
)

FOOTER = (
    "Every story happened, or was first reported, on Wednesday 18 November "
    "2026. Disputed claims are attributed to those who made them.   "
    "Sources: Reuters · AP · AFP · BBC · Al Jazeera · Anadolu · ONS · IMD · "
    "NASA · ECDC · UN · Amnesty.   Original drawings."
)


# ------------------------------------------------------------- illustrations
def _box(d, x, y, w, h, fill):
    d.rectangle([x, y, x + w, y + h], fill=fill)


def illo_gulf(d, x, y, w, h):
    _box(d, x, y, w, h, (168, 198, 214))
    d.polygon([(x, y), (x + w, y), (x + w, y + h * 0.30), (x + w * 0.45, y + h * 0.42),
               (x + w * 0.2, y + h * 0.30), (x, y + h * 0.36)], fill=(216, 196, 152))
    d.polygon([(x, y + h), (x, y + h * 0.62), (x + w * 0.34, y + h * 0.52),
               (x + w * 0.62, y + h * 0.66), (x + w * 0.8, y + h), ], fill=(216, 196, 152))
    for fx, fy in [(0.30, 0.44), (0.52, 0.60)]:
        cx, cy = x + w * fx, y + h * fy
        for a in range(0, 360, 45):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([cx - dx * 3, cy - dy * 3, cx + dx * 6, cy + dy * 6], fill=RED, width=2)
    for t in (0.25, 0.5, 0.75):
        sx, sy = x + w * 0.78, y + h * 0.16
        ex, ey = x + w * (0.30 + 0.22 * (t - 0.25)), y + h * (0.44 + 0.16 * (t - 0.25))
        mx, my = (sx + ex) / 2, min(sy, ey) - h * 0.12
        pts = []
        for i in range(13):
            u = i / 12
            pts.append(((1 - u) ** 2 * sx + 2 * (1 - u) * u * mx + u * u * ex,
                        (1 - u) ** 2 * sy + 2 * (1 - u) * u * my + u * u * ey))
        d.line(pts, fill=RED, width=2)


def illo_shenzhen(d, x, y, w, h):
    _box(d, x, y, w, h, (58, 74, 110))
    d.ellipse([x + w * 0.82, y + h * 0.08, x + w * 0.94, y + h * 0.34], fill=(240, 200, 90))
    base = y + h * 0.92
    for bx, bw, bh in [(0.04, 0.10, 0.42), (0.16, 0.08, 0.58), (0.26, 0.12, 0.36),
                       (0.62, 0.09, 0.5), (0.73, 0.13, 0.33), (0.88, 0.08, 0.46)]:
        _box(d, x + w * bx, base - h * bh, w * bw, h * bh, (30, 40, 62))
    for px, col in [(0.44, (204, 40, 40)), (0.52, (60, 90, 180)), (0.60, (204, 40, 40))]:
        fx = x + w * px
        d.line([fx, base, fx, y + h * 0.18], fill=(230, 228, 220), width=2)
        d.polygon([(fx, y + h * 0.18), (fx + w * 0.055, y + h * 0.235), (fx, y + h * 0.29)], fill=col)
    _box(d, x, base, w, y + h - base, (24, 32, 50))


def illo_alaska(d, x, y, w, h):
    _box(d, x, y, w, h, (38, 54, 84))
    cx, base = x + w * 0.30, y + h * 0.94
    d.rectangle([cx - w * 0.16, base - h * 0.34, cx + w * 0.16, base], fill=(226, 228, 232))
    d.polygon([(cx - w * 0.19, base - h * 0.34), (cx + w * 0.19, base - h * 0.34),
               (cx, base - h * 0.52)], fill=(226, 228, 232))
    d.ellipse([cx - w * 0.055, base - h * 0.66, cx + w * 0.055, base - h * 0.44], fill=(226, 228, 232))
    d.rectangle([cx - w * 0.012, base - h * 0.78, cx + w * 0.012, base - h * 0.64], fill=(226, 228, 232))
    ak = [(0.58, 0.62), (0.66, 0.5), (0.78, 0.46), (0.9, 0.52), (0.94, 0.64),
          (0.86, 0.7), (0.88, 0.8), (0.8, 0.78), (0.76, 0.88), (0.7, 0.8),
          (0.62, 0.84), (0.56, 0.72)]
    d.polygon([(x + w * a, y + h * b) for a, b in ak], fill=(88, 140, 190))
    d.ellipse([x + w * 0.68, y + h * 0.56, x + w * 0.72, y + h * 0.64], fill=RED)


def _drone(d, cx, cy, s, col):
    d.line([cx - s, cy - s * 0.6, cx + s, cy + s * 0.6], fill=col, width=2)
    d.line([cx - s, cy + s * 0.6, cx + s, cy - s * 0.6], fill=col, width=2)
    d.ellipse([cx - s * 0.28, cy - s * 0.28, cx + s * 0.28, cy + s * 0.28], fill=col)


def illo_drones(d, x, y, w, h):
    _box(d, x, y, w, h, (26, 32, 52))
    d.ellipse([x + w * 0.84, y + h * 0.08, x + w * 0.93, y + h * 0.3], fill=(232, 230, 214))
    for fx, fy, s in [(0.2, 0.3, 9), (0.38, 0.2, 7), (0.55, 0.38, 10), (0.7, 0.24, 7), (0.3, 0.52, 6)]:
        _drone(d, x + w * fx, y + h * fy, s, (200, 205, 215))
    d.line([x, y + h * 0.86, x + w, y + h * 0.86], fill=(90, 100, 80), width=3)
    for fx in (0.12, 0.47, 0.8):
        cx, cy = x + w * fx, y + h * 0.8
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(240, 160, 60))


def illo_gaza(d, x, y, w, h):
    _box(d, x, y, w, h, (196, 178, 150))
    base = y + h * 0.9
    for i, fx in enumerate((0.08, 0.3, 0.52, 0.74)):
        tw, th = w * 0.2, h * (0.38 if i % 2 == 0 else 0.3)
        d.polygon([(x + w * fx, base), (x + w * fx + tw / 2, base - th),
                   (x + w * fx + tw, base)], fill=(228, 222, 206), outline=(88, 80, 64))
    fx = x + w * 0.9
    d.line([fx, base, fx, y + h * 0.16], fill=INK, width=2)
    d.polygon([(fx, y + h * 0.16), (fx + w * 0.07, y + h * 0.22), (fx, y + h * 0.28)], fill=(46, 110, 70))
    _box(d, x, base, w, y + h - base, (150, 132, 104))


def illo_akvan(d, x, y, w, h):
    _box(d, x, y, w, h, (120, 170, 196))
    cx, cy, r = x + w * 0.36, y + h * 0.52, h * 0.3
    for k in range(5):
        rr = r * (1 - k * 0.17)
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=k * 55, end=k * 55 + 250,
              fill=(240, 244, 246), width=3)
    d.polygon([(x + w * 0.66, y + h), (x + w * 0.78, y + h * 0.3), (x + w * 0.9, y + h * 0.42),
               (x + w, y + h * 0.36), (x + w, y + h)], fill=(216, 196, 152))
    px, py = x + w * 0.86, y + h * 0.34
    d.line([px, py + h * 0.3, px, py], fill=(80, 90, 60), width=3)
    for a in (-50, -15, 20, 55):
        d.line([px, py, px + math.cos(math.radians(a)) * w * 0.07,
                py - abs(math.sin(math.radians(a))) * h * 0.16 - 2], fill=(80, 110, 70), width=3)


def illo_uk(d, x, y, w, h):
    _box(d, x, y, w, h, (232, 226, 210))
    px, py, pw, ph = x + w * 0.1, y + h * 0.18, w * 0.2, h * 0.62
    d.rounded_rectangle([px, py, px + pw, py + ph], 4, fill=(52, 58, 70))
    d.rectangle([px + pw * 0.2, py + ph * 0.14, px + pw * 0.8, py + ph * 0.4], fill=(240, 200, 90))
    gx, gy = x + w * 0.42, y + h * 0.82
    pts = [(gx, gy), (gx + w * 0.14, gy - h * 0.16), (gx + w * 0.26, gy - h * 0.1),
           (gx + w * 0.4, gy - h * 0.34), (gx + w * 0.5, gy - h * 0.52)]
    d.line(pts, fill=RED, width=3)
    hx, hy = pts[-1]
    d.polygon([(hx, hy), (hx - 9, hy + 1), (hx - 2, hy + 8)], fill=RED)
    d.line([gx, gy, gx + w * 0.54, gy], fill=FAINT, width=1)


def illo_sudan(d, x, y, w, h):
    _box(d, x, y, w, h, (222, 200, 158))
    blob = [(0.3, 0.14), (0.52, 0.08), (0.68, 0.2), (0.72, 0.42), (0.62, 0.58),
            (0.66, 0.8), (0.5, 0.9), (0.34, 0.78), (0.24, 0.52), (0.26, 0.3)]
    d.polygon([(x + w * a, y + h * b) for a, b in blob], fill=(206, 176, 122), outline=(150, 124, 80))
    px, py = x + w * 0.46, y + h * 0.52
    d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED)
    d.line([px, py + 5, px, py + 13], fill=RED, width=2)
    _drone(d, x + w * 0.8, y + h * 0.24, 7, (70, 70, 76))


def illo_gta(d, x, y, w, h):
    _box(d, x, y, w, h, (30, 30, 48))
    d.ellipse([x + w * 0.8, y + h * 0.1, x + w * 0.9, y + h * 0.32], fill=(235, 233, 210))
    cx, cy = x + w * 0.4, y + h * 0.56
    d.rounded_rectangle([cx - w * 0.24, cy - h * 0.2, cx + w * 0.24, cy + h * 0.2], 12,
                        fill=(52, 54, 74), outline=(150, 155, 175))
    d.ellipse([cx - w * 0.17, cy - h * 0.05, cx - w * 0.1, cy + h * 0.06], fill=(200, 200, 215))
    for dx, dy, col in [(0.13, -0.06, (220, 90, 90)), (0.18, 0.0, (90, 200, 120)),
                       (0.13, 0.06, (90, 140, 230)), (0.08, 0.0, (240, 200, 90))]:
        d.ellipse([cx + w * dx - 3, cy + h * dy - 3, cx + w * dx + 3, cy + h * dy + 3], fill=col)
    gx, gy = x + w * 0.78, y + h * 0.62
    d.ellipse([gx - 11, gy - 11, gx + 11, gy + 11], outline=(230, 230, 220), width=2)
    d.line([gx, gy, gx, gy - 8], fill=(230, 230, 220), width=2)
    d.line([gx, gy, gx + 6, gy + 3], fill=(230, 230, 220), width=2)


def illo_ecdc(d, x, y, w, h):
    _box(d, x, y, w, h, (226, 234, 228))
    cx, cy = x + w * 0.3, y + h * 0.52
    d.rounded_rectangle([cx - w * 0.2, cy - h * 0.13, cx + w * 0.02, cy + h * 0.13], 10, fill=(200, 70, 60))
    d.rounded_rectangle([cx + w * 0.02, cy - h * 0.13, cx + w * 0.2, cy + h * 0.13], 10, fill=(240, 240, 244))
    d.line([cx + w * 0.02, cy - h * 0.13, cx + w * 0.02, cy + h * 0.13], fill=(150, 150, 155), width=2)
    for fx, fy in [(0.62, 0.3), (0.74, 0.55), (0.6, 0.74)]:
        bx, by = x + w * fx, y + h * fy
        d.ellipse([bx - 9, by - 5, bx + 9, by + 5], fill=(90, 150, 90))
        for a in range(0, 360, 60):
            d.line([bx, by, bx + math.cos(math.radians(a)) * 12, by + math.sin(math.radians(a)) * 8],
                   fill=(90, 150, 90), width=1)
    ax, ay = x + w * 0.88, y + h * 0.3
    d.line([ax, ay + 12, ax, ay - 12], fill=RED, width=3)
    d.polygon([(ax, ay - 16), (ax - 5, ay - 6), (ax + 5, ay - 6)], fill=RED)


def illo_cop31(d, x, y, w, h):
    _box(d, x, y, w, h, (206, 226, 238))
    cx, cy, r = x + w * 0.34, y + h * 0.52, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(96, 160, 110))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 320, fill=(70, 130, 190), width=5)
    d.arc([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], 90, 270, fill=(240, 244, 240), width=1)
    d.line([cx - r, cy, cx + r, cy], fill=(240, 244, 240), width=1)
    tx = x + w * 0.72
    d.rounded_rectangle([tx - 5, y + h * 0.3, tx + 5, y + h * 0.74], 5, fill=(240, 244, 246), outline=FAINT)
    d.ellipse([tx - 10, y + h * 0.68, tx + 10, y + h * 0.9], fill=RED)
    d.rectangle([tx - 2, y + h * 0.74, tx + 2, y + h * 0.8], fill=RED)


def illo_dhaka(d, x, y, w, h):
    _box(d, x, y, w, h, (216, 206, 188))
    base = y + h * 0.88
    _box(d, x + w * 0.14, base - h * 0.52, w * 0.44, h * 0.52, (150, 146, 140))
    for r_ in range(3):
        for c_ in range(4):
            _box(d, x + w * (0.18 + c_ * 0.1), base - h * (0.44 - r_ * 0.13), w * 0.06, h * 0.08, (240, 210, 120))
    for fx in (0.64, 0.74):
        _box(d, x + w * fx, base - h * 0.66, w * 0.05, h * 0.66, (120, 116, 110))
        d.ellipse([x + w * fx - 3, base - h * 0.8, x + w * fx + w * 0.07, base - h * 0.64], fill=(190, 188, 182))
    for i in range(9):
        hx = x + w * (0.1 + i * 0.1)
        d.ellipse([hx - 2.5, base + 1, hx + 2.5, base + 5], fill=(70, 66, 60))
    if y + h - base - 6 > 0:
        _box(d, x, base + 6, w, y + h - base - 6, (170, 158, 138))


def illo_voyager(d, x, y, w, h):
    _box(d, x, y, w, h, (8, 10, 24))
    for fx, fy in [(0.1, 0.2), (0.3, 0.7), (0.55, 0.15), (0.7, 0.6), (0.9, 0.3), (0.45, 0.85), (0.85, 0.85)]:
        d.ellipse([x + w * fx, y + h * fy, x + w * fx + 2, y + h * fy + 2], fill=(230, 232, 240))
    ex, ey = x + w * 0.1, y + h * 0.5
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(90, 150, 230))
    px, py = x + w * 0.78, y + h * 0.44
    for i in range(1, 9):
        u = i / 9
        d.ellipse([ex + (px - ex) * u - 1, ey + (py - ey) * u - 1,
                   ex + (px - ex) * u + 1, ey + (py - ey) * u + 1], fill=(200, 205, 220))
    d.arc([px - 13, py - 13, px + 13, py + 13], 110, 250, fill=(225, 228, 235), width=3)
    d.line([px, py, px - 12, py + 10], fill=(225, 228, 235), width=2)
    d.line([px - 12, py + 10, px + 4, py + 12], fill=(225, 228, 235), width=2)


def illo_eu(d, x, y, w, h):
    _box(d, x, y, w, h, (32, 62, 124))
    cx, cy, r = x + w * 0.3, y + h * 0.52, h * 0.3
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.polygon([(sx, sy - 4), (sx + 3, sy + 3), (sx - 3, sy + 3)], fill=(245, 200, 70))
    fnt = font(SERIF_B, int(h * 0.52))
    d.text((x + w * 0.58, y + h * 0.2), "€45bn", font=fnt, fill=(245, 200, 70))


ILLOS = {"gulf": illo_gulf, "shenzhen": illo_shenzhen, "alaska": illo_alaska,
         "drones": illo_drones, "gaza": illo_gaza, "akvan": illo_akvan,
         "uk": illo_uk, "sudan": illo_sudan, "gta": illo_gta, "ecdc": illo_ecdc,
         "cop31": illo_cop31, "dhaka": illo_dhaka, "voyager": illo_voyager,
         "eu": illo_eu}

# ------------------------------------------------------------- world map
# Land spans on a 104 x 40 grid: row -> [(first col, last col), ...]
MAP_ROWS = {
    0: [(6, 17), (37, 45), (58, 63), (68, 72), (78, 84), (90, 96)],
    1: [(3, 10), (12, 24), (38, 44), (54, 57), (59, 100)],
    2: [(2, 11), (13, 28), (39, 43), (47, 47), (54, 58), (59, 100)],
    3: [(2, 10), (14, 30), (40, 42), (52, 60), (61, 99)],
    4: [(4, 8), (15, 31), (50, 51), (53, 62), (63, 98)],
    5: [(16, 32), (50, 50), (52, 63), (64, 97)],
    6: [(17, 31), (50, 62), (63, 95)],
    7: [(16, 30), (49, 60), (61, 93), (94, 95)],
    8: [(17, 30), (48, 58), (62, 72), (74, 90), (92, 94)],
    9: [(17, 29), (49, 58), (62, 74), (75, 89)],
    10: [(16, 29), (47, 56), (57, 63), (73, 88), (90, 92)],
    11: [(16, 28), (46, 56), (57, 64), (65, 72), (74, 87)],
    12: [(15, 26), (44, 58), (59, 63), (68, 74), (76, 85)],
    13: [(14, 24), (43, 58), (59, 62), (68, 73), (77, 82)],
    14: [(14, 22), (42, 57), (59, 61), (68, 72), (77, 81), (84, 86)],
    15: [(15, 19), (41, 56), (59, 60), (68, 71), (77, 80), (84, 85)],
    16: [(40, 54), (59, 60), (69, 70), (78, 80), (84, 84)],
    17: [(32, 37), (39, 53), (77, 80), (82, 88)],
    18: [(31, 38), (38, 52), (69, 69), (77, 79), (81, 90)],
    19: [(30, 37), (44, 50), (56, 60), (80, 92), (93, 95)],
    20: [(30, 36), (45, 49), (59, 59), (81, 93), (94, 96)],
    21: [(29, 37), (45, 50), (82, 90)],
    22: [(29, 38), (46, 51), (83, 89)],
    23: [(29, 38), (46, 51)],
    24: [(28, 38), (46, 52), (55, 56), (85, 93)],
    25: [(28, 37), (47, 52), (55, 55), (85, 95)],
    26: [(28, 37), (47, 52), (55, 55), (84, 96)],
    27: [(29, 36), (47, 51), (85, 95)],
    28: [(29, 36), (47, 51), (86, 94)],
    29: [(30, 35), (48, 50), (87, 93)],
    30: [(30, 35), (48, 50), (88, 92)],
    31: [(30, 34), (48, 49), (88, 91), (100, 102)],
    32: [(30, 34), (100, 102)],
    33: [(31, 33), (100, 101)],
    34: [(31, 33)],
    35: [(31, 32)],
    36: [(31, 32)],
}


# ------------------------------------------------------------------ layout
M = 14
CW = W - 2 * M


def draw_card(d, card, x, y, w, h, illo_h, cap_h, kick_size, head_size,
              head_lh, deck_size, deck_lh, head_lines_max=3):
    num, region, beat, illo, caption, headline, deck, _lon, _lat = card
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=LINE)
    pad = 7
    iw = w - 2
    ILLOS[illo](d, x + 1, y + 1, iw, illo_h - cap_h)
    if cap_h:
        cy = y + 1 + illo_h - cap_h
        d.rectangle([x + 1, cy, x + 1 + iw, y + illo_h], fill=NAVY)
        cf = fit(d, caption, SANS_B, 9, iw - 8, 7)
        d.text((x + 5, cy + 1), caption, font=cf, fill=(240, 238, 230))
    r = 10
    bx, by = x + 11, y + 11
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=RED)
    nf = font(SANS_B, 12)
    nw = text_w(d, str(num), nf)
    d.text((bx - nw / 2, by - 8), str(num), font=nf, fill=(255, 255, 255))
    ty = y + illo_h + 4
    kf = font(SANS_B, kick_size)
    d.text((x + pad, ty), f"{region} · {beat}", font=kf,
           fill=REGION_COLORS.get(region, INK))
    ty += kick_size + 4
    hf = font(SERIF_B, head_size)
    for ln in wrap(d, headline, hf, w - 2 * pad)[:head_lines_max]:
        d.text((x + pad, ty), ln, font=hf, fill=INK)
        ty += head_lh
    ty += 2
    size = deck_size
    while size > 8:
        df = font(SANS, size)
        lines = wrap(d, deck, df, w - 2 * pad)
        if len(lines) * deck_lh <= y + h - ty - 3:
            break
        size -= 0.5
    df = font(SANS, size)
    for ln in wrap(d, deck, df, w - 2 * pad):
        if ty + deck_lh > y + h - 2:
            break
        d.text((x + pad, ty), ln, font=df, fill=(58, 60, 66))
        ty += deck_lh


def draw_map(d, x, y, w, h):
    cols, rows = 104, 40
    dx, dy = w / cols, h / rows
    land = (110, 128, 148)
    for r_, spans in MAP_ROWS.items():
        for a, b in spans:
            for c in range(a, b + 1):
                cx, cy = x + (c + 0.5) * dx, y + (r_ + 0.5) * dy
                d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], fill=land)
    for card in CARDS:
        num, _r, _b, _i, _c, _h, _dk, lon, lat = card
        if lon is None:
            continue
        px = x + (lon + 180) / 360 * w
        py = y + (76 - lat) / 136 * h
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=(255, 255, 255))
        nf = font(SANS_B, 8)
        s = str(num)
        d.text((px - text_w(d, s, nf) / 2, py - 5), s, font=nf, fill=(255, 255, 255))
    ax, ay = x + w - 118, y + 12
    d.line([ax, ay, ax + 34, ay - 6], fill=FAINT, width=1)
    tf = font(SANS, 8)
    d.text((ax + 36, ay - 9), "13 · to Voyager 1", font=tf, fill=FAINT)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(CARDS) + len(BRIEFS)
    # top strip
    lf = font(SANS_B, 13)
    d.text((M, 10), "THE DAY IN WORLD NEWS", font=lf, fill=INK)
    right = f"{total} STORIES · 6 CONTINENTS · ONE DAY"
    d.text((W - M - text_w(d, right, lf), 10), right, font=lf, fill=INK)
    # masthead
    mf = fit(d, "Wednesday 18 November 2026", SERIF_B, 74, CW, 40)
    d.text((M - 2, 30), "Wednesday 18 November 2026", font=mf, fill=INK)
    d.line([M, 106, W - M, 106], fill=INK, width=2)
    it = "Everything on this page happened, or was first reported, on Wednesday 18 November 2026."
    iff = font(SERIF_I, 14)
    d.text(((W - text_w(d, it, iff)) / 2, 111), it, font=iff, fill=(70, 72, 78))
    # region tally band (computed from the data)
    tally_order = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "GLOBAL"]
    counts = {k: 0 for k in tally_order}
    for c in CARDS:
        counts["GLOBAL" if c[1] == "SPACE" else c[1]] += 1
    for b in BRIEFS:
        counts[b[1]] += 1
    tally = "   ·   ".join(f"{k} {counts[k]}" for k in tally_order)
    d.rectangle([M, 134, W - M, 158], fill=NAVY)
    tf = fit(d, tally, SANS_B, 13, CW - 20, 9)
    d.text(((W - text_w(d, tally, tf)) / 2, 139), tally, font=tf, fill=(242, 240, 232))
    # cards
    y = 166
    row_a = CARDS[:3]
    w_a = (CW - 24) // 3
    for i, c in enumerate(row_a):
        draw_card(d, c, M + i * (w_a + 12), y, w_a, 200, 84, 13, 11, 19, 22, 11.5, 14)
    y += 208
    row_b = CARDS[3:8]
    w_b = (CW - 40) // 5
    for i, c in enumerate(row_b):
        draw_card(d, c, M + i * (w_b + 10), y, w_b, 152, 46, 11, 9.5, 14, 16, 10, 12.5)
    y += 160
    row_c = CARDS[8:]
    w_c = (CW - 45) // 6
    for i, c in enumerate(row_c):
        draw_card(d, c, M + i * (w_c + 9), y, w_c, 140, 38, 0, 9, 13, 15, 9.3, 11.5)
    y += 148
    # numbers + date check band
    d.line([M, y, W - M, y], fill=INK, width=1)
    nf_title = font(SANS_B, 11)
    d.text((M, y + 5), "WEDNESDAY BY THE NUMBERS", font=nf_title, fill=RED)
    cell_w = 100
    for i, (big, small) in enumerate(NUMBERS):
        cx = M + i * cell_w
        bf = fit(d, big, SERIF_B, 17, cell_w - 4, 11)
        d.text((cx, y + 20), big, font=bf, fill=INK)
        sf = font(SANS, 8.6)
        for j, ln in enumerate(wrap(d, small, sf, cell_w - 6)[:2]):
            d.text((cx, y + 42 + j * 10), ln, font=sf, fill=(70, 72, 78))
    dc_x = M + 612
    d.rectangle([dc_x, y + 4, W - M, y + 66], fill=(250, 233, 213), outline=(206, 170, 120))
    dcf = font(SANS, 9.6)
    ty = y + 8
    for ln in wrap(d, DATE_CHECK, dcf, W - M - dc_x - 12):
        d.text((dc_x + 6, ty), ln, font=dcf, fill=(90, 52, 30))
        ty += 11.5
    y += 74
    # bottom zone: map left, briefs right
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 6
    mf_title = font(SANS_B, 11.5)
    d.text((M, y), "WHERE IT HAPPENED — PINS MATCH THE NUMBERED CARDS", font=mf_title, fill=INK)
    draw_map(d, M, y + 18, 404, 178)
    lg = font(SANS, 9)
    d.text((M, y + 200), "Red pins: stories 1–14 above. Voyager 1 (13) is off the map,", font=lg, fill=FAINT)
    d.text((M, y + 212), "in deep space. Hairlines are guides, not borders.", font=lg, fill=FAINT)
    bx = M + 428
    d.text((bx, y), f"ALSO ON WEDNESDAY — {len(BRIEFS)} MORE STORIES IN BRIEF", font=mf_title, fill=INK)
    col_w = (W - M - bx - 12) // 2
    per_col = (len(BRIEFS) + 1) // 2
    bf = font(SANS, 10.3)
    bfb = font(SANS_B, 10.3)
    lh = 13.1
    for idx, (num, region, lead, rest) in enumerate(BRIEFS):
        col = idx // per_col
        row = idx % per_col
        x0 = bx + col * (col_w + 12)
        y0 = y + 18 + row * lh
        colr = REGION_COLORS.get(region, INK)
        s_num = f"{num} "
        d.text((x0, y0), s_num, font=bfb, fill=colr)
        x1 = x0 + text_w(d, s_num, bfb)
        d.text((x1, y0), lead + " ", font=bfb, fill=INK)
        x2 = x1 + text_w(d, lead + " ", bfb)
        size = 10.3
        rf = bf
        while size > 8.6 and x2 + text_w(d, rest, rf) > x0 + col_w:
            size -= 0.4
            rf = font(SANS, size)
        d.text((x2, y0), rest, font=rf, fill=(40, 42, 48))
    # footer
    ff = fit(d, FOOTER, SANS, 9.2, CW, 7.5)
    d.text(((W - text_w(d, FOOTER, ff)) / 2, H - 16), FOOTER, font=ff, fill=FAINT)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    print("stories:", total, "| bytes:", os.path.getsize(out), "| ->", out)


if __name__ == "__main__":
    main()
