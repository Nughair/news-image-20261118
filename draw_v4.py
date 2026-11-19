#!/usr/bin/env python3
"""Generator for the v4 entry image: one page summing up the world news
of Wednesday 18 November 2026, drawn with Pillow.

Layout, in the broadsheet family the live board rewards: a big date
masthead, a computed region tally, a by-the-numbers strip, 15 numbered
illustrated cards, a dotted world map with a pin for every card, 35
numbered one-line briefs, a DATE CHECK box naming the tempting stories
left out because they belong to Tuesday (or to Thursday/Friday), and a
sources footer. 50 stories in all.

Story selection follows tonight's live top of the board (eager-badger-82,
alim3596, kevin — fetched and read before this build) cross-checked
against the v3 sourcing notes. Two changes of discipline versus v3,
both dictated by those leaders' DATE CHECK boxes: the Alaska Senate
call and the Board of Peace Gaza warning are treated as Tuesday
stories and excluded (named in the DATE CHECK box), and the Dow's
Tuesday fall is replaced by Wednesday's Fed minutes (Dow -561).
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)
INK = (20, 32, 48)
NAVY = (18, 38, 63)
RED = (179, 53, 44)
GOLD = (176, 141, 42)
GREY = (96, 104, 112)
CARD_BG = (253, 251, 245)
HAIR = (203, 194, 175)

REGIONS = {
    "EUROPE": (46, 95, 138),
    "MIDDLE EAST": (179, 53, 44),
    "ASIA": (122, 79, 157),
    "AFRICA": (199, 123, 41),
    "AMERICAS": (46, 125, 91),
    "OCEANIA": (42, 157, 143),
    "WORLD": (90, 100, 114),
}

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, width):
    """Greedy word wrap; returns a list of lines that fit width."""
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if tw(d, trial, font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_size(d, text, path, width, start, floor=8):
    size = start
    while size > floor and tw(d, text, F(path, size)) > width:
        size -= 1
    return size


# ---------------------------------------------------------------- stories

# num, region, beat, headline, deck, scene, source tag
CARDS = [
    (1, "ASIA", "APEC SUMMIT",
     "Xi greets Trump on the tarmac in Shenzhen",
     "A rare airport honour as APEC opens; Putin joins the banquet. "
     "The three-way talks with Xi are set for Thursday.",
     "tarmac", "CONFIRMED · AP"),
    (2, "MIDDLE EAST", "IRAN WAR",
     "Kuwait and Bahrain intercept Iran's drones",
     "Iran says it aimed at US forces at Ali Al Salem, after "
     "Tuesday's US strike on Qeshm. CENTCOM reports no casualties.",
     "gulf", "CLAIM · REUTERS"),
    (3, "WORLD", "SPACE",
     "Voyager 1 reaches one light-day from Earth",
     "NASA's 1977 probe is the first craft 25.9 billion km out: a "
     "radio command sent today arrives tomorrow.",
     "voyager", "CONFIRMED · NASA"),
    (4, "EUROPE", "UKRAINE WAR",
     "Russia fires 141 drones at Ukraine; 126 downed",
     "Kyiv counts 126 downed; officials report five killed and 15 "
     "injured, power cut across Rivne region.",
     "drones", "KYIV"),
    (5, "AMERICAS", "MARKETS",
     "Fed minutes: almost all officials back more hikes",
     "A bigger December rise is floated; the Dow falls 561 points "
     "(−1.1%) while the Nasdaq edges up 0.4%.",
     "fed", "FED"),
    (6, "MIDDLE EAST", "GAZA",
     "Israeli tanks push into central Gaza near Nuseirat",
     "The first ground push since the truce; the army says it is "
     "destroying a tunnel. Three killed, medics say.",
     "gaza", "REUTERS"),
    (7, "ASIA", "WEATHER",
     "Cyclone Akvan veers north toward Odisha",
     "Nearly 50,000 people are moved to shelters as the storm nears "
     "the coast; landfall is due on Friday.",
     "akvan", "IMD"),
    (8, "AFRICA", "SUDAN WAR",
     "Amnesty: RSF drones killed 37 in El Obeid",
     "The group urges a war-crimes inquiry; the RSF blames Sudan's "
     "army for the deaths.",
     "elobeid", "AMNESTY"),
    (9, "EUROPE", "UKRAINE AID",
     "EU proposes a €45bn loan for Ukraine",
     "Two-thirds of a €70bn gap for 2027, repaid only once Russia "
     "pays reparations.",
     "eu", "EU"),
    (10, "EUROPE", "ECONOMY",
     "UK inflation climbs to 3.6%, a one-year high",
     "Fuel and a tobacco duty rise push October CPI up from 3.5%.",
     "uk", "ONS"),
    (11, "AMERICAS", "US POLITICS",
     "Jeffries wins the Speaker nod",
     "A 251–11 caucus vote; on course to be the first Black Speaker "
     "when the House votes on 3 January.",
     "jeffries", "NPR"),
    (12, "WORLD", "CULTURE",
     "GTA VI goes on sale after a 13-year wait",
     "New Zealand plays first at midnight; 14.9m digital pre-orders "
     "banked.",
     "gta", "ROCKSTAR"),
    (13, "ASIA", "LABOUR",
     "Bangladesh protests shut 55 factories",
     "Police tear-gas garment workers blocking a highway over pay; "
     "about 300 arrests.",
     "dhaka", "DHAKA"),
    (14, "AMERICAS", "BUSINESS",
     "Anthropic prices a record $81.3bn IPO",
     "Shares at $83, above the range — the biggest listing ever. "
     "Trading starts Thursday.",
     "ipo", "AL JAZEERA"),
    (15, "WORLD", "CLIMATE",
     "COP31 splits over fossil-fuel draft",
     "Arab states and Russia reject the text; a '35 by 35' power "
     "goal wins 75 backers. Friday deadline.",
     "cop31", "AFP · AGENCIES"),
]

# num, place lead-in, text, region
BRIEFS = [
    (16, "Manila", "Trump hails a 'biggest' trade deal; Manila disputes it", "ASIA"),
    (17, "Tokyo", "Takaichi makes her first China visit as prime minister", "ASIA"),
    (18, "Ottawa", "Carney and Xi agree tariff relief on pork and seafood", "AMERICAS"),
    (19, "Seoul", "Lee seeks Xi's help on peace with the North", "ASIA"),
    (20, "Riyadh", "the coalition downs a Houthi cruise missile", "MIDDLE EAST"),
    (21, "Berlin", "Germany pledges air defences and F-16 ammo to Kyiv", "EUROPE"),
    (22, "The Hague", "a court gives ex-president Thaçi 17 months", "EUROPE"),
    (23, "Kemerovo", "19 die in an An-12 plane crash, media say", "ASIA"),
    (24, "Kinshasa", "WHO keeps Ebola a global emergency at 11,300 cases", "AFRICA"),
    (25, "Badme", "Ethiopia and Eritrea trade artillery fire", "AFRICA"),
    (26, "Khartoum", "the UN counts 2,230 Sudan civilians killed this year", "AFRICA"),
    (27, "Maputo", "opposition leader Mondlane goes on trial", "AFRICA"),
    (28, "Conakry", "Guinea jails 224 over illegal gold mining", "AFRICA"),
    (29, "Pretoria", "inflation rises to 5.2%, the highest since 2024", "AFRICA"),
    (30, "Gaza", "floods deepen; WHO urges open aid routes", "MIDDLE EAST"),
    (31, "Canberra", "Australia sanctions settler leader Daniella Weiss", "OCEANIA"),
    (32, "Sydney", "Tame Impala sweeps seven ARIA Music Awards", "OCEANIA"),
    (33, "Port Moresby", "a magnitude 6.0 quake strikes PNG", "OCEANIA"),
    (34, "Avarua", "Cyclone Xavier reaches Category 5, turns east", "OCEANIA"),
    (35, "Wellington", "tsunami advisory lifted after 60 cm surges", "OCEANIA"),
    (36, "Caracas", "Hegseth's surprise visit seals a defence pact", "AMERICAS"),
    (37, "Bogotá", "the economy shrinks 0.8% in the third quarter", "AMERICAS"),
    (38, "Brasília", "the Senate passes Lula's $10bn fiscal package", "AMERICAS"),
    (39, "Lima", "the Tumbes River passes its red-alert level", "AMERICAS"),
    (40, "Turin", "Alcaraz beats Medvedev 6–2, 6–4 at the Finals", "EUROPE"),
    (41, "Los Angeles", "Grimes scores 47 as the Lakers win a ninth straight", "AMERICAS"),
    (42, "New York", "USA beat Haiti 2–0, reach the Nations League semis", "AMERICAS"),
    (43, "Gold", "sinks to $3,792 an ounce, a one-year low", "WORLD"),
    (44, "Naypyidaw", "the junta says ASEAN treated it unfairly", "ASIA"),
    (45, "Paris", "a court suspends the school-protest ban", "EUROPE"),
    (46, "Belgrade", "a Serbian MiG-29 crashes near the capital", "EUROPE"),
    (47, "Port Louis", "Mauritius sets the UK a December Chagos deadline", "AFRICA"),
    (48, "Lahore", "again the world's most polluted big city, AQI 339", "ASIA"),
    (49, "Stockholm", "Europe off track on antibiotic resistance — ECDC", "EUROPE"),
    (50, "Bucharest", "a magnitude 5.3 earthquake shakes Romania", "EUROPE"),
]

NUMBERS = [
    ("141", "Russian drones fired at Ukraine overnight"),
    ("126", "of them downed, Kyiv's air force says"),
    ("25.9bn km", "Voyager 1 from Earth — one light-day out"),
    ("55", "factories shut by Bangladesh wage protests"),
    ("251–11", "the caucus vote that nominates Jeffries"),
    ("$81.3bn", "Anthropic's record IPO pricing"),
]

DATE_CHECK = (
    "Left out on purpose — each first reported on Tuesday 17 November: the US strike on "
    "Qeshm (background to story 2) · Alaska's Senate call · the Kerch Bridge span collapse · "
    "the Knesset speaker vote · Nvidia's $115.8bn results · the Prague train crash · the "
    "Board of Peace's Gaza warning · Ebola passing 11,000 cases. Not yet: the Trump–Xi–Putin "
    "talks (Thu 19) · Anthropic's first trade (Thu 19) · Akvan's landfall (Fri 20) · COP31's "
    "close (Fri 20)."
)

FOOTER = (
    "Sources: Reuters · AP · AFP · BBC · Al Jazeera · CNBC · CNN · ONS · IMD · NASA · "
    "Amnesty · WHO. All 50 stories happened, or were first reported, on Wednesday "
    "18 November 2026; disputed claims are attributed. Original drawings."
)


# ---------------------------------------------------------------- scenes
# Each scene draws inside the box (x, y, w, h) with flat shapes only.

def _sky(d, x, y, w, h, top, bottom):
    steps = 24
    for i in range(steps):
        t = i / steps
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.rectangle([x, y + h * i / steps, x + w, y + h * (i + 1) / steps + 1], fill=c)


def sc_tarmac(d, x, y, w, h):
    _sky(d, x, y, w, h, (126, 168, 205), (232, 214, 178))
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.92, y + h * 0.34], fill=(244, 205, 110))
    for i, bx in enumerate((0.04, 0.20, 0.38, 0.58, 0.74)):
        bh = (0.34, 0.26, 0.42, 0.30, 0.22)[i]
        d.rectangle([x + w * bx, y + h * (0.72 - bh), x + w * (bx + 0.13), y + h * 0.72],
                    fill=(43, 58, 79))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(104, 108, 112))
    d.rectangle([x, y + h * 0.86, x + w, y + h * 0.90], fill=(240, 238, 230))
    d.rectangle([x + w * 0.30, y + h * 0.90, x + w * 0.72, y + h * 0.97], fill=(179, 53, 44))
    for fx, col in ((0.30, (206, 48, 49)), (0.50, (38, 62, 110)), (0.70, (206, 48, 49))):
        d.line([x + w * fx, y + h * 0.30, x + w * fx, y + h * 0.72], fill=(30, 30, 30), width=2)
        d.rectangle([x + w * fx, y + h * 0.30, x + w * (fx + 0.075), y + h * 0.44], fill=col)
    d.polygon([(x + w * 0.86, y + h * 0.52), (x + w * 0.99, y + h * 0.66),
               (x + w * 0.86, y + h * 0.66)], fill=(225, 228, 232))
    d.rectangle([x + w * 0.80, y + h * 0.62, x + w * 0.88, y + h * 0.72], fill=(190, 196, 204))


def sc_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 92, 128))
    land = (222, 198, 152)
    d.polygon([(x, y + h * 0.30), (x + w * 0.30, y + h * 0.22), (x + w * 0.44, y + h * 0.40),
               (x + w * 0.40, y + h * 0.66), (x + w * 0.22, y + h * 0.80), (x, y + h * 0.78)],
              fill=land)
    d.polygon([(x + w * 0.58, y), (x + w, y), (x + w, y + h * 0.30),
               (x + w * 0.78, y + h * 0.36), (x + w * 0.62, y + h * 0.18)], fill=land)
    d.polygon([(x + w * 0.30, y + h), (x + w * 0.44, y + h * 0.78), (x + w * 0.52, y + h),
               ], fill=land)
    for t in (0.25, 0.5, 0.75):
        sx, sy = x + w * 0.66, y + h * 0.12
        ex, ey = x + w * (0.30 + 0.1 * t), y + h * (0.30 + 0.35 * t)
        for s in range(13):
            u = s / 12
            px = sx + (ex - sx) * u
            py = sy + (ey - sy) * u - h * 0.16 * u * (1 - u) * 2
            if s % 2 == 0:
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(255, 220, 120))
    for bx, by in ((0.34, 0.44), (0.42, 0.62)):
        cx, cy = x + w * bx, y + h * by
        for a in range(0, 360, 45):
            import math
            d.line([cx, cy, cx + 7 * math.cos(math.radians(a)), cy + 7 * math.sin(math.radians(a))],
                   fill=(255, 176, 66), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 120, 60))
    d.ellipse([x + w * 0.60, y + h * 0.08, x + w * 0.66, y + h * 0.20], fill=(230, 60, 50))


def sc_voyager(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 14, 30))
    stars = [(0.06, 0.2), (0.16, 0.62), (0.28, 0.14), (0.4, 0.78), (0.52, 0.3),
             (0.63, 0.66), (0.72, 0.16), (0.84, 0.5), (0.93, 0.24), (0.35, 0.44),
             (0.58, 0.86), (0.9, 0.82), (0.22, 0.86), (0.78, 0.34)]
    for sx, sy in stars:
        r = 1.6
        d.ellipse([x + w * sx - r, y + h * sy - r, x + w * sx + r, y + h * sy + r],
                  fill=(235, 238, 245))
    ex, ey = x + w * 0.10, y + h * 0.76
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(84, 138, 205))
    d.ellipse([ex - 7, ey - 3, ex + 1, ey + 4], fill=(96, 178, 120))
    for s in range(26):
        u = s / 25
        px = ex + (w * 0.62) * u
        py = ey - (h * 0.52) * u - h * 0.10 * u * (1 - u)
        if s % 2 == 0:
            d.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4], fill=(240, 203, 110))
    px, py = x + w * 0.74, y + h * 0.22
    d.ellipse([px - 11, py - 11, px + 11, py + 11], outline=(225, 228, 232), width=2)
    d.line([px, py, px + 17, py - 10], fill=(225, 228, 232), width=2)
    d.line([px - 3, py + 3, px - 14, py + 13], fill=(225, 228, 232), width=2)
    d.rectangle([px - 2, py - 16, px + 2, py - 11], fill=(240, 203, 110))
    f = F(SANS_B, 11)
    d.text((x + w * 0.60, y + h * 0.80), "1 LIGHT-DAY", font=f, fill=(240, 203, 110))


def sc_drones(d, x, y, w, h):
    _sky(d, x, y, w, h, (16, 26, 48), (58, 62, 84))
    for i, bx in enumerate((0.0, 0.14, 0.30, 0.47, 0.63, 0.80, 0.92)):
        bh = (0.30, 0.42, 0.26, 0.38, 0.30, 0.44, 0.28)[i]
        d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + 0.13), y + h], fill=(10, 14, 24))
        for wy in (0.78, 0.88):
            d.rectangle([x + w * (bx + 0.04), y + h * wy, x + w * (bx + 0.07), y + h * (wy + 0.04)],
                        fill=(250, 205, 105))
    def drone(cx, cy, s):
        d.line([cx - s, cy - s * 0.5, cx + s, cy + s * 0.5], fill=(200, 208, 220), width=2)
        d.line([cx - s, cy + s * 0.5, cx + s, cy - s * 0.5], fill=(200, 208, 220), width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 90, 70))
    drone(x + w * 0.22, y + h * 0.24, 8)
    drone(x + w * 0.48, y + h * 0.16, 10)
    drone(x + w * 0.72, y + h * 0.30, 7)
    drone(x + w * 0.88, y + h * 0.14, 6)
    import math
    for bx, by in ((0.36, 0.52), (0.62, 0.44)):
        cx, cy = x + w * bx, y + h * by
        for a in range(0, 360, 60):
            d.line([cx, cy, cx + 6 * math.cos(math.radians(a)), cy + 6 * math.sin(math.radians(a))],
                   fill=(255, 176, 66), width=2)


def sc_fed(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 230, 218))
    bx, by, bw = x + w * 0.07, y + h * 0.16, w * 0.44
    d.polygon([(bx, by + h * 0.16), (bx + bw / 2, by), (bx + bw, by + h * 0.16)], fill=(90, 98, 110))
    d.rectangle([bx, by + h * 0.16, bx + bw, by + h * 0.22], fill=(110, 118, 130))
    for i in range(4):
        cx = bx + bw * (0.10 + 0.24 * i)
        d.rectangle([cx, by + h * 0.24, cx + bw * 0.10, by + h * 0.66], fill=(140, 148, 160))
    d.rectangle([bx - 3, by + h * 0.68, bx + bw + 3, by + h * 0.76], fill=(90, 98, 110))
    pts = [(0.56, 0.22), (0.66, 0.34), (0.74, 0.30), (0.84, 0.52), (0.95, 0.68)]
    pp = [(x + w * a, y + h * b) for a, b in pts]
    d.line(pp, fill=(179, 53, 44), width=3)
    d.polygon([(pp[-1][0], pp[-1][1]), (pp[-1][0] - 9, pp[-1][1] - 2), (pp[-1][0] - 2, pp[-1][1] + 8)],
              fill=(179, 53, 44))


def sc_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 205, 164))
    d.rectangle([x, y + h * 0.74, x + w, y + h], fill=(198, 168, 118))
    for i in range(9):
        d.line([x + w * (0.55 + 0.045 * i), y, x + w * (0.55 + 0.045 * i), y + h * 0.16],
               fill=(214, 178, 60), width=2)
    d.line([x + w * 0.55, y + h * 0.16, x + w * 0.97, y + h * 0.16], fill=(214, 178, 60), width=2)
    tx, ty = x + w * 0.14, y + h * 0.52
    d.rounded_rectangle([tx, ty, tx + w * 0.34, ty + h * 0.20], 5, fill=(96, 100, 96))
    d.rectangle([tx + w * 0.10, ty - h * 0.12, tx + w * 0.22, ty + 2], fill=(84, 88, 84))
    d.line([tx + w * 0.20, ty - h * 0.08, tx + w * 0.46, ty - h * 0.16], fill=(70, 74, 70), width=4)
    for i in range(4):
        cx = tx + w * (0.05 + 0.085 * i)
        d.ellipse([cx, ty + h * 0.17, cx + w * 0.06, ty + h * 0.30], fill=(60, 63, 60))
    for dx, dy in ((0.60, 0.62), (0.70, 0.70), (0.80, 0.58), (0.88, 0.68)):
        d.ellipse([x + w * dx, y + h * dy, x + w * dx + 4, y + h * dy + 3], fill=(170, 140, 96))


def sc_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 116, 138))
    d.polygon([(x + w * 0.78, y), (x + w, y), (x + w, y + h), (x + w * 0.86, y + h),
               (x + w * 0.80, y + h * 0.6), (x + w * 0.88, y + h * 0.35), (x + w * 0.78, y + h * 0.15)],
              fill=(226, 205, 164))
    import math
    cx, cy = x + w * 0.42, y + h * 0.52
    for r, a0 in ((10, 20), (19, 140), (28, 260), (37, 60), (46, 200)):
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], a0, a0 + 250,
              fill=(238, 244, 246), width=3)
    d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=(20, 50, 70))
    for i in range(6):
        rx, ry = x + w * (0.06 + 0.1 * i), y + h * (0.10 + 0.06 * (i % 2))
        d.line([rx, ry, rx - 5, ry + 9], fill=(190, 220, 235), width=2)


def sc_elobeid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 214, 178))
    d.polygon([(x + w * 0.30, y + h * 0.06), (x + w * 0.62, y + h * 0.02), (x + w * 0.74, y + h * 0.26),
               (x + w * 0.66, y + h * 0.48), (x + w * 0.72, y + h * 0.72), (x + w * 0.52, y + h * 0.94),
               (x + w * 0.34, y + h * 0.80), (x + w * 0.22, y + h * 0.44)], fill=(214, 164, 96))
    px, py = x + w * 0.46, y + h * 0.52
    d.polygon([(px, py + 10), (px - 6, py), (px, py - 9), (px + 6, py)], fill=(179, 53, 44))
    d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=(255, 255, 255))
    for dx, dy in ((0.20, 0.2), (0.80, 0.16), (0.68, 0.84)):
        cx, cy = x + w * dx, y + h * dy
        d.line([cx - 5, cy - 3, cx + 5, cy + 3], fill=(90, 80, 60), width=2)
        d.line([cx - 5, cy + 3, cx + 5, cy - 3], fill=(90, 80, 60), width=2)


def sc_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(32, 62, 128))
    import math
    cx, cy, r = x + w * 0.26, y + h * 0.5, h * 0.30
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(250, 205, 80))
    f = F(SERIF_B, 26)
    d.text((x + w * 0.48, y + h * 0.30), "€45bn", font=f, fill=(255, 255, 255))


def sc_uk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 233, 224))
    d.rounded_rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.30, y + h * 0.86], 4,
                        fill=(70, 78, 90))
    d.rectangle([x + w * 0.13, y + h * 0.24, x + w * 0.25, y + h * 0.44], fill=(200, 220, 235))
    d.rectangle([x + w * 0.30, y + h * 0.30, x + w * 0.36, y + h * 0.52], fill=(50, 56, 66))
    pts = [(x + w * a, y + h * b) for a, b in
           ((0.46, 0.70), (0.58, 0.58), (0.68, 0.62), (0.80, 0.38), (0.93, 0.24))]
    d.line(pts, fill=(179, 53, 44), width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 9, pts[-1][1] + 1),
               (pts[-1][0] - 3, pts[-1][1] + 9)], fill=(179, 53, 44))
    f = F(SERIF_B, 15)
    d.text((x + w * 0.60, y + h * 0.76), "3.6%", font=f, fill=(179, 53, 44))


def sc_jeffries(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 40, 66))
    cx = x + w * 0.34
    d.polygon([(cx - w * 0.16, y + h * 0.52), (cx, y + h * 0.16), (cx + w * 0.16, y + h * 0.52)],
              fill=(228, 230, 234))
    d.rectangle([cx - w * 0.20, y + h * 0.52, cx + w * 0.20, y + h * 0.60], fill=(210, 213, 218))
    for i in range(5):
        cxx = cx - w * 0.16 + i * w * 0.08
        d.rectangle([cxx, y + h * 0.60, cxx + w * 0.03, y + h * 0.88], fill=(228, 230, 234))
    d.rectangle([cx - w * 0.22, y + h * 0.88, cx + w * 0.22, y + h * 0.94], fill=(210, 213, 218))
    d.rounded_rectangle([x + w * 0.62, y + h * 0.30, x + w * 0.92, y + h * 0.78], 4,
                        fill=(240, 238, 230))
    d.line([x + w * 0.68, y + h * 0.54, x + w * 0.75, y + h * 0.66], fill=(46, 125, 91), width=4)
    d.line([x + w * 0.75, y + h * 0.66, x + w * 0.87, y + h * 0.40], fill=(46, 125, 91), width=4)


def sc_gta(d, x, y, w, h):
    _sky(d, x, y, w, h, (38, 24, 66), (196, 84, 120))
    d.ellipse([x + w * 0.70, y + h * 0.10, x + w * 0.86, y + h * 0.42], fill=(250, 170, 90))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(24, 18, 40))
    cx, cy = x + w * 0.40, y + h * 0.52
    d.rounded_rectangle([cx - w * 0.20, cy - h * 0.20, cx + w * 0.20, cy + h * 0.20], 12,
                        fill=(30, 30, 38))
    d.line([cx - w * 0.10, cy, cx - w * 0.04, cy], fill=(230, 230, 235), width=3)
    d.line([cx - w * 0.07, cy - h * 0.07, cx - w * 0.07, cy + h * 0.07], fill=(230, 230, 235), width=3)
    for dx, dy, col in ((0.10, -0.06, (240, 90, 90)), (0.145, 0.02, (90, 200, 120)),
                        (0.10, 0.10, (90, 140, 240)), (0.055, 0.02, (240, 200, 90))):
        d.ellipse([cx + w * dx - 3.5, cy + h * dy - 3.5, cx + w * dx + 3.5, cy + h * dy + 3.5],
                  fill=col)
    f = F(SANS_B, 12)
    d.text((x + w * 0.66, y + h * 0.52), "VI", font=F(SERIF_B, 22), fill=(255, 255, 255))


def sc_dhaka(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 226, 216))
    d.rectangle([x + w * 0.10, y + h * 0.18, x + w * 0.58, y + h * 0.72], fill=(150, 146, 138))
    d.rectangle([x + w * 0.50, y + h * 0.04, x + w * 0.58, y + h * 0.18], fill=(110, 106, 100))
    for r in range(3):
        for c in range(4):
            d.rectangle([x + w * (0.15 + 0.10 * c), y + h * (0.26 + 0.15 * r),
                         x + w * (0.21 + 0.10 * c), y + h * (0.35 + 0.15 * r)],
                        fill=(250, 214, 120))
    d.rectangle([x + w * 0.64, y + h * 0.30, x + w * 0.95, y + h * 0.44], fill=(179, 53, 44))
    f = F(SANS_B, 9)
    d.text((x + w * 0.685, y + h * 0.335), "PAY NOW", font=f, fill=(255, 255, 255))
    import random
    rnd = random.Random(7)
    for i in range(26):
        px = x + w * (0.06 + 0.88 * rnd.random())
        py = y + h * (0.80 + 0.13 * rnd.random())
        d.ellipse([px, py, px + 4, py + 4], fill=(60, 64, 70))


def sc_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(234, 240, 234))
    base = y + h * 0.86
    for i, bh in enumerate((0.22, 0.36, 0.30, 0.52, 0.72)):
        bx = x + w * (0.08 + 0.17 * i)
        d.rectangle([bx, base - h * bh, bx + w * 0.11, base], fill=(46, 125, 91))
    d.line([x + w * 0.06, base - h * 0.30, x + w * 0.90, base - h * 0.88],
           fill=(20, 32, 48), width=3)
    d.polygon([(x + w * 0.90, base - h * 0.88), (x + w * 0.80, base - h * 0.86),
               (x + w * 0.87, base - h * 0.76)], fill=(20, 32, 48))
    f = F(SERIF_B, 15)
    d.text((x + w * 0.10, y + h * 0.06), "$83", font=f, fill=(20, 32, 48))


def sc_cop31(d, x, y, w, h):
    _sky(d, x, y, w, h, (120, 178, 205), (226, 232, 214))
    cx, cy, r = x + w * 0.36, y + h * 0.52, h * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(74, 130, 190))
    d.polygon([(cx - r * 0.7, cy - r * 0.4), (cx - r * 0.2, cy - r * 0.7), (cx + r * 0.1, cy - r * 0.3),
               (cx - r * 0.3, cy)], fill=(96, 168, 110))
    d.polygon([(cx + r * 0.2, cy + r * 0.3), (cx + r * 0.65, cy + r * 0.15), (cx + r * 0.6, cy + r * 0.6),
               (cx + r * 0.25, cy + r * 0.7)], fill=(96, 168, 110))
    tx = x + w * 0.78
    d.rounded_rectangle([tx - 5, y + h * 0.16, tx + 5, y + h * 0.78], 5, outline=(60, 64, 70), width=2)
    d.rectangle([tx - 3, y + h * 0.30, tx + 3, y + h * 0.76], fill=(214, 84, 60))
    d.ellipse([tx - 9, y + h * 0.74, tx + 9, y + h * 0.96], fill=(214, 84, 60))


SCENES = {
    "tarmac": sc_tarmac, "gulf": sc_gulf, "voyager": sc_voyager,
    "drones": sc_drones, "fed": sc_fed, "gaza": sc_gaza, "akvan": sc_akvan,
    "elobeid": sc_elobeid, "eu": sc_eu, "uk": sc_uk, "jeffries": sc_jeffries,
    "gta": sc_gta, "dhaka": sc_dhaka, "ipo": sc_ipo, "cop31": sc_cop31,
}


# ---------------------------------------------------------------- world map
# Coarse continent polygons in (lon, lat); the map is drawn as a dot
# grid, a dot wherever a point falls inside any polygon.

POLYS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-80, 73),
     (-75, 68), (-65, 62), (-55, 52), (-60, 46), (-70, 44), (-74, 40), (-76, 35),
     (-80, 32), (-80, 26), (-84, 22), (-90, 20), (-95, 18), (-97, 16), (-105, 20),
     (-110, 23), (-114, 28), (-120, 33), (-124, 40), (-124, 46), (-130, 55),
     (-150, 60), (-165, 60)],
    [(-45, 60), (-30, 68), (-22, 70), (-20, 76), (-30, 80), (-50, 78), (-58, 70), (-52, 62)],
    [(-78, 7), (-70, 11), (-62, 10), (-52, 5), (-44, -3), (-35, -8), (-40, -20),
     (-48, -26), (-56, -35), (-62, -39), (-65, -45), (-67, -50), (-68, -54),
     (-72, -50), (-73, -44), (-73, -37), (-71, -30), (-70, -20), (-75, -15),
     (-79, -8), (-80, -4), (-77, 3)],
    [(-17, 15), (-10, 29), (-6, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (38, 22), (43, 12), (48, 11), (51, 12), (44, 0), (40, -8), (38, -18),
     (35, -24), (30, -30), (20, -35), (17, -32), (14, -22), (12, -15), (13, -5),
     (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 12)],
    [(44, -16), (47, -15), (50, -20), (47, -24), (45, -25), (44, -20)],
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (-1, 50), (2, 51), (7, 54), (8, 57),
     (13, 55), (19, 55), (21, 59), (25, 60), (24, 64), (30, 65), (32, 66),
     (29, 60), (28, 54), (30, 50), (28, 46), (30, 42), (27, 40), (23, 36),
     (19, 40), (14, 42), (12, 45), (8, 44), (3, 43), (0, 39), (-2, 36)],
    [(4, 58), (6, 62), (12, 64), (18, 66), (24, 68), (30, 70), (31, 66),
     (25, 64), (21, 62), (18, 59), (12, 58), (6, 57)],
    [(-5, 50), (-2, 52), (-3, 54), (-5, 56), (-7, 58), (-6, 59), (-4, 57),
     (-2, 55), (-1, 52), (-3, 50)],
    [(30, 66), (45, 68), (60, 69), (75, 72), (100, 77), (130, 72), (160, 70),
     (178, 66), (178, 62), (162, 60), (156, 52), (142, 50), (140, 42), (135, 35),
     (128, 38), (122, 37), (121, 31), (110, 20), (108, 14), (106, 9), (103, 5),
     (100, 7), (98, 13), (95, 16), (92, 16), (90, 22), (88, 22), (86, 20),
     (81, 15), (77, 8), (76, 10), (73, 18), (70, 21), (66, 25), (61, 25),
     (57, 26), (52, 28), (50, 29), (48, 30), (50, 25), (55, 24), (59, 22),
     (56, 19), (53, 16), (45, 12), (43, 12), (40, 16), (38, 21), (35, 28),
     (34, 31), (36, 36), (33, 36), (30, 36), (30, 41), (28, 46), (30, 50),
     (28, 55), (30, 60)],
    [(95, 5), (100, 0), (105, -5), (110, -6), (115, -8), (120, -9), (125, -10),
     (130, -8), (135, -4), (140, -3), (145, -5), (150, -8), (147, -9), (142, -8),
     (136, -6), (131, -9), (126, -11), (120, -10), (113, -7), (106, -6),
     (100, -2), (96, 3)],
    [(109, 1), (113, 4), (117, 6), (119, 2), (117, -2), (113, -3), (110, -1)],
    [(120, 18), (122, 16), (122, 13), (124, 10), (126, 8), (124, 7), (121, 10), (120, 14)],
    [(130, 31), (133, 34), (137, 35), (140, 36), (140, 39), (142, 42), (144, 44),
     (142, 45), (140, 41), (138, 37), (135, 34), (131, 32)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (130, -32),
     (132, -31), (135, -35), (138, -36), (140, -38), (145, -38), (150, -37),
     (153, -30), (153, -26), (150, -22), (146, -19), (142, -15), (142, -11),
     (139, -17), (136, -15), (135, -12), (132, -11), (130, -12), (126, -14),
     (122, -17), (118, -20)],
    [(167, -45), (170, -43), (172, -41), (174, -39), (176, -38), (174, -41),
     (172, -43), (169, -46)],
]

# card number -> (lon, lat) of its pin; card 3 (Voyager) gets the corner star
PINS = {
    1: (114.0, 22.5), 2: (48.0, 29.4), 4: (30.5, 50.4), 5: (-77.0, 38.9),
    6: (34.3, 31.4), 7: (86.0, 20.3), 8: (30.2, 13.2), 9: (4.4, 50.8),
    10: (-0.1, 51.5), 11: (-75.0, 34.0), 12: (172.6, -43.5), 13: (90.4, 23.8),
    14: (-122.4, 37.8), 15: (30.7, 36.9),
}


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < xin:
                inside = not inside
    return inside


def draw_map(d, x, y, w, h):
    def proj(lon, lat):
        return (x + (lon + 180) / 360 * w, y + (78 - lat) / 140 * h)
    step = 6.4
    gx = x + 3
    while gx < x + w - 2:
        gy = y + 3
        while gy < y + h - 2:
            lon = (gx - x) / w * 360 - 180
            lat = 78 - (gy - y) / h * 140
            if any(_in_poly(lon, lat, p) for p in POLYS):
                d.ellipse([gx - 1.3, gy - 1.3, gx + 1.3, gy + 1.3], fill=(112, 124, 136))
            gy += step
        gx += step
    # dashed gold line out of the top-right corner, for Voyager (story 3)
    sx, sy = proj(-155, 42)
    ex, ey = x + w - 4, y + 4
    for s in range(18):
        u = s / 17
        px, py = sx + (ex - sx) * u, sy + (ey - sy) * u
        if s % 2 == 0:
            d.ellipse([px - 1.3, py - 1.3, px + 1.3, py + 1.3], fill=GOLD)
    for num, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        d.ellipse([px - 6.5, py - 6.5, px + 6.5, py + 6.5], fill=RED)
        f = F(SANS_B, 8)
        t = str(num)
        d.text((px - tw(d, t, f) / 2, py - 4.5), t, font=f, fill=(255, 255, 255))
    px, py = ex, ey + 6
    d.ellipse([px - 6.5, py - 6.5, px + 6.5, py + 6.5], fill=GOLD)
    f = F(SANS_B, 8)
    d.text((px - tw(d, "3", f) / 2, py - 4.5), "3", font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- assembly

WARN = []


def draw_card(d, x, y, w, h, card, tier):
    num, region, beat, head, deck, scene, src = card
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=HAIR, width=1)
    if tier == "A":
        sh, hs, ds, hlh, dlh, maxd = 92, 20, 11, 24, 14, 3
    elif tier == "B":
        sh, hs, ds, hlh, dlh, maxd = 52, 15, 9.5, 18, 12, 3
    else:
        sh, hs, ds, hlh, dlh, maxd = 38, 12.5, 8.5, 15, 10.5, 4
    SCENES[scene](d, x + 1, y + 1, w - 2, sh)
    d.rectangle([x, y + sh + 1, x + w, y + sh + 4], fill=REGIONS[region])
    by = y + sh + 10
    d.ellipse([x + 7, by - 7, x + 23, by + 9], fill=RED)
    nf = F(SANS_B, 10)
    t = str(num)
    d.text((x + 15 - tw(d, t, nf) / 2, by - 5), t, font=nf, fill=(255, 255, 255))
    kf = F(SANS_B, 9)
    d.text((x + 28, by - 5), f"{region} · {beat}", font=kf, fill=REGIONS[region])
    if tier in ("A", "B"):
        sf = F(SANS, 8)
        d.text((x + w - 7 - tw(d, src, sf), by - 4), src, font=sf, fill=GREY)
    pad = 8
    hy = by + 12
    hf = F(SERIF_B, int(hs * 2) // 2 if hs == int(hs) else int(hs))
    hf = ImageFont.truetype(SERIF_B, round(hs))
    lines = wrap(d, head, hf, w - 2 * pad)
    if len(lines) > 2:
        WARN.append(f"card {num}: headline {len(lines)} lines")
    for ln in lines[:2]:
        d.text((x + pad, hy), ln, font=hf, fill=INK)
        hy += hlh
    df = ImageFont.truetype(SANS, round(ds))
    dlines = wrap(d, deck, df, w - 2 * pad)
    if len(dlines) > maxd:
        WARN.append(f"card {num}: deck {len(dlines)} lines (max {maxd})")
    for ln in dlines[:maxd]:
        d.text((x + pad, hy + 1), ln, font=df, fill=(52, 60, 70))
        hy += dlh
    if hy > y + h - 2:
        WARN.append(f"card {num}: content bottom {hy - y:.0f} > {h}")


def build(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M, CW = 16, W - 32

    # masthead
    d.rectangle([M, 10, M + 84, 102], fill=RED)
    f = F(SANS_B, 13)
    d.text((M + 42 - tw(d, "NOV", f) / 2, 18), "NOV", font=f, fill=(255, 255, 255))
    f = F(SERIF_B, 38)
    d.text((M + 42 - tw(d, "18", f) / 2, 34), "18", font=f, fill=(255, 255, 255))
    f = F(SANS_B, 9)
    d.text((M + 42 - tw(d, "WED · 2026", f) / 2, 80), "WED · 2026", font=f, fill=(255, 255, 255))
    tx = M + 98
    f = F(SANS_B, 12)
    d.text((tx, 14), "T H E   D A Y   I N   W O R L D   N E W S", font=f, fill=GOLD)
    f = ImageFont.truetype(SERIF_B, fit_size(d, "Wednesday 18 November 2026", SERIF_B, 716, 46))
    d.text((tx, 30), "Wednesday 18 November 2026", font=f, fill=NAVY)
    f = F(SERIF_I, 13)
    d.text((tx, 82), "Everything on this page happened, or was first reported, "
                     "on Wednesday 18 November 2026.", font=f, fill=(52, 60, 70))
    d.rectangle([838, 10, 1008, 102], fill=NAVY)
    for i, line in enumerate(("50 STORIES", "7 REGIONS", "ONE PAGE")):
        f = F(SERIF_B, 16)
        d.text((923 - tw(d, line, f) / 2, 20 + i * 27), line, font=f, fill=(255, 255, 255))

    # region tally (computed from the story data)
    counts = {}
    for c in CARDS:
        counts[c[1]] = counts.get(c[1], 0) + 1
    for b in BRIEFS:
        counts[b[3]] = counts.get(b[3], 0) + 1
    order = ["EUROPE", "AMERICAS", "ASIA", "AFRICA", "MIDDLE EAST", "OCEANIA", "WORLD"]
    x = M
    for rname in order:
        segw = CW * counts[rname] / 50
        d.rectangle([x, 106, x + segw, 130], fill=REGIONS[rname])
        f = F(SANS_B, 10)
        label = f"{rname} {counts[rname]}"
        d.text((x + segw / 2 - tw(d, label, f) / 2, 112), label, font=f, fill=(255, 255, 255))
        x += segw

    # by the numbers
    ny = 134
    f = F(SANS_B, 11)
    d.text((M, ny + 8), "THE DAY", font=f, fill=NAVY)
    d.text((M, ny + 22), "IN NUMBERS", font=f, fill=NAVY)
    d.rectangle([M, ny + 40, M + 84, ny + 43], fill=RED)
    cellw = (CW - 96) / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + 96 + i * cellw
        if i:
            d.line([cx - 8, ny + 4, cx - 8, ny + 48], fill=HAIR, width=1)
        f = ImageFont.truetype(SERIF_B, fit_size(d, num, SERIF_B, cellw - 14, 25, 14))
        d.text((cx, ny), num, font=f, fill=NAVY)
        cf = F(SANS, 9)
        for j, ln in enumerate(wrap(d, cap, cf, cellw - 14)[:2]):
            d.text((cx, ny + 30 + j * 11), ln, font=cf, fill=(52, 60, 70))

    # cards: rows A (3), B (5), C (7)
    def row(cards, y0, h, tier):
        n = len(cards)
        gap = 13 if tier == "A" else (10 if tier == "B" else 8)
        cw = (CW - gap * (n - 1)) / n
        for i, c in enumerate(cards):
            draw_card(d, M + i * (cw + gap), y0, cw, h, c, tier)
    row(CARDS[0:3], 196, 204, "A")
    row(CARDS[3:8], 406, 150, "B")
    row(CARDS[8:15], 562, 138, "C")

    # bottom band: map left, briefs right
    by0 = 706
    f = F(SANS_B, 12)
    d.text((M, by0), "WHERE IT HAPPENED", font=f, fill=NAVY)
    d.rectangle([M, by0 + 17, M + 306, by0 + 19], fill=RED)
    draw_map(d, M, by0 + 24, 306, 178)
    f = F(SANS, 8.5)
    d.text((M, by0 + 208), "Red pins: stories 1–15 · gold: 3, to Voyager · positions approximate",
           font=f, fill=GREY)
    bx = M + 322
    f = F(SERIF_B, 15)
    d.text((bx, by0 - 2), "ALSO ON WEDNESDAY 18 NOVEMBER", font=f, fill=NAVY)
    f = F(SANS_B, 10)
    d.text((bx + 316, by0 + 3), "— 35 MORE STORIES", font=f, fill=RED)
    d.rectangle([bx, by0 + 17, 1008, by0 + 19], fill=RED)
    colw = (1008 - bx - 14) / 2
    bf = F(SANS, 10.5)
    bfb = F(SANS_B, 10.5)
    lh = 11.9
    for i, (num, place, text, region) in enumerate(BRIEFS):
        col, r = divmod(i, 18) if i < 18 else (1, i - 18)
        cx = bx + col * (colw + 14)
        yy = by0 + 26 + r * lh
        nf = F(SANS_B, 10.5)
        d.text((cx, yy), str(num), font=nf, fill=REGIONS[region])
        px = cx + tw(d, str(num) + " ", nf)
        lead = place + ": "
        d.text((px, yy), lead, font=bfb, fill=INK)
        tx2 = px + tw(d, lead, bfb)
        line = text
        if tx2 + tw(d, line, bf) > cx + colw:
            WARN.append(f"brief {num}: too wide ({tx2 + tw(d, line, bf) - cx:.0f} > {colw:.0f})")
        d.text((tx2, yy), line, font=bf, fill=(40, 48, 58))

    # date check
    dy = 952
    d.rectangle([M, dy, 1008, dy + 38], fill=(250, 240, 236), outline=RED, width=1)
    f = F(SANS_B, 10.5)
    d.text((M + 8, dy + 5), "DATE CHECK", font=f, fill=RED)
    tf = F(SANS, 9.5)
    for j, ln in enumerate(wrap(d, DATE_CHECK, tf, 992 - 96)[:3]):
        d.text((M + 88, dy + 3 + j * 12), ln, font=tf, fill=(52, 44, 40))

    # footer
    f = F(SANS, 9.5)
    if tw(d, FOOTER, f) > CW:
        f = F(SANS, 9)
    d.text((512 - tw(d, FOOTER, f) / 2, 998), FOOTER, font=f, fill=GREY)

    img.save(path)
    print(f"wrote {path}")
    for w_ in WARN:
        print("WARN:", w_)
    if not WARN:
        print("no layout warnings")


if __name__ == "__main__":
    import os
    build(os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"))
