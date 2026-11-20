#!/usr/bin/env python3
"""news-image-20261120 - one-page broadsheet for Friday 20 November 2026.
Draws a deterministic 1024x1024 newspaper with Pillow, no network.
Writes to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)."""
import os, math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (247, 241, 227)
PAPER = (252, 249, 240)
NAVY = (18, 38, 76)
RED = (178, 34, 34)
GOLD = (196, 145, 32)
INK = (28, 28, 28)
GREY = (92, 92, 86)
LIGHT = (231, 222, 198)
TEAL = (22, 110, 110)
GREEN = (48, 110, 62)
ORANGE = (210, 105, 30)
BLUE = (45, 95, 170)

FD = "/usr/share/fonts/truetype/dejavu/"
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/liberation/",
    "/usr/share/fonts/truetype/noto/",
    "/usr/share/fonts/",
]
_FONT_ALT = {
    "DejaVuSans.ttf": ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "NotoSans-Regular.ttf"],
    "DejaVuSans-Bold.ttf": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"],
    "DejaVuSerif-Bold.ttf": ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf", "NotoSerif-Bold.ttf"],
}
def F(name, size):
    for cand in _FONT_ALT.get(name, [name]):
        for base in _FONT_DIRS:
            p = base + cand
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()
def serif(size): return F("DejaVuSerif-Bold.ttf", size)
def sans(size): return F("DejaVuSans.ttf", size)
def bold(size): return F("DejaVuSans-Bold.ttf", size)

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def txt(d, x, y, text, font, color=INK, anchor=None):
    d.text((x, y), text, font=font, fill=color, anchor=anchor)

def para(d, x, y, text, font, maxw, color=INK, lh=None, max_lines=None):
    lines = wrap(d, text, font, maxw)
    if max_lines: lines = lines[:max_lines]
    step = lh or int(font.size * 1.28)
    for i, ln in enumerate(lines):
        d.text((x, y + i * step), ln, font=font, fill=color)
    return y + len(lines) * step

def box(d, xy, fill=PAPER, outline=INK, width=1, radius=4):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def num_circle(d, cx, cy, r, n, fill=RED):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=(255,255,255), width=2)
    txt(d, cx, cy, str(n), bold(max(9, r)), (255,255,255), anchor="mm")

# ---------- small drawn scenes for the leads ----------
def draw_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(178, 205, 225))
    cx, cy = x + w*0.38, y + h*0.52
    for r, col in [(34,(255,255,255)),(26,(225,235,245)),(18,(255,255,255)),(10,(170,195,220))]:
        d.arc([cx-r, cy-r*0.72, cx+r, cy+r*0.72], start=20, end=320, fill=col, width=5)
        d.arc([cx-r, cy-r*0.72, cx+r, cy+r*0.72], start=200, end=500, fill=col, width=4)
    d.ellipse([cx-5, cy-4, cx+5, cy+4], fill=NAVY)
    # coast + houses + wind
    d.polygon([(x+w*0.62, y+h), (x+w, y+h*0.35), (x+w, y+h)], fill=(214, 196, 150))
    for hx in (0.70, 0.82, 0.92):
        bx = x + w*hx
        d.rectangle([bx, y+h*0.72, bx+16, y+h*0.88], fill=(250,248,240), outline=INK)
        d.polygon([(bx-3, y+h*0.72), (bx+8, y+h*0.60), (bx+19, y+h*0.72)], fill=RED)
    for i in range(3):
        yy = y + 10 + i*12
        d.arc([x+8, yy, x+52, yy+14], start=180, end=340, fill=(255,255,255), width=2)

def draw_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(38, 44, 74))
    # skyline
    for bx, bh, bw in [(0.05,0.45,0.14),(0.22,0.62,0.12),(0.38,0.50,0.16),(0.58,0.68,0.12),(0.74,0.52,0.14),(0.90,0.60,0.09)]:
        bx2 = x + w*bx
        d.rectangle([bx2, y+h*(1-bh), bx2+w*bw, y+h], fill=(18,20,32))
        for wy in range(3):
            for wx in range(2):
                d.rectangle([bx2+4+wx*9, y+h*(1-bh)+6+wy*11, bx2+9+wx*9, y+h*(1-bh)+11+wy*11], fill=(250,200,80))
    # missiles
    for mx, my, ang in [(0.25,0.18,-35),(0.52,0.12,-30),(0.78,0.22,-40)]:
        cx, cy = x+w*mx, y+h*my
        d.line([cx-16, cy-10, cx+10, cy+8], fill=(255,120,60), width=4)
        d.ellipse([cx+6, cy+4, cx+16, cy+13], fill=(255,210,90))
    d.ellipse([x+w*0.60, y+h*0.66, x+w*0.78, y+h*0.84], fill=(235,110,40))
    d.ellipse([x+w*0.64, y+h*0.60, x+w*0.74, y+h*0.74], fill=(250,180,70))

def draw_cop(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(205, 228, 205))
    cx, cy = x+w*0.50, y+h*0.50
    d.ellipse([cx-30, cy-26, cx+30, cy+26], fill=(90,160,210), outline=NAVY, width=2)
    d.polygon([(cx-18,cy-12),(cx-4,cy-18),(cx-2,cy-4),(cx-16,cy+2)], fill=GREEN)
    d.polygon([(cx+6,cy+6),(cx+22,cy+2),(cx+24,cy+14),(cx+8,cy+16)], fill=GREEN)
    # conference table + deadlock sign
    d.rectangle([x+10, y+h-20, x+w-10, y+h-8], fill=(120,85,50))
    d.rectangle([cx-52, y+4, cx+52, y+20], fill=(255,255,255), outline=NAVY)
    txt(d, cx, y+12, "COP31", bold(11), NAVY, anchor="mm")
    d.rectangle([cx-58, y+h-34, cx+58, y+h-22], fill=(255,255,255), outline=RED)
    txt(d, cx, y+h-28, "FOSSIL FUELS \u2717", bold(8), RED, anchor="mm")

ICON_COLORS = [TEAL, ORANGE, BLUE, GREEN, RED, NAVY, GOLD, TEAL, ORANGE, BLUE]

# ---------- content (exact set from the brief) ----------
LEADS = [
    ("1", "ODISHA, INDIA \u00b7 CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Severe storm crosses near Gopalpur; 300,000+ evacuated, winds 90\u2013100 gusting 110 km/h, 423 rescue teams deployed, schools shut. (IMD, The Hindu)", draw_cyclone),
    ("2", "KYIV, UKRAINE \u00b7 WAR", "Russia fires wave of ~30 ballistic missiles at Kyiv",
     "Seven overnight waves hit energy and transport sites; 3 killed, fires in three districts; Dutch and Austrian embassies damaged. (Kyiv Post, Reuters)", draw_kyiv),
    ("3", "ANTALYA, T\u00dcRKIYE \u00b7 CLIMATE", "COP31 reaches its final day deadlocked",
     "Closing draft omits fossil-fuel phase-out while $120bn adaptation finance stays unresolved; hosts push \u201c35 by 35\u201d clean-power goal. (UN News, Reuters)", draw_cop),
]

CARDS = [
    (4, "SEOUL/TOKYO \u00b7 MARKETS", "AI sell-off sinks Asia to worst week since 2020", "Nikkei \u22124.9%, KOSPI \u22125.4% (below 5,000), TAIEX \u22126.8%; chipmakers lead the slide. (Reuters)"),
    (5, "NEW YORK \u00b7 MARKETS", "Anthropic ends first day up 17%", "Claude maker closes at $97.17, still above its $83 offer, as the S&P 500 falls 2.02%. (Reuters)"),
    (6, "MERCURY \u00b7 SPACE", "BepiColombo reaches Mercury after 8 years", "ESA/JAXA probe ends 6bn-mile trip; orbit insertion set for Saturday. (ESA, BBC)"),
    (7, "BRUSSELS \u00b7 EUROPE", "Burnham holds first EU\u2013UK reset summit", "Costa & von der Leyen host UK PM; agrifood & carbon links eyed; 100,000 youth places. (EU Council)"),
    (8, "TOKYO \u00b7 ECONOMY", "Japan inflation 2.3%; core quickens to 2.2%", "BoJ hike eyed; core above 2% for second month. (Reuters, CNBC)"),
    (9, "BEIJING \u00b7 RATES", "China holds lending rates for 18th month", "1-year LPR stays at 3.0%, 5-year at 3.5%, as expected. (PBOC, Reuters)"),
    (10, "WELLINGTON \u00b7 CRICKET", "Phillips makes history with 118 vs India", "First NZ batter with centuries in all 3 formats vs India in a year; NZ 368. (ICC, AP)"),
    (11, "SAN SALVADOR \u00b7 POLITICS", "Bukele registers for third-term bid", "Files with electoral tribunal for Feb 2027 vote; rights groups object. (AP)"),
    (12, "SENEGAL \u00b7 MIGRATION", "Migrant boat capsizes off Yenne; 4 dead", "Dozens missing from 50\u2013100 aboard as Canary arrivals surge. (Al Jazeera)"),
    (13, "ROME \u00b7 LABOUR", "Italy's CGIL holds 24-hr general strike", "Unions rally across ~100 squares against 2027 budget; transit hit. (CGIL, AFP)"),
]

BRIEFS = [
    (14, "JAKARTA", "Indonesia's parliament passes asset-forfeiture bill (Reuters)"),
    (15, "SEOUL", "Ruling party adopts bid to impeach Chief Justice Cho (SBS)"),
    (16, "SHENZHEN", "Leaders issue peace declaration after the trilateral"),
    (17, "WORLD \u00b7 GAMES", "GTA VI first full day: ~1.7m copies, $1.65bn pre-launch; 99 (Sensor Tower)"),
    (18, "TONGA", "Pacific kingdom declares emergency as El Ni\u00f1o drought bites (RNZ)"),
    (19, "LAS VEGAS", "Russell fastest in wet GP practice, 1:47.272 (Formula1.com)"),
    (20, "HORMUZ", "Tanker catches fire after striking a mine; 46 ships waiting"),
    (21, "GENOA", "Unidentified drones close Genoa's airport for four hours"),
    (22, "GERMANY", "IG Metall 24-hour strikes idle Audi, BMW and VW plants (Reuters)"),
    (23, "CINCINNATI", "Zoo's famed hippo Fiona dies a day after swallowing a hat (zoo)"),
    (24, "SEOUL", "Appeal court upholds Kakao founder's acquittal (AJU Press)"),
    (25, "KHARKIV", "Drone hits a hospital; at least four hurt (Ukrinform)"),
    (26, "TURIN", "Alcaraz\u2013Cobolli & Medvedev\u2013Tiafoe close ATP Finals groups (ATP)"),
    (27, "GLOBAL", "Gold down 2.6% near $3,526, lowest since Sept 2025 (ABC)"),
    (28, "SYDNEY", "Man charged with terror offences over researched vehicle bomb"),
    (29, "PUNJAB", "A truck driver wins $1.3m in a Diwali lottery"),
    (30, "RIYADH", "Officials confirm financial-district damage from Thu Houthi attack"),
    (31, "BLANTYRE", "Malawi fuel crisis: night queues, 20-litre cap, $3.24/litre"),
    (32, "BRAZIL", "Lula meets Chief Raoni as Indigenous land is recognised"),
    (33, "WASHINGTON", "Pentagon puts US war cost against Iran at $48.3bn"),
    (34, "COPENHAGEN", "Denmark's parliament approves Greenland defence bill (AFP)"),
    (35, "CANBERRA", "CBO warns AUKUS sub sales could shrink US fleet (Reuters)"),
    (36, "S\u00c3O PAULO", "Markets shut for Black Consciousness Day"),
    (37, "MEXICO CITY", "Nation marks 116th Revolution Day"),
    (38, "JUBA", "South Sudan postpones first elections to February 2027"),
    (39, "GENEVA", "Pew: Muslims will pass Christians as largest faith by 2035"),
    (40, "CUPERTINO", "Apple reportedly building an AI agent to run devices (Bloomberg)"),
]

NUMBERS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("~30", "ballistic missiles fired at Kyiv"),
    ("\u22124.9%", "Nikkei at its intraday low"),
    ("2.2%", "Japan core inflation, Oct"),
    ("118", "Phillips' historic century vs India"),
    ("$97.17", "Anthropic's first close, +17%"),
]

# dotted world map: rough continent polygons (x 0..100, y 0..55)
CONTINENTS = [
    [(2,14),(10,6),(24,5),(30,10),(28,18),(22,22),(20,30),(14,28),(8,22),(3,20)],
    [(20,32),(26,30),(30,36),(28,48),(23,52),(19,42)],
    [(42,12),(50,7),(54,12),(52,18),(46,20),(43,17)],
    [(44,24),(54,22),(58,30),(55,44),(48,50),(44,38)],
    [(56,10),(72,5),(88,9),(92,16),(84,22),(70,22),(60,18)],
    [(68,24),(80,24),(86,32),(80,40),(70,36)],
    [(86,40),(96,38),(98,46),(90,50),(85,46)],
]
def _in_poly(px, py, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj-xi)*(py-yi)/(yj-yi)+xi):
            inside = not inside
        j = i
    return inside
PINS = [  # (num, x, y) in 0..100 / 0..55 map space
    (1, 68, 30), (2, 54, 11), (3, 58, 19), (4, 82, 18), (5, 16, 16),
    (6, 96, 6), (7, 45, 10), (8, 86, 20), (9, 78, 19), (10, 94, 46),
    (11, 13, 27), (12, 43, 27), (13, 50, 17),
]

def draw_map(d, x, y, w, h):
    box(d, (x, y, x+w, y+h), fill=(238, 232, 210), outline=NAVY, width=2)
    txt(d, x+8, y+6, "WHERE IT HAPPENED", bold(11), NAVY)
    txt(d, x+w-8, y+6, "pins 1\u201313", sans(8), GREY, anchor="ra")
    # dots
    for gx in range(0, 101, 3):
        for gy in range(0, 56, 3):
            if not any(_in_poly(gx, gy, poly) for poly in CONTINENTS):
                continue
            px = x + 10 + gx / 100 * (w - 20)
            py = y + 28 + gy / 55 * (h - 38)
            d.ellipse([px-1.3, py-1.3, px+1.3, py+1.3], fill=(110, 125, 105))
    for n, pxp, pyp in PINS:
        px = x + 10 + pxp / 100 * (w - 20)
        py = y + 28 + pyp / 55 * (h - 38)
        if n == 6:
            # space inset for Mercury
            d.rectangle([x+w-62, y+24, x+w-6, y+62], fill=(30,30,50), outline=GOLD)
            d.ellipse([x+w-48, y+32, x+w-20, y+56], fill=(200,170,140), outline=(120,100,80))
            txt(d, x+w-34, y+58, "6 MERCURY", bold(6), (255,255,255), anchor="ma")
        else:
            num_circle(d, px, py, 8, n, fill=RED)
    txt(d, x+8, y+h-16, "SPACE inset: 6 \u00b7 Mercury (BepiColombo)", sans(7), GREY)

def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 14
    # kicker
    txt(d, M, 6, "THE WORLD IN ONE DAY", bold(11), NAVY)
    txt(d, W-M, 6, "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 40 STORIES \u00b7 7 REGIONS", bold(10), RED, anchor="ra")
    d.line([M, 24, W-M, 24], fill=NAVY, width=2)
    # masthead navy + red date block
    d.rectangle([M, 28, W-M, 92], fill=NAVY)
    d.rectangle([W-M-118, 28, W-M, 92], fill=RED)
    txt(d, M+14, 60, "Friday 20 November 2026", serif(40), (255,255,255), anchor="lm")
    txt(d, W-M-59, 48, "20 NOV", bold(20), (255,255,255), anchor="mm")
    txt(d, W-M-59, 72, "2026 \u00b7 FRI", bold(11), (255,255,255), anchor="mm")
    # standfirst + date line
    txt(d, M, 98, "Cyclone Akvan strikes India  \u00b7  Ballistic missiles hit Kyiv  \u00b7  COP31 deadlocked on final day", bold(15), INK)
    para(d, M, 120, "Every story on this page happened, or was first reported, on Friday 20 November 2026 in at least one time zone.", sans(9), W-2*M, GREY)
    # numbers strip
    y = 138; bw = (W - 2*M - 10) // 6
    txt(d, M, y, "THE DAY IN NUMBERS", bold(9), RED)
    y += 14
    for i, (big, label) in enumerate(NUMBERS):
        x = M + i * (bw + 2)
        box(d, (x, y, x+bw, y+42), fill=PAPER, outline=NAVY)
        txt(d, x+bw//2, y+4, big, bold(16), NAVY, anchor="ma")
        para(d, x+4, y+24, label, sans(7), bw-8, GREY, lh=9, max_lines=2)
    # region bar
    y += 48
    regions = [("EUROPE 10", RED), ("ASIA-PACIFIC 9", TEAL), ("AMERICAS 9", BLUE), ("AFRICA 3", ORANGE), ("OCEANIA 4", GREEN), ("MIDDLE EAST 2", GOLD), ("WORLD 3", NAVY)]
    total = 40; x = M
    for label, col in regions:
        cnt = int(label.rsplit(" ", 1)[1]); wseg = int((W-2*M) * cnt / total)
        d.rectangle([x, y, x+wseg, y+18], fill=col)
        txt(d, x+wseg//2, y+9, label, bold(8), (255,255,255), anchor="mm")
        x += wseg
    # timeline
    y += 22
    para(d, M, y, "UTC TIMELINE  00:22 Phillips century, Wellington \u00b7 01:27 Tanker hits mine near Hormuz \u00b7 04:07 Missiles hit Kyiv \u00b7 06:30 Akvan crosses coast near Gopalpur \u00b7 Morning Japan inflation 2.2% \u00b7 All day IG Metall strikes idle German car plants \u00b7 By midnight COP31 final text due, Antalya", sans(8), W-2*M, INK, lh=10, max_lines=2)
    # leads
    y += 22; lh_h = 176; lw = (W - 2*M - 12) // 3
    for i, (num, tag, head, body, scene) in enumerate(LEADS):
        x = M + i * (lw + 6)
        box(d, (x, y, x+lw, y+lh_h), fill=PAPER, outline=NAVY, width=2)
        scene(d, x+4, y+4, lw-8, 68)
        num_circle(d, x+16, y+16, 11, num)
        txt(d, x+8, y+76, tag, bold(8), RED)
        ny = para(d, x+8, y+88, head, bold(13), lw-16, INK, lh=16, max_lines=3)
        para(d, x+8, max(ny+2, y+128), body, sans(8), lw-16, GREY, lh=10, max_lines=4)
    # cards 4-13: 5 x 2
    y += lh_h + 8; cw = (W - 2*M - 16) // 5; ch = 92
    for idx, (n, tag, head, body) in enumerate(CARDS):
        col, row = idx % 5, idx // 5
        x = M + col * (cw + 4); yy = y + row * (ch + 4)
        box(d, (x, yy, x+cw, yy+ch), fill=PAPER, outline=GREY)
        d.rectangle([x, yy, x+cw, yy+5], fill=ICON_COLORS[idx])
        num_circle(d, x+13, yy+18, 9, n, fill=NAVY)
        txt(d, x+26, yy+11, tag, bold(6), RED)
        ny = para(d, x+6, yy+30, head, bold(9), cw-12, INK, lh=11, max_lines=3)
        para(d, x+6, min(ny+1, yy+62), body, sans(7), cw-12, GREY, lh=9, max_lines=3)
    # map + briefs
    y += 2 * ch + 12
    draw_map(d, M, y, 330, 172)
    bx = M + 338; bw2 = W - M - bx
    box(d, (bx, y, bx+bw2, y+172), fill=PAPER, outline=NAVY, width=2)
    txt(d, bx+8, y+6, "ALSO ON FRIDAY 20 NOVEMBER", bold(11), NAVY)
    txt(d, bx+8, y+22, "Briefs 14\u201340 \u00b7 one line each", sans(7), GREY)
    # two columns of briefs
    colw = (bw2 - 20) // 2
    for j, (n, loc, text) in enumerate(BRIEFS):
        col = 0 if j < 14 else 1; row = j if j < 14 else j - 14
        x = bx + 8 + col * (colw + 4); yy = y + 34 + row * 9
        line = f"{n} {loc} \u2014 {text}"
        # truncate to fit
        fnt = sans(7)
        while d.textlength(line, font=fnt) > colw and len(line) > 10:
            line = line[:-4].rstrip() + "\u2026" if False else line[:-1]
        txt(d, x, yy, line, fnt, INK)
    # date check footer
    y += 178
    box(d, (M, y, W-M, y+78), fill=(238, 228, 200), outline=RED, width=2)
    txt(d, M+8, y+6, "DATE CHECK", bold(11), RED)
    para(d, M+8, y+22, "First reported Thursday 19 Nov, so NOT shown as Friday's news: the Trump\u2013Xi\u2013Putin Shenzhen summit itself \u00b7 Anthropic's $83 IPO pricing and Nasdaq debut \u00b7 the ICJ's Myanmar Rohingya genocide verdict \u00b7 GTA VI's midnight launch \u00b7 the $190.4m Van Gogh sale \u00b7 Voyager 1's one light-day confirmation \u00b7 the Crimean Bridge strike \u00b7 COP31's second draft. Not yet: COP31's closing plenary and any final deal \u00b7 Las Vegas GP qualifying.", sans(8), W-2*M-16, INK, lh=11, max_lines=4)
    y += 84
    para(d, M, y, "Every story here happened, or was first reported, on Friday 20 November 2026 in at least one time zone. Claims are attributed, not stated as fact. Sources: Reuters, AP, AFP, BBC, Al Jazeera, The Hindu, PTI, UN News, EU Council, ICC. Original vector drawings.", sans(8), W-2*M, GREY, lh=10, max_lines=2)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    img.save(out, format="PNG", optimize=False)
    print(out)

if __name__ == "__main__":
    main()
