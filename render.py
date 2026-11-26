#!/usr/bin/env python3
"""Render THE WEDNESDAY GLOBE v4 — one-page broadsheet for 25 Nov 2026.

v4 adopts the shared concept of the competition's top 1-3 entries:
3 big illustrated lead cards + 10 small illustrated story cards +
big-number stat strip + UTC timeline + region counts + how-sure badges
+ map with numbered pins + numbered IN BRIEF list + DATE CHECK footer.

Local-only render script (provenance). The submitted program is main.py,
a stdlib-only copier that ships the pre-rendered entry.png.
"""
import hashlib
import math
import os
from PIL import Image, ImageDraw, ImageFont

import stories as S

W, H = 1024, 1024
PAPER = (246, 241, 227)
INK = (25, 25, 25)
RED = (169, 35, 24)
NAVY = (30, 58, 92)
NAVY_LT = (47, 79, 120)
TEAL = (0, 120, 110)
OLIVE = (96, 112, 58)
SAGE = (176, 184, 150)
SAGE_DK = (120, 130, 96)
OCEAN = (214, 226, 228)
RULE = (150, 140, 115)
GREY = (90, 86, 76)
CREAM = (246, 241, 227)

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"
SERIF_IT = "LiberationSerif-Italic.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rich_para(draw, x, y, max_w, segments, line_h):
    """Draw [(text, font, fill), ...] as one flowing paragraph.

    Returns the y just below the last line drawn.
    """
    words = []  # (word, font, fill)
    for text, fnt, fill in segments:
        for w in text.split(" "):
            words.append((w, fnt, fill))
    lines, cur, cur_w = [], [], 0.0
    space = draw.textlength(" ", font=segments[0][1])
    for w, fnt, fill in words:
        ww = draw.textlength(w, font=fnt)
        add = ww if not cur else space + ww
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(w, fnt, fill)], ww
        else:
            cur.append((w, fnt, fill))
            cur_w += add
    if cur:
        lines.append(cur)
    yy = y
    for line in lines:
        xx = x
        for w, fnt, fill in line:
            draw.text((xx, yy), w, font=fnt, fill=fill)
            xx += draw.textlength(w + " ", font=fnt)
        yy += line_h
    return yy


def centre(draw, y, text, fnt, fill, cx=W // 2):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def rule(draw, y, x0=16, x1=1008, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def lerp_col(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, top, bot, power=1.4):
    """Vertical gradient fill of a rectangle."""
    h = max(1, y1 - y0)
    for yy in range(y0, y1):
        t = ((yy - y0) / h) ** power
        draw.line([(x0, yy), (x1, yy)], fill=lerp_col(top, bot, t))


def chip(draw, x, y, text, fill=RED, fg=CREAM, fnt_size=10, pad=5):
    """Filled label chip; returns its width."""
    f = font(SANS_B, fnt_size)
    w = draw.textlength(text, font=f) + pad * 2
    h = fnt_size + 7
    draw.rectangle([x, y, x + w, y + h], fill=fill)
    draw.text((x + pad, y + 3), text, font=f, fill=fg)
    return w


def badge(draw, x, y, text):
    """How-sure badge chip; returns its width."""
    f = font(SANS_B, 9)
    w = draw.textlength(text, font=f) + 10
    h = 15
    if text == "OFFICIAL":
        draw.rectangle([x, y, x + w, y + h], fill=TEAL)
        draw.text((x + 5, y + 3), text, font=f, fill=CREAM)
    elif text == "CONFIRMED":
        draw.rectangle([x, y, x + w, y + h], fill=NAVY)
        draw.text((x + 5, y + 3), text, font=f, fill=CREAM)
    elif text == "REPORTED":
        draw.rectangle([x, y, x + w, y + h], fill=OLIVE)
        draw.text((x + 5, y + 3), text, font=f, fill=CREAM)
    else:  # CLAIM — red outline, red text on paper
        draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=RED, width=1)
        draw.text((x + 5, y + 3), text, font=f, fill=RED)
    return w


def num_disc(draw, cx, cy, num, r=9, fill=RED):
    """Circled story number."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
                 outline=(255, 255, 255), width=2)
    f = font(SANS_B, 10 if num < 10 else 9)
    tw = draw.textlength(str(num), font=f)
    draw.text((cx - tw / 2, cy - 7 if num < 10 else cy - 6), str(num),
              font=f, fill=(255, 255, 255))


def flame(draw, cx, base, w, h):
    """Layered teardrop flame rising from (cx, base)."""
    layers = [
        ((255, 90, 20), 1.00, 1.00),
        ((255, 150, 40), 0.78, 0.82),
        ((255, 205, 70), 0.55, 0.62),
        ((255, 240, 170), 0.32, 0.42),
    ]
    for col, wf, hf in layers:
        hw, hh = w * wf / 2, h * hf
        draw.polygon([
            (cx - hw, base), (cx - hw * 0.85, base - hh * 0.45),
            (cx - hw * 0.35, base - hh * 0.72), (cx, base - hh),
            (cx + hw * 0.30, base - hh * 0.70), (cx + hw * 0.8, base - hh * 0.4),
            (cx + hw, base),
        ], fill=col)


def smoke(draw, pts):
    """pts: list of (cx, cy, r, fill) smoke puffs."""
    for cx, cy, r, c in pts:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def spiked_mine(draw, x, y, r, ring=False):
    for k in range(8):
        ang = math.pi * k / 4
        x2 = x + int((r + 5) * math.cos(ang))
        y2 = y + int((r + 5) * math.sin(ang))
        draw.line([(x, y), (x2, y2)], fill=(8, 10, 14), width=2)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=(8, 10, 14),
                 outline=(70, 72, 80), width=1)
    if ring:
        draw.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3],
                     outline=RED, width=2)


def stars(draw, x0, y0, x1, y1, pts):
    """Deterministic stars: pts = list of (fx, fy, r) fractions of the box."""
    w, h = x1 - x0, y1 - y0
    for fx, fy, r in pts:
        x, y = x0 + fx * w, y0 + fy * h
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))


# ---------------------------------------------------------------- masthead
def masthead(draw):
    title = font(SERIF_B, 50)
    while draw.textlength(S.MASTHEAD_TITLE, font=title) > 980 and title.size > 30:
        title = font(SERIF_B, title.size - 2)
    centre(draw, 6, S.MASTHEAD_TITLE, title, INK)
    sub = font(SANS_B, 15)
    centre(draw, 64, S.MASTHEAD_DATE + "   •   " + S.MASTHEAD_TAG, sub, RED)
    rule(draw, 86, width=3)
    rule(draw, 90, width=1)


# ------------------------------------------------------- big-number strip
def stat_strip(draw):
    y0, y1 = 96, 148
    draw.rectangle([16, y0, 1008, y1], fill=NAVY)
    n = len(S.STATS)
    cell = 992 / n
    big_f = font(SANS_B, 24)
    cap_f = font(SANS, 9)
    for i, (big, cap) in enumerate(S.STATS):
        cx = 16 + cell * i + cell / 2
        bw = draw.textlength(big, font=big_f)
        draw.text((cx - bw / 2, y0 + 4), big, font=big_f, fill=CREAM)
        cw = draw.textlength(cap, font=cap_f)
        draw.text((cx - cw / 2, y0 + 34), cap, font=cap_f,
                  fill=(200, 210, 225))
        if i:
            x = 16 + cell * i
            draw.line([(x, y0 + 6), (x, y1 - 6)], fill=NAVY_LT, width=1)


# ---------------------------------------------------------- region counts
REGION_COLOURS = [(30, 58, 92), (169, 35, 24), (96, 112, 58),
                  (0, 120, 110), (120, 90, 30), (90, 86, 76)]


def region_counts(draw):
    y0 = 152
    n = len(S.REGION_COUNTS)
    cell = 992 / n
    f_name = font(SANS_B, 11)
    f_num = font(SANS_B, 13)
    for i, (name, count) in enumerate(S.REGION_COUNTS):
        col = REGION_COLOURS[i % len(REGION_COLOURS)]
        x = 16 + cell * i
        draw.rectangle([x, y0, x + cell - 4, y0 + 16], fill=col)
        txt = f"{name} {count}"
        tw = draw.textlength(txt, font=f_name)
        draw.text((x + (cell - 4 - tw) / 2, y0 + 2), txt, font=f_name,
                  fill=CREAM)


# ---------------------------------------------------------------- timeline
def timeline(draw):
    y0, y1 = 172, 190
    draw.rectangle([16, y0, 1008, y1], fill=INK)
    lab_f = font(SANS_B, 9)
    lab = "THE DAY IN UTC"
    draw.text((24, y0 + 4), lab, font=lab_f, fill=(255, 200, 80))
    f_t = font(SANS_B, 9)
    f_x = font(SANS, 9)
    x = 24 + draw.textlength(lab, font=lab_f) + 14
    items = S.TIMELINE
    # even spacing across the remaining width
    avail = 1008 - 8 - x
    per = avail / len(items)
    for i, (t, txt) in enumerate(items):
        xx = x + per * i
        draw.text((xx, y0 + 4), t, font=f_t, fill=(255, 200, 80))
        tx = xx + draw.textlength(t + " ", font=f_t)
        draw.text((tx, y0 + 4), txt, font=f_x, fill=CREAM)


# ============================================================ lead scenes
# Each draws into box (x0, y0, x1, y1). No text except chips added here.

def scene_hormuz(draw, x0, y0, x1, y1):
    """Burning tanker in the Strait of Hormuz (v3 scene, redrawn compact)."""
    w, h = x1 - x0, y1 - y0
    hor = y0 + int(h * 0.52)
    vgrad(draw, x0, y0, x1, hor, (16, 30, 56), (198, 86, 38))
    # landmasses framing the strait
    draw.polygon([(x0, y0), (x0 + int(w * 0.14), y0),
                  (x0 + int(w * 0.19), hor - 8), (x0 + int(w * 0.16), hor),
                  (x0, hor)], fill=(10, 20, 36))
    draw.polygon([(x1, y0), (x1 - int(w * 0.12), y0),
                  (x1 - int(w * 0.16), hor - 10), (x1 - int(w * 0.13), hor),
                  (x1, hor)], fill=(10, 20, 36))
    # sea
    draw.rectangle([x0, hor, x1, y1], fill=(14, 40, 64))
    for wy in (hor + 6, hor + 14, hor + 22):
        for wx in range(x0 + 8, x1 - 30, 46):
            draw.line([(wx, wy), (wx + 20, wy)], fill=(52, 96, 128), width=2)
    # US carrier group, mid-left
    cx0 = x0 + int(w * 0.30)
    draw.rectangle([cx0, hor - 8, cx0 + 64, hor - 3], fill=(24, 38, 58))
    draw.polygon([(cx0, hor - 3), (cx0 + 64, hor - 3), (cx0 + 60, hor + 3),
                  (cx0 + 4, hor + 3)], fill=(24, 38, 58))
    draw.rectangle([cx0 + 46, hor - 16, cx0 + 53, hor - 8], fill=(24, 38, 58))
    draw.rectangle([cx0 - 62, hor - 5, cx0 - 12, hor - 1], fill=(20, 32, 50))
    draw.polygon([(cx0 - 12, hor - 5), (cx0 - 4, hor - 3), (cx0 - 12, hor - 1)],
                 fill=(20, 32, 50))
    # burning tanker, right: listing hull, bow down — tall enough to read
    bx0 = x0 + int(w * 0.56)
    bx1 = x1 - int(w * 0.03)
    draw.polygon([(bx0, hor + 4), (bx1 - 14, hor + 12), (bx1, hor + 16),
                  (bx1 - 14, hor + 28), (bx0, hor + 24)],
                 fill=(24, 32, 44), outline=(110, 130, 150), width=1)
    draw.line([(bx0 + 20, hor + 5), (bx1 - 16, hor + 13)],
              fill=(255, 150, 60), width=2)
    draw.rectangle([bx0 + 6, hor - 16, bx0 + 26, hor + 4], fill=(10, 14, 22))
    draw.rectangle([bx0 + 12, hor - 26, bx0 + 20, hor - 16], fill=(10, 14, 22))
    # mine-strike burst at the bow waterline
    draw.ellipse([bx1 - 14, hor + 10, bx1 + 2, hor + 26], fill=(255, 160, 40))
    draw.ellipse([bx1 - 9, hor + 15, bx1 - 1, hor + 23], fill=(255, 240, 200))
    # fire reflection on the water
    draw.line([(bx0 + 30, hor + 30), (bx1 - 20, hor + 30)],
              fill=(255, 140, 60), width=2)
    # BIG FLAMES rising from the breach
    fx = bx0 + int((bx1 - bx0) * 0.55)
    flame(draw, fx, hor + 4, 62, 62)
    flame(draw, fx - 34, hor + 4, 26, 26)
    flame(draw, fx + 36, hor + 4, 26, 26)
    # smoke column drifting left
    smoke(draw, [
        (fx - 6, hor - 42, 9, (45, 45, 50)),
        (fx - 24, hor - 46, 10, (60, 60, 66)),
        (fx - 44, hor - 44, 9, (75, 75, 82)),
        (fx - 62, hor - 40, 9, (60, 60, 66)),
        (fx - 78, hor - 36, 8, (45, 45, 50)),
    ])
    # embers
    for ex, ey in ((fx - 20, hor - 30), (fx + 24, hor - 36),
                   (fx - 8, hor - 52), (fx + 40, hor - 18)):
        draw.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(255, 200, 80))
    # naval mines in the channel
    spiked_mine(draw, x0 + int(w * 0.24), hor + 16, 5, ring=True)
    spiked_mine(draw, x0 + int(w * 0.47), hor + 20, 5)
    # chips
    chip(draw, x0 + 6, y0 + 6, "3 TANKERS", fill=RED)
    lab = font(SANS_B, 9)
    txt = "STRAIT OF HORMUZ"
    tw = draw.textlength(txt, font=lab)
    draw.rectangle([x1 - tw - 12, y1 - 18, x1 - 4, y1 - 4], fill=(10, 20, 36))
    draw.text((x1 - tw - 6, y1 - 16), txt, font=lab, fill=CREAM)


def scene_refineries(draw, x0, y0, x1, y1):
    """Two Rosneft refineries burning at dusk."""
    w, h = x1 - x0, y1 - y0
    hor = y0 + int(h * 0.62)
    vgrad(draw, x0, y0, x1, hor, (38, 30, 66), (214, 110, 48))
    # distant skyline
    draw.rectangle([x0, hor, x1, y1], fill=(24, 20, 32))
    # refinery: towers, chimneys, storage tanks
    base = hor
    draw.rectangle([x0 + int(w * 0.06), base - 34, x0 + int(w * 0.16), base],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.10), base - 52, x0 + int(w * 0.13), base - 34],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.20), base - 26, x0 + int(w * 0.34), base],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.24), base - 44, x0 + int(w * 0.27), base - 26],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.40), base - 40, x0 + int(w * 0.52), base],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.44), base - 58, x0 + int(w * 0.47), base - 40],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.58), base - 30, x0 + int(w * 0.72), base],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.76), base - 46, x0 + int(w * 0.88), base],
                   fill=(12, 12, 18))
    draw.rectangle([x0 + int(w * 0.80), base - 62, x0 + int(w * 0.83), base - 46],
                   fill=(12, 12, 18))
    # two fireballs + smoke
    fx1 = x0 + int(w * 0.28)
    fx2 = x0 + int(w * 0.68)
    flame(draw, fx1, base - 24, 44, 44)
    flame(draw, fx2, base - 28, 50, 50)
    smoke(draw, [
        (fx1 - 4, base - 52, 8, (50, 46, 56)),
        (fx1 - 20, base - 56, 9, (66, 60, 72)),
        (fx1 - 36, base - 52, 7, (50, 46, 56)),
        (fx2 + 2, base - 58, 8, (50, 46, 56)),
        (fx2 + 16, base - 62, 9, (66, 60, 72)),
        (fx2 - 12, base - 56, 7, (50, 46, 56)),
    ])
    # ground glow
    draw.line([(x0 + int(w * 0.2), base + 2), (x0 + int(w * 0.76), base + 2)],
              fill=(255, 140, 60), width=2)
    chip(draw, x0 + 6, y0 + 6, "2 REFINERIES", fill=RED)
    lab = font(SANS_B, 9)
    txt = "SAMARA"
    tw = draw.textlength(txt, font=lab)
    draw.rectangle([x1 - tw - 12, y1 - 18, x1 - 4, y1 - 4], fill=(10, 20, 36))
    draw.text((x1 - tw - 6, y1 - 16), txt, font=lab, fill=CREAM)


def scene_gaza(draw, x0, y0, x1, y1):
    """Gaza City at night: skyline, one building hit, smoke rising."""
    w, h = x1 - x0, y1 - y0
    hor = y0 + int(h * 0.66)
    vgrad(draw, x0, y0, x1, hor, (12, 18, 40), (96, 62, 84))
    stars(draw, x0, y0, x1, hor, [
        (0.08, 0.15, 1), (0.22, 0.08, 1), (0.35, 0.22, 1), (0.5, 0.1, 1),
        (0.62, 0.2, 1), (0.78, 0.08, 1), (0.9, 0.18, 1), (0.45, 0.3, 1),
    ])
    # moon
    draw.ellipse([x1 - 34, y0 + 8, x1 - 14, y0 + 28], fill=(240, 234, 200))
    # skyline
    base = hor
    blds = [(0.02, 0.30, 0.34), (0.14, 0.42, 0.52), (0.28, 0.24, 0.44),
            (0.40, 0.50, 0.62), (0.54, 0.34, 0.46), (0.66, 0.44, 0.60),
            (0.80, 0.28, 0.40), (0.90, 0.36, 0.50)]
    for fx, fw, fh in blds:
        bx = x0 + int(w * fx)
        bw = int(w * fw)
        bh = int(h * fh)
        draw.rectangle([bx, base - bh, bx + bw, base], fill=(16, 16, 26))
        # lit windows
        for wy in range(base - bh + 6, base - 6, 12):
            for wx in range(bx + 5, bx + bw - 5, 12):
                if (wx + wy) % 3 == 0:
                    draw.rectangle([wx, wy, wx + 3, wy + 4],
                                   fill=(255, 200, 110))
    # struck building: glow + smoke (kept inside the box)
    sx = x0 + int(w * 0.46)
    flame(draw, sx, base - int(h * 0.40), 38, 32)
    smoke(draw, [
        (sx, base - int(h * 0.52), 8, (60, 58, 66)),
        (sx - 14, base - int(h * 0.56), 9, (76, 74, 82)),
        (sx - 28, base - int(h * 0.50), 7, (60, 58, 66)),
    ])
    draw.rectangle([x0, hor, x1, y1], fill=(20, 18, 28))
    chip(draw, x0 + 6, y0 + 6, "2ND IN 24 H", fill=RED)
    lab = font(SANS_B, 9)
    txt = "GAZA CITY"
    tw = draw.textlength(txt, font=lab)
    draw.rectangle([x1 - tw - 12, y1 - 18, x1 - 4, y1 - 4], fill=(10, 20, 36))
    draw.text((x1 - tw - 6, y1 - 16), txt, font=lab, fill=CREAM)


# ======================================================= small-card scenes
def scene_tiangong(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    vgrad(draw, x0, y0, x1, y1, (10, 18, 44), (30, 60, 110))
    stars(draw, x0, y0, x1, y1, [
        (0.1, 0.2, 1), (0.25, 0.1, 1), (0.4, 0.3, 1), (0.55, 0.12, 1),
        (0.7, 0.25, 1), (0.85, 0.1, 1), (0.92, 0.35, 1), (0.15, 0.45, 1),
    ])
    # space station (top right, below the badge row)
    sx, sy = x1 - 52, y0 + 24
    draw.rectangle([sx, sy + 6, sx + 34, sy + 12], fill=(200, 205, 210))
    draw.rectangle([sx + 8, sy, sx + 26, sy + 6], fill=(160, 165, 175))
    draw.rectangle([sx - 12, sy + 7, sx, sy + 11], fill=(40, 90, 180))
    draw.rectangle([sx + 34, sy + 7, sx + 46, sy + 11], fill=(40, 90, 180))
    # rocket rising (left)
    rx = x0 + 34
    draw.polygon([(rx, y0 + 6), (rx - 7, y0 + 18), (rx - 7, y0 + 34),
                  (rx + 7, y0 + 34), (rx + 7, y0 + 18)], fill=(240, 240, 240))
    draw.polygon([(rx - 7, y0 + 34), (rx - 12, y0 + 42), (rx - 7, y0 + 38)],
                 fill=(200, 60, 40))
    draw.polygon([(rx + 7, y0 + 34), (rx + 12, y0 + 42), (rx + 7, y0 + 38)],
                 fill=(200, 60, 40))
    flame(draw, rx, y0 + 44, 12, 12)
    # ground
    draw.rectangle([x0, y1 - 6, x1, y1], fill=(120, 90, 60))


def scene_mine(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    # cross-section: grass, earth, flooded shaft
    draw.rectangle([x0, y0, x1, y0 + 12], fill=(96, 130, 70))
    draw.rectangle([x0, y0 + 12, x1, y1], fill=(122, 96, 66))
    draw.polygon([(x0 + int(w * 0.42), y0 + 12), (x0 + int(w * 0.58), y0 + 12),
                  (x0 + int(w * 0.54), y1), (x0 + int(w * 0.46), y1)],
                 fill=(30, 24, 18))
    draw.rectangle([x0 + int(w * 0.46), y1 - 10, x0 + int(w * 0.54), y1],
                   fill=(40, 110, 160))
    # shaft rim + rescue light
    draw.rectangle([x0 + int(w * 0.40), y0 + 10, x0 + int(w * 0.60), y0 + 14],
                   fill=(60, 48, 32))
    draw.ellipse([x0 + int(w * 0.5) - 3, y0 + 18, x0 + int(w * 0.5) + 3,
                  y0 + 24], fill=(255, 220, 120))
    chip(draw, x0 + 4, y0 + 4, "100 M DEEP", fill=(10, 20, 36), fnt_size=8)


def scene_garment(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    vgrad(draw, x0, y0, x1, y1, (140, 200, 210), (210, 230, 225))
    # factory with sawtooth roof
    draw.polygon([(x0 + 10, y1 - 8), (x0 + 10, y0 + 22), (x0 + 30, y0 + 12),
                  (x0 + 50, y0 + 22), (x0 + 70, y0 + 12), (x0 + 90, y0 + 22),
                  (x0 + 90, y1 - 8)], fill=(0, 120, 110))
    for wx in range(x0 + 18, x0 + 86, 16):
        draw.rectangle([wx, y0 + 28, wx + 8, y0 + 38], fill=(255, 240, 180))
    # coin stack + big +36%
    for i, cy in enumerate((y1 - 10, y1 - 16, y1 - 22)):
        draw.ellipse([x1 - 46, cy - 4, x1 - 14, cy + 4], fill=(230, 180, 60),
                     outline=(160, 110, 20), width=1)
    chip(draw, x0 + 30, y1 - 18, "+36%", fill=RED, fnt_size=10)


def scene_chip(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(16, 24, 40))
    # green AI chip
    cx, cy = x0 + int(w * 0.32), y0 + int(h * 0.5)
    for dx in (-18, -9, 0, 9, 18):
        draw.line([(cx + dx, cy - 26), (cx + dx, cy - 16)], fill=(120, 200, 120),
                  width=2)
        draw.line([(cx + dx, cy + 16), (cx + dx, cy + 26)], fill=(120, 200, 120),
                  width=2)
    for dy in (-12, 0, 12):
        draw.line([(cx - 28, cy + dy), (cx - 18, cy + dy)],
                  fill=(120, 200, 120), width=2)
        draw.line([(cx + 18, cy + dy), (cx + 28, cy + dy)],
                  fill=(120, 200, 120), width=2)
    draw.rectangle([cx - 18, cy - 16, cx + 18, cy + 16], fill=(0, 160, 90),
                   outline=(120, 220, 140), width=1)
    f = font(SANS_B, 12)
    draw.text((cx - 6, cy - 8), "AI", font=f, fill=CREAM)
    chip(draw, x0 + 30, y1 - 18, "$12.9BN", fill=RED, fnt_size=9)


def scene_dow(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(14, 28, 52))
    # grid lines
    for gy in range(y0 + 8, y1 - 4, 10):
        draw.line([(x0 + 4, gy), (x1 - 4, gy)], fill=(30, 52, 84), width=1)
    # rising line
    pts = [(x0 + 10, y1 - 12), (x0 + 40, y1 - 26), (x0 + 62, y1 - 20),
           (x0 + 92, y1 - 34), (x0 + 122, y1 - 30), (x0 + 152, y1 - 44),
           (x1 - 12, y1 - 48)]
    draw.line(pts, fill=(110, 220, 130), width=3)
    draw.polygon([(x1 - 12, y1 - 48), (x1 - 24, y1 - 46), (x1 - 14, y1 - 38)],
                 fill=(110, 220, 130))
    chip(draw, x0 + 4, y0 + 4, "50,018.70", fill=(10, 20, 36), fnt_size=9)


def scene_fire(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    vgrad(draw, x0, y0, x1, y1, (60, 40, 50), (180, 90, 40))
    # factory silhouette
    draw.rectangle([x0 + 12, y1 - 26, x0 + 70, y1 - 6], fill=(20, 16, 20))
    draw.rectangle([x0 + 20, y1 - 40, x0 + 28, y1 - 26], fill=(20, 16, 20))
    draw.rectangle([x0 + 76, y1 - 22, x0 + 130, y1 - 6], fill=(20, 16, 20))
    draw.rectangle([x0 + 84, y1 - 34, x0 + 90, y1 - 22], fill=(20, 16, 20))
    # flames + smoke
    flame(draw, x0 + 44, y1 - 24, 30, 26)
    flame(draw, x0 + 100, y1 - 20, 24, 22)
    smoke(draw, [
        (x0 + 44, y0 + 12, 8, (60, 56, 62)),
        (x0 + 60, y0 + 8, 9, (76, 72, 78)),
        (x0 + 100, y0 + 10, 8, (60, 56, 62)),
    ])
    chip(draw, x0 + 4, y0 + 4, "26 DEAD", fill=RED, fnt_size=9)


def scene_treaty(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    vgrad(draw, x0, y0, x1, y1, (120, 190, 220), (200, 230, 240))
    # island
    draw.ellipse([x0 + 30, y1 - 18, x1 - 30, y1 + 6], fill=(96, 150, 80))
    draw.rectangle([x0, y1 - 8, x1, y1], fill=(40, 110, 160))
    # two flag poles
    for fx, col in ((x0 + 60, (0, 40, 120)), (x0 + 120, (0, 90, 60))):
        draw.line([(fx, y0 + 8), (fx, y1 - 12)], fill=(60, 50, 40), width=2)
        draw.rectangle([fx, y0 + 8, fx + 26, y0 + 22], fill=col)
        draw.ellipse([fx + 4, y0 + 12, fx + 9, y0 + 17], fill=CREAM)
    chip(draw, x0 + 4, y0 + 4, "SIGNED", fill=TEAL, fnt_size=9)


def scene_hostages(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(210, 205, 190))
    # storefront with striped awning
    draw.rectangle([x0 + 14, y0 + 18, x1 - 14, y1 - 6], fill=(240, 236, 222),
                   outline=(120, 110, 90), width=1)
    for i in range(6):
        col = RED if i % 2 == 0 else CREAM
        draw.polygon([(x0 + 14 + i * 26, y0 + 18), (x0 + 40 + i * 26, y0 + 18),
                      (x0 + 40 + i * 26, y0 + 28), (x0 + 14 + i * 26, y0 + 28)],
                     fill=col)
    draw.rectangle([x0 + 30, y0 + 32, x0 + 74, y1 - 6], fill=(60, 90, 120))
    draw.rectangle([x0 + 96, y0 + 32, x1 - 30, y1 - 6], fill=(60, 90, 120))
    # green shield with check
    sx, sy = x1 - 34, y0 + 30
    draw.polygon([(sx, sy), (sx + 22, sy), (sx + 22, sy + 12),
                  (sx + 11, sy + 24), (sx, sy + 12)], fill=(0, 140, 80))
    draw.line([(sx + 5, sy + 11), (sx + 9, sy + 15), (sx + 17, sy + 6)],
              fill=CREAM, width=2)


def scene_protein(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(18, 26, 44))
    # DNA helix: two sine strands + rungs
    cx = x0 + int(w * 0.42)
    amp, per = 14, 26
    pts1, pts2 = [], []
    for yy in range(y0 + 4, y1 - 4):
        t = (yy - y0) / per * math.pi
        pts1.append((cx + amp * math.sin(t), yy))
        pts2.append((cx - amp * math.sin(t), yy))
    draw.line(pts1, fill=(120, 200, 230), width=2)
    draw.line(pts2, fill=(255, 150, 90), width=2)
    for yy in range(y0 + 8, y1 - 6, 13):
        t = (yy - y0) / per * math.pi
        x1p = cx + amp * math.sin(t)
        x2p = cx - amp * math.sin(t)
        draw.line([(x1p, yy), (x2p, yy)], fill=(180, 180, 200), width=1)
    chip(draw, x0 + 30, y1 - 18, "GPT-6", fill=NAVY, fnt_size=9)


def scene_drones(draw, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    vgrad(draw, x0, y0, x1, y1, (220, 190, 140), (190, 150, 100))
    # ground + buildings
    draw.rectangle([x0, y1 - 12, x1, y1], fill=(150, 115, 70))
    draw.rectangle([x0 + 12, y1 - 26, x0 + 52, y1 - 12], fill=(120, 92, 58))
    draw.rectangle([x0 + 130, y1 - 22, x0 + 176, y1 - 12], fill=(120, 92, 58))
    # drone silhouette
    dx, dy = x0 + 96, y0 + 16
    draw.ellipse([dx - 8, dy - 3, dx + 8, dy + 3], fill=(30, 30, 36))
    for ox, oy in ((-16, -6), (16, -6), (-16, 6), (16, 6)):
        draw.line([(dx, dy), (dx + ox, dy + oy)], fill=(30, 30, 36), width=2)
        draw.ellipse([dx + ox - 7, dy + oy - 2, dx + ox + 7, dy + oy + 2],
                     fill=(90, 90, 96))
    # explosion burst below
    ex, ey = x0 + 96, y1 - 16
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        draw.line([(ex, ey), (ex + 16 * math.cos(a), ey + 10 * math.sin(a))],
                  fill=(255, 140, 40), width=2)
    draw.ellipse([ex - 7, ey - 6, ex + 7, ey + 6], fill=(255, 200, 80))
    chip(draw, x0 + 4, y0 + 4, "19 KILLED", fill=RED, fnt_size=9)


SCENES = {
    "hormuz": scene_hormuz,
    "refineries": scene_refineries,
    "gaza": scene_gaza,
    "tiangong": scene_tiangong,
    "mine": scene_mine,
    "garment": scene_garment,
    "chip": scene_chip,
    "dow": scene_dow,
    "fire": scene_fire,
    "treaty": scene_treaty,
    "hostages": scene_hostages,
    "protein": scene_protein,
    "drones": scene_drones,
}


# =============================================================== lead cards
LEAD_Y0, LEAD_Y1 = 196, 420
CARD_W = 320
CARD_X = [16, 352, 688]


def lead_cards(draw):
    img_h = 112
    for i, lead in enumerate(S.LEADS):
        x0 = CARD_X[i]
        x1 = x0 + CARD_W
        # illustration
        SCENES[lead["scene"]](draw, x0, LEAD_Y0, x1, LEAD_Y0 + img_h)
        num_disc(draw, x0 + 14, LEAD_Y0 + img_h - 12, lead["num"], r=10)
        # badge at the top-right of the illustration
        bw = draw.textlength(lead["badge"], font=font(SANS_B, 9)) + 10
        badge(draw, x1 - bw - 6, LEAD_Y0 + 6, lead["badge"])
        # kicker + location
        yy = LEAD_Y0 + img_h + 6
        kicker = font(SANS_B, 10)
        draw.text((x0, yy), lead["kicker"], font=kicker, fill=RED)
        yy += 14
        loc = font(SANS_B, 9)
        draw.text((x0, yy), lead["location"], font=loc, fill=GREY)
        yy += 13
        # headline (up to 3 lines)
        head = font(SERIF_B, 19)
        for ln in wrap(draw, lead["headline"], head, CARD_W):
            draw.text((x0, yy), ln, font=head, fill=INK)
            yy += 23
        # body, 2 lines
        body = font(SANS, 11.5)
        rich_para(draw, x0, yy + 2, CARD_W,
                  [(lead["body"], body, INK)], 14)
        if i < 2:
            draw.line([(x1 + 8, LEAD_Y0), (x1 + 8, LEAD_Y1)], fill=RULE,
                      width=1)


# ============================================================== small cards
CARD_ROWS = [(428, 548), (554, 674)]
SMALL_W = 192
SMALL_X = [16, 216, 416, 616, 816]


def small_cards(draw):
    img_h = 52
    for idx, card in enumerate(S.CARDS):
        row, col = divmod(idx, 5)
        y0, y1 = CARD_ROWS[row]
        x0 = SMALL_X[col]
        x1 = x0 + SMALL_W
        num, loc, head_txt, body_txt, badge_txt, scene = card
        SCENES[scene](draw, x0, y0, x1, y0 + img_h)
        num_disc(draw, x0 + 12, y0 + img_h - 11, num, r=9)
        bw = draw.textlength(badge_txt, font=font(SANS_B, 9)) + 10
        badge(draw, x1 - bw - 4, y0 + 4, badge_txt)
        yy = y0 + img_h + 4
        loc_f = font(SANS_B, 8)
        draw.text((x0, yy), loc, font=loc_f, fill=RED)
        yy += 11
        head = font(SANS_B, 11)
        for ln in wrap(draw, head_txt, head, SMALL_W):
            draw.text((x0, yy), ln, font=head, fill=INK)
            yy += 13
        body = font(SANS, 10)
        rich_para(draw, x0, yy + 1, SMALL_W, [(body_txt, body, INK)], 12)


# ---------------------------------------------------------------- world map
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 16, 700, 420, 936
LON0, LON1, LAT0, LAT1 = -170.0, 190.0, 78.0, -58.0


def project(lon, lat):
    x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_Y1 - MAP_Y0)
    return (x, y)


NORTH_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 59), (-145, 60),
                 (-135, 58), (-130, 54), (-127, 50), (-124, 48), (-124, 40),
                 (-121, 34), (-117, 33), (-112, 29), (-108, 25), (-105, 20),
                 (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
                 (-80, 8), (-77, 8), (-79, 9), (-81, 13), (-83, 15),
                 (-86, 16), (-88, 18), (-87, 21), (-90, 21), (-91, 19),
                 (-96, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
                 (-81, 25), (-80, 32), (-76, 35), (-74, 39), (-70, 42),
                 (-68, 44), (-65, 44), (-60, 46), (-65, 50), (-60, 52),
                 (-64, 58), (-68, 58), (-72, 62), (-78, 62), (-85, 66),
                 (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
                 (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
             (-22, 70), (-20, 76), (-30, 78), (-45, 78), (-55, 76),
             (-58, 70)]
SOUTH_AMERICA = [(-79, 9), (-77, 4), (-75, 0), (-80, -3), (-81, -6),
                 (-77, -12), (-72, -18), (-70, -23), (-70, -30), (-72, -37),
                 (-73, -44), (-74, -50), (-70, -54), (-66, -55), (-68, -50),
                 (-65, -45), (-62, -41), (-58, -35), (-52, -32), (-48, -28),
                 (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
                 (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9),
                 (-68, 11), (-72, 12), (-75, 11)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
          (-2, 50), (0, 51), (3, 52), (5, 53), (8, 55), (8, 57), (10, 59),
          (12, 56), (18, 56), (21, 55), (21, 59), (24, 59), (28, 60),
          (30, 62), (28, 59), (24, 58), (22, 56), (20, 54), (19, 50),
          (16, 46), (14, 45), (12, 44), (8, 44), (6, 43), (3, 42),
          (0, 40), (-2, 37), (-6, 36)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1),
          (12, -5), (13, -10), (12, -18), (14, -22), (12, -28), (16, -29),
          (18, -34), (20, -35), (26, -34), (28, -32), (32, -29), (35, -24),
          (36, -20), (40, -15), (40, -10), (42, -4), (44, 0), (46, 2),
          (48, 5), (51, 11), (48, 11), (44, 12), (43, 12), (40, 15),
          (38, 20), (37, 22), (35, 28), (34, 31), (32, 31), (28, 32),
          (22, 33), (19, 33), (15, 32), (11, 34), (10, 37), (6, 37),
          (0, 36)]
ASIA = [(28, 42), (30, 46), (35, 50), (40, 55), (45, 58), (50, 60),
        (55, 62), (60, 65), (65, 68), (70, 70), (75, 72), (80, 73),
        (90, 75), (100, 76), (110, 74), (120, 73), (130, 72), (140, 72),
        (150, 70), (158, 69), (162, 66), (170, 66), (178, 65), (178, 62),
        (170, 60), (162, 58), (158, 52), (155, 50), (150, 45), (145, 42),
        (142, 40), (140, 38), (138, 35), (135, 33), (132, 34), (130, 35),
        (128, 38), (126, 40), (124, 40), (122, 38), (120, 35), (118, 32),
        (116, 30), (114, 28), (112, 25), (110, 21), (108, 18), (106, 15),
        (105, 10), (104, 8), (103, 5), (101, 8), (99, 12), (97, 16),
        (94, 18), (92, 21), (89, 22), (86, 20), (84, 18), (81, 16),
        (79, 12), (77, 8), (75, 12), (73, 16), (71, 20), (68, 22),
        (66, 25), (62, 25), (59, 25), (57, 26), (55, 26), (53, 27),
        (51, 28), (49, 30), (47, 30), (45, 29), (43, 29), (41, 30),
        (39, 31), (37, 33), (36, 36), (34, 36), (31, 36), (29, 38)]
SUMATRA = [(95, 5), (98, 3), (100, 0), (102, -2), (104, -4), (106, -6),
           (104, -5), (102, -3), (100, 0), (97, 4)]
JAVA = [(105, -6), (108, -7), (110, -7), (112, -7), (114, -8), (114, -9),
        (111, -8), (108, -8), (106, -7)]
BORNEO = [(109, 1), (111, 3), (113, 4), (116, 6), (118, 2), (117, -1),
          (116, -3), (114, -4), (111, -3), (109, 0)]
NEW_GUINEA = [(131, -1), (134, -2), (137, -3), (140, -4), (141, -8),
              (141, -9), (138, -8), (135, -5), (132, -3)]
SULAWESI = [(119, 0), (121, 1), (120, -1), (119, -3), (120, -5), (121, -3),
            (120, 0)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
         (141, 39), (141, 41), (142, 43), (144, 44), (141, 45), (140, 42),
         (139, 38), (137, 36), (135, 34), (132, 33)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-3, 50)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
             (129, -32), (132, -32), (135, -35), (137, -35), (140, -38),
             (144, -39), (147, -39), (150, -37), (153, -32), (153, -27),
             (151, -24), (149, -20), (146, -19), (143, -15), (142, -11),
             (141, -13), (139, -15), (137, -12), (136, -15), (135, -12),
             (132, -11), (130, -13), (128, -14), (126, -14), (124, -17),
             (122, -17), (120, -19), (117, -20), (114, -22)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -41), (175, -38), (177, -38),
               (175, -40), (173, -42), (170, -44), (167, -46)]

CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EUROPE, AFRICA,
              ASIA, SUMATRA, JAVA, BORNEO, NEW_GUINEA, SULAWESI, JAPAN,
              UK, AUSTRALIA, NEW_ZEALAND]


def world_map(draw):
    sec = font(SANS_B, 13)
    draw.text((16, 682), "WHERE IT HAPPENED", font=sec, fill=INK)
    note = font(SANS, 10)
    draw.text((180, 685), "numbers match the stories", font=note, fill=GREY)
    rule(draw, 698, width=1, fill=RULE)
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=OCEAN)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=SAGE, outline=SAGE_DK)
    for lon in (-120, -60, 0, 60, 120):
        x = project(lon, 0)[0]
        draw.line([(x, MAP_Y0), (x, MAP_Y1)], fill=(200, 212, 214), width=1)
    num_f = font(SANS_B, 9)
    for num, lon, lat, nx, ny in S.PINS:
        x, y = project(lon, lat)
        if nx or ny:
            draw.line([(x, y), (x + nx, y + ny)], fill=RED, width=1)
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=RED)
            x, y = x + nx, y + ny
        r = 8
        draw.ellipse([x - r, y - r, x + r, y + r], fill=RED,
                     outline=(255, 255, 255), width=2)
        tw = draw.textlength(str(num), font=num_f)
        draw.text((x - tw / 2, y - 6), str(num), font=num_f,
                  fill=(255, 255, 255))
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=RULE, width=1)


# ------------------------------------------------------------- IN BRIEF list
def in_brief(draw):
    x0 = 436
    col_w = 278
    cols = [x0, x0 + col_w + 16]
    sec = font(SANS_B, 13)
    draw.text((x0, 682), "IN BRIEF — 37 MORE FROM 25 NOVEMBER", font=sec,
              fill=RED)
    f_num = font(SANS_B, 9.5)
    f_txt = font(SANS, 9.5)
    items = S.BRIEF
    per_col = (len(items) + 1) // 2
    for ci in range(2):
        xx = cols[ci]
        yy = 702
        for num, txt in items[ci * per_col:(ci + 1) * per_col]:
            draw.text((xx, yy), str(num), font=f_num, fill=RED)
            draw.text((xx + 20, yy), txt, font=f_txt, fill=INK)
            yy += 12.5


# ------------------------------------------------------------------- footer
def footer(draw):
    rule(draw, 942, width=1, fill=RULE)
    lab = font(SANS_B, 10)
    txt = font(SANS, 10)
    lab_txt = "DATE CHECK   "
    lw = draw.textlength(lab_txt, font=lab)
    draw.text((16, 948), lab_txt, font=lab, fill=RED)
    rich_para(draw, 16 + lw, 948, 1008 - 16 - lw,
              [(S.DATE_CHECK, txt, INK)], 12.5)
    leg = font(SANS, 9)
    rich_para(draw, 16, 976, 976, [(S.LEGEND, leg, GREY)], 11)
    src = font(SANS, 9)
    rich_para(draw, 16, 988, 976, [(S.SOURCES, src, GREY)], 11)
    foot = font(SERIF_IT, 10)
    centre(draw, 1008,
           "The Wednesday Globe  •  All stories verified for 25 November 2026",
           foot, GREY)


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(draw)
    stat_strip(draw)
    region_counts(draw)
    timeline(draw)
    lead_cards(draw)
    small_cards(draw)
    world_map(draw)
    in_brief(draw)
    footer(draw)
    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    build(target)
    data = open(target, "rb").read()
    print(f"{target}: {len(data)} bytes sha256 "
          f"{hashlib.sha256(data).hexdigest()}")
