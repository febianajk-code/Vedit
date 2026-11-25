# Flat motion graphic: Hukum-Hukum Newton (Indonesian), ~7 minutes, 1280x720 @24fps
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W, H = 1280, 720
FPS = 24
FF = imageio_ffmpeg.get_ffmpeg_exe()

F_CACHE = {}
def F(name, size):
    key = (name, size)
    if key not in F_CACHE:
        F_CACHE[key] = ImageFont.truetype(f"fonts/{name}.ttf", size)
    return F_CACHE[key]
FB = lambda s: F("Poppins-Bold", s)
FS = lambda s: F("Poppins-SemiBold", s)
FR = lambda s: F("Poppins-Regular", s)

BG    = (23, 29, 57)
CARD  = (36, 45, 84)
CARD2 = (30, 38, 72)
INK   = (245, 248, 255)
MUT   = (164, 176, 214)
YEL   = (255, 199, 88)
RED   = (255, 111, 97)
GRN   = (96, 214, 158)
BLU   = (104, 165, 255)
PUR   = (186, 132, 255)
DARK  = (12, 16, 36)

def clamp01(x): return max(0.0, min(1.0, x))
def eo(x): x = clamp01(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp01(x); return x * x * (3 - 2 * x)
def pingpong(t, period):
    p = (t % period) / period
    return p if p < 0.5 else 1 - p

def mixc(c, k):  # blend color toward BG by k (fake fade)
    k = clamp01(k)
    return tuple(int(c[i] + (BG[i] - c[i]) * k) for i in range(3))

def pop(t, t0, dur=0.5):
    """returns (visible, scale)"""
    if t < t0: return False, 0.0
    p = clamp01((t - t0) / dur)
    if p < 0.8: return True, eo(p / 0.8) * 1.0
    return True, 1.0 + 0.04 * math.sin(math.pi * (p - 0.8) / 0.2)

def fal(t, t0, dur=0.6):
    return 1 - eo((t - t0) / dur)   # fade factor for mixc k

def scaled_text(d, xy, s, fnc, size, fill, scale=1.0, anchor="mm", is_bold=False):
    if scale <= 0.02: return
    if abs(scale - 1.0) < 0.02:
        d.text(xy, s, font=fnc(size), fill=fill, anchor=anchor)
    else:
        fnt = ImageFont.truetype(f"fonts/{'Poppins-Bold' if is_bold else 'Poppins-SemiBold'}.ttf",
                                 max(4, int(size * scale)))
        d.text(xy, s, font=fnt, fill=fill, anchor=anchor)

def arrow(d, x0, y0, x1, y1, color, w=7, head=20):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx = x1 - head * 0.85 * math.cos(ang); by = y1 - head * 0.85 * math.sin(ang)
    d.line([x0, y0, bx, by], fill=color, width=w)
    a1 = ang + math.pi * 0.80; a2 = ang - math.pi * 0.80
    d.polygon([(x1, y1),
               (x1 + head * math.cos(a1), y1 + head * math.sin(a1)),
               (x1 + head * math.cos(a2), y1 + head * math.sin(a2))], fill=color)

def ball(d, cx, cy, r, color, k=0.0):
    c1 = mixc(color, k); c2 = mixc(tuple(min(255, v + 45) for v in color), k)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c1)
    d.ellipse([cx - r * 0.45, cy - r * 0.55, cx + r * 0.1, cy - r * 0.05], fill=c2)

def cart(d, x, y, w, h, color, label=None, k=0.0):
    # x,y = left,top of body; wheels below
    wy = y + h + 10
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=mixc(color, k))
    for wx in (x + w * 0.22, x + w * 0.78):
        d.ellipse([wx - 13, wy - 13, wx + 13, wy + 13], fill=mixc(DARK, k * 0.6), outline=mixc(MUT, k), width=3)
    if label:
        d.text((x + w / 2, y + h / 2), label, font=FS(24), fill=mixc(DARK, k), anchor="mm")

def ground(d, x0, x1, y, k=0.0):
    d.line([x0, y, x1, y], fill=mixc(MUT, k + 0.35), width=5)
    for i in range(int((x1 - x0) / 34) + 1):
        gx = x0 + i * 34
        d.line([gx, y + 4, gx - 10, y + 13], fill=mixc(MUT, k + 0.55), width=3)

def person(d, x, fy, s, col, lean=0.0, k=0.0, pushlen=46):
    hr = 11 * s
    hx = x + lean * 18 * s; hy = fy - (70 + lean * 6) * s
    neck = (x + lean * 10 * s, fy - 58 * s)
    hip = (x + lean * 2 * s, fy - 32 * s)
    d.line([neck, hip], fill=mixc(col, k), width=int(7 * s))
    d.line([hip, (x - 12 * s, fy)], fill=mixc(col, k), width=int(6 * s))
    d.line([hip, (x + 13 * s, fy - 3 * s)], fill=mixc(col, k), width=int(6 * s))
    for a in (-0.5, 0.35):
        ex = neck[0] + pushlen * s * math.cos(a); ey = neck[1] + pushlen * s * math.sin(a)
        d.line([neck, (ex, ey)], fill=mixc(col, k), width=int(6 * s))
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=mixc(col, k))

def chip(d, cx, cy, text, fnt, fg, bgc, padx=22, pady=10, k=0.0):
    tw = d.textlength(text, font=fnt)
    bh = fnt.size + pady * 2
    bb = [cx - tw / 2 - padx, cy - bh / 2, cx + tw / 2 + padx, cy + bh / 2]
    d.rounded_rectangle(bb, radius=bh / 2, fill=mixc(bgc, k))
    d.text((cx, cy), text, font=fnt, fill=mixc(fg, k), anchor="mm")
    return bb

def apple(d, cx, cy, r, k=0.0):
    ball(d, cx, cy, r, RED, k)
    d.ellipse([cx - r * 0.42, cy - r * 0.52, cx - r * 0.02, cy - r * 0.12], fill=mixc((255, 150, 130), k))
    d.line([cx, cy - r + 4, cx + 3, cy - r - 12], fill=mixc((120, 85, 60), k), width=6)
    d.ellipse([cx + 4, cy - r - 20, cx + 30, cy - r - 2], fill=mixc(GRN, k))

def subpill(d, beats, t, base_col=YEL):
    for (t0, t1, lines) in beats:
        if t0 <= t < t1:
            local = t - t0
            fnt = FR(26); lh = 36
            budget = int(local * 34 + 2)
            shown = []
            for L in lines:
                n = max(0, budget); take = L[:n]; shown.append(take); budget -= len(L)
                if budget <= 0: break
            while shown and not shown[-1]: shown.pop()
            if not shown: shown = [" "]
            maxw = max(v for v in [d.textlength(L, font=fnt) for L in lines]) + 56
            cx, cy = W / 2, H - 96
            hh = lh * len(lines) + 22
            top = cy - hh / 2
            d.rounded_rectangle([cx - maxw / 2, top, cx + maxw / 2, top + hh],
                                radius=16, fill=DARK, outline=mixc(base_col, 0.3), width=2)
            d.rectangle([cx - maxw / 2 + 10, top + 12, cx - maxw / 2 + 16, top + hh - 12], fill=base_col)
            for i, L in enumerate(shown):
                d.text((cx + 10, top + 22 + lh * i), L, font=fnt, fill=INK, anchor="mm")
            return

def hud(d, abs_t, total_t, scene_names, scene_idx, scene_t, scene_T):
    # progress bar
    x0, x1, y = 60, W - 60, H - 26
    d.rounded_rectangle([x0, y, x1, y + 8], radius=4, fill=CARD)
    frac = (abs_t / total_t)
    fx = x0 + (x1 - x0) * frac
    d.rounded_rectangle([x0, y, fx, y + 8], radius=4, fill=YEL)
    n = len(scene_names)
    for i in range(n):
        px = x0 + (x1 - x0) * (sum(SCENE_DUR[:i]) / total_t)
        d.ellipse([px - 4, y + 2, px + 4, y + 10], fill=BG if i > scene_idx else (INK if i < scene_idx else YEL))
    d.text((x0, y - 22), f"{scene_names[scene_idx]}", font=FS(17), fill=mixc(MUT, 0.15), anchor="lm")
    d.text((W - 60, y - 22), f"{int(abs_t // 60)}:{int(abs_t % 60):02d} / {int(total_t // 60)}:{int(total_t % 60):02d}",
           font=FR(16), fill=mixc(MUT, 0.3), anchor="rm")

FLOATERS = [(0.13, 0.2, 70, 26), (0.31, 0.7, 40, -16), (0.48, 0.35, 90, 20), (0.66, 0.8, 52, -13),
            (0.82, 0.5, 66, 18), (0.93, 0.25, 38, -20), (0.21, 0.85, 46, 12), (0.59, 0.12, 58, -15)]

def backdrop(d, abs_t):
    d.rectangle([0, 0, W, H], fill=BG)
    for i, (fx, fy, rr_, sp) in enumerate(FLOATERS):
        bx = (fx * W + sp * abs_t) % (W + 240) - 120
        by = fy * H + math.sin(abs_t * 0.4 + i * 1.7) * 26
        col = mixc((58, 68, 118), 0.42)
        if i % 2 == 0:
            d.ellipse([bx - rr_, by - rr_, bx + rr_, by + rr_], outline=col, width=2)
        else:
            sz = rr_ * 0.7
            ang = abs_t * 0.2 + i
            pts = [(bx + sz * math.cos(ang + a), by + sz * math.sin(ang + a)) for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
            d.polygon(pts, fill=col)

# ---------- scenes ----------
def s0(d, t, T, at):  # INTRO (25s)
    # falling apple
    ft = clamp01((t - 0.3) / 1.4)
    ay = -80 + (300 + 80) * eo(ft) + math.sin(t * 1.4) * 6 * (ft > 0.99 or ft > 0.98)
    apr = 1.0
    sh_k = clamp01(1 - (t - 1.7) / 1.2)
    if sh_k > 0:
        d.ellipse([480, 330, 800, 360], fill=mixc((15, 20, 44), 0.0))
    apple(d, 640, ay, 52)

    p = eo((t - 2.3) / 0.9)
    scaled_text(d, (W / 2, 470), "HUKUM-HUKUM NEWTON", FB, 76, mixc(INK, fal(t, 2.3, 0.9)),
                scale=0.85 + 0.15 * p, is_bold=True)
    k = fal(t, 4.2, 0.8)
    d.text((W / 2, 540), "Memahami Gaya & Gerak dengan Cara Sederhana", font=FS(30), fill=mixc(MUT, k), anchor="mm")
    for i, (lbl, col) in enumerate((("I", BLU), ("II", GRN), ("III", PUR))):
        vis, sc = pop(t, 6.1 + i * 0.7, 0.55)
        if vis:
            cx = 400 + i * 240
            fnt = FS(26); tw = d.textlength(lbl, font=fnt)
            d.rounded_rectangle([cx - tw / 2 - 26, 596 - 24, cx + tw / 2 + 26, 596 + 24],
                                radius=24, fill=mixc(col, fal(t, 6.1 + i * 0.7, 0.55)),
                                outline=mixc(INK, 0.6 + 0.4 * fal(t, 6.1 + i * 0.7, 0.55)), width=0)
            d.text((cx, 596), lbl, font=fnt, fill=mixc(DARK, fal(t, 6.1 + i * 0.7, 0.55)), anchor="mm")
            d.text((cx, 640), ("Inersia", "F = m · a", "Aksi-Reaksi")[i], font=FR(20),
                   fill=mixc(MUT, fal(t, 7.1 + i * 0.7, 0.55)), anchor="mm")
    d.text((W / 2, 688), "FISIKA • GERAK & GAYA", font=FS(18), fill=mixc(MUT, 0.45), anchor="mm")

BEATS0 = [
    (0.5, 6.2, ["Pernahkah kamu bertanya, mengapa benda bisa bergerak?"]),
    (6.2, 12.5, ["Lebih dari 300 tahun yang lalu, Isaac Newton", "menjawabnya dengan tiga hukum sederhana."]),
    (12.5, 19.5, ["Dalam video ini, kita akan mempelajari ketiga", "hukum itu lewat animasi yang mudah dipahami."]),
    (19.5, 25.0, ["Siap? Mari kita mulai!"]),
]

def s1(d, t, T, at):  # APA ITU GAYA (45s)
    k1 = fal(t, 0.2, 0.7)
    px0, py0, px1, py1 = 150, 120, W - 150, 560
    d.rounded_rectangle([px0, py0, px1, py1], radius=26, fill=mixc(CARD2, k1))
    d.text((W / 2, 168), "APA ITU GAYA?", font=FB(40), fill=mixc(YEL, k1), anchor="mm")
    d.text((W / 2, 222), "Gaya adalah tarikan atau dorongan pada sebuah benda",
           font=FR(26), fill=mixc(INK, fal(t, 1.2, 0.7)), anchor="mm")

    # left mini scene: push
    k = fal(t, 6, 0.7)
    bx = 210 + 26 * math.sin(t * 2.0)
    ground(d, 190, 590, 430, k)
    d.rounded_rectangle([470 + bx - 470, 355, 560 + bx - 470, 430], radius=10, fill=mixc(BLU, k))
    person(d, 360 + bx - 470 + 96 * math.sin(t * 2) * 0.3, 430, 0.9, YEL, lean=0.25, k=k)
    p1 = eo((t - 8) / 0.8)
    if p1 > 0: arrow(d, 575 + bx - 470, 392, 575 + bx - 470 + 80 * p1, 392, mixc(YEL, k), w=8)
    d.text((500 + bx - 470, 470), "Dorongan", font=FS(22), fill=mixc(INK, k), anchor="mm")

    # right mini scene: pull
    k = fal(t, 11, 0.7)
    bx2 = 0 - 26 * math.sin(t * 2.0)
    ground(d, 690, 1090, 430, k)
    d.rounded_rectangle([900 + bx2, 355, 990 + bx2, 430], radius=10, fill=mixc(GRN, k))
    sw = 40 * math.sin(t * 2.0)
    d.line([990 + bx2, 392, 1040 + bx2 + sw, 392], fill=mixc(MUT, k), width=5)
    d.ellipse([1038 + bx2 + sw - 11, 392 - 26, 1038 + bx2 + sw + 11, 392 - 4], fill=mixc(YEL, k))
    p2 = eo((t - 13) / 0.8)
    if p2 > 0: arrow(d, 1040 + bx2 + sw, 330, 1040 + bx2 + sw + 80 * p2, 330, mixc(GRN, k), w=8)
    d.text((945 + bx2, 470), "Tarikan", font=FS(22), fill=mixc(INK, k), anchor="mm")

    # pills
    for i, (txt, col) in enumerate((("Simbol :  F", YEL), ("Satuan :  Newton (N)", GRN), ("Vektor :  punya besar & arah", PUR))):
        vis, _ = pop(t, 26 + i * 2.6, 0.6)
        if vis:
            fnt = FS(24)
            tw = d.textlength(txt, font=fnt)
            cxs = (295, 640, 985)
            tw2 = min(tw + 52, 330)
            bb = [cxs[i] - tw2 / 2, 512, cxs[i] + tw2 / 2, 552]
            d.rounded_rectangle(bb, radius=20, fill=mixc(CARD, fal(t, 26 + i * 2.6, 0.6)),
                                outline=mixc(col, fal(t, 26 + i * 2.6, 0.6)), width=3)
            d.text((cxs[i], 532), txt, font=fnt, fill=mixc(col, fal(t, 26 + i * 2.6, 0.6)), anchor="mm")
    # vector arrow for last pill
    p3 = eo((t - 33) / 0.9)
    if p3 > 0:
        arrow(d, 1120, 545 - p3 * 40, 1195, 545 - p3 * 90, mixc(PUR, fal(t, 33, 0.9)), w=7)
        d.text((1176, 480), "F", font=FB(26), fill=mixc(PUR, fal(t, 33, 0.9)), anchor="mm")

BEATS1 = [
    (0.3, 7.5, ["Gaya adalah tarikan atau dorongan pada sebuah benda."]),
    (7.5, 12.2, ["Gaya tidak terlihat, tetapi efeknya bisa kita rasakan."]),
    (12.2, 25.0, ["Dorongan dan tarikan sama-sama merupakan gaya."]),
    (25.0, 33.5, ["Gaya disimbolkan dengan huruf F,", "dan satuannya adalah Newton (N)."]),
    (33.5, 45.0, ["Gaya juga besaran vektor — ia punya besar dan arah."]),
]

def s2(d, t, T, at):  # HUKUM I (62s)
    k0 = fal(t, 0.2, 0.7)
    chip(d, 250, 78, "HUKUM I NEWTON", FS(24), DARK, BLU, k=k0)
    d.rounded_rectangle([90, 118, W - 90, 216], radius=20, fill=mixc(CARD2, k0))
    d.text((W / 2, 166), "\u201cJika resultan gaya nol, benda diam tetap diam", font=FS(26), fill=mixc(INK, k0), anchor="mm")
    d.text((W / 2, 200), "dan benda bergerak tetap bergerak lurus.\u201d", font=FS(26), fill=mixc(INK, k0), anchor="mm")

    stages = [(0.0, 22.0, 0), (20.0, 41.0, 1), (38.5, 62.0, 2)]
    def off_in(t0, dur=0.8):
        p = eo((t - t0) / dur); return (1 - p) * 130, 1 - p
    act = [s for s in stages if s[0] - 0.05 <= t < s[1] + 1.0]
    for (s0t, s1t, idx) in sorted(act, key=lambda st: st[0], reverse=True):
        oi, ki = off_in(s0t)
        oo, ko = 0, 0
        p = eo((t - (s1t - 0.8)) / 0.9)
        if 0 < p < 1: oo, ko = -p * 130, p * 0.85
        ox, kfade = oi if t < s1t - 0.8 else max(oi, oo), min(ki, ko) if t < s1t - 0.8 else ko
        if idx == 0: s2_p1(d, t, ox, kfade, at)
        elif idx == 1: s2_p2(d, t, ox, kfade, at)
        else: s2_p3(d, t, ox, kfade, at)

def s2_p1(d, t, ox, k, at):  # bal with balanced forces
    d.rounded_rectangle([90 + ox, 240, W - 90 + ox, 560], radius=22, fill=mixc(CARD, k))
    ground(d, 170 + ox, 560 + ox, 480, k)
    bx, by, r = 380 + ox, 480 - 34, 34
    ball(d, bx, by, r, BLU, k)
    p = eo((t - 7) / 0.9)
    if p > 0:
        arrow(d, bx - 34 - 110 * p + 0, by, bx - 34 - 34, by, mixc(RED, k), w=7)
        arrow(d, bx + 34 + 34 - 76 * (1 - p) - p * 0, by, bx + 34 + 110 * p, by, mixc(RED, k), w=7)
    kp = fal(t, 10, 0.6)
    chip(d, 620 + ox, 320, "\u03a3F = 0  \u2192  benda TETAP DIAM", FS(24), INK, mixc(CARD, 0.0), k=k)
    d.text((620 + ox, 372), "semua gaya saling meniadakan", font=FR(21), fill=mixc(MUT, k), anchor="mm")

def s2_p2(d, t, T, k, at):
    d.rounded_rectangle([90, 240, W - 90, 560], radius=22, fill=mixc(CARD, k))
    ground(d, 170, 1130, 480, k)
    cyc = pingpong(t - 20, 7.0) / 0.5
    cx = 200 + cyc * 620
    cart(d, cx, 396, 190, 70, GRN, "v tetap", k=k)
    p = eo((t - 23) / 0.9)
    if p > 0:
        arrow(d, cx + 95, 430, cx + 95 + 90 * p, 430, mixc(YEL, k), w=7)
        arrow(d, cx + 95 + 90 * p - 78 * (1 - p), 460, cx + 95, 460, mixc(RED, k), w=7)
        d.text((cx + 150, 408), "dorong", font=FR(18), fill=mixc(YEL, k), anchor="mm")
        d.text((cx + 150, 484), "gesek", font=FR(18), fill=mixc(RED, k), anchor="mm")
    kp = fal(t, 26, 0.6)
    chip(d, 640, 320, "\u03a3F = 0  \u2192  kecepatan tetap, lurus", FS(24), INK, CARD, k=k)

def s2_p3(d, t, T, k, at):
    d.rounded_rectangle([90, 240, W - 90, 560], radius=22, fill=mixc(CARD, k))
    # bus + braking + passenger lurch
    ground(d, 150, 1130, 500, k)
    B = min(1.0, (t - 39.8) / 3.0)  # bus progress
    busx = 90 + B * 420
    brake = t > 46.5
    brkx = busx + (min(1.0, (t - 46.5) / 2.6)) * 190
    d.rounded_rectangle([busx, 350, busx + 340, 480], radius=16, fill=mixc(YEL, k))
    for i in range(3):
        d.rounded_rectangle([busx + 26 + i * 100, 375, busx + 96 + i * 100, 425], radius=8, fill=mixc((70, 90, 140), k))
    for wx in (busx + 70, busx + 270):
        d.ellipse([wx - 20, 470, wx + 20, 510], fill=mixc(DARK, k), outline=mixc(MUT, k), width=4)
    px = busx + 180 + (22 * math.sin(math.pi * clamp01((t - 47.2) / 1.6)) if brake else 0)
    d.ellipse([px - 14, 388, px + 14, 416], fill=mixc(BLU, k))
    d.rounded_rectangle([px - 13, 416, px + 13, 462], radius=8, fill=mixc(BLU, k))
    if brake:
        p = clamp01((t - 46.5) / 0.7)
        arrow(d, busx + 190, 330, busx + 190 + 70 * p, 330, mixc(RED, k), w=6)
        d.text((busx + 240, 300), "rem!", font=FB(26), fill=mixc(RED, k), anchor="mm")
        arrow(d, px, 372, px - 60 * p, 372, mixc(PUR, k), w=6)
        d.text((px - 60, 340), "badan maju", font=FS(19), fill=mixc(PUR, k), anchor="mm")
    kp = fal(t, 50, 0.7)
    chip(d, 640, 545, "Kaki berhenti bersama bus \u2014 badan kita \u201cingat\u201d kecepatan awal", FS(21), INK, CARD, k=k)

BEATS2 = [
    (0.3, 8.0, ["Hukum I Newton sering disebut Hukum Inersia."]),
    (8.0, 19.0, ["Kalau resultan gaya pada benda nol,", "benda yang diam akan tetap diam."]),
    (20.0, 36.0, ["Benda yang bergerak akan terus bergerak lurus", "dengan kecepatan tetap \u2014 selama tidak ada gaya resultan."]),
    (38.5, 49.0, ["Contohnya: saat bus direm mendadak,", "badan kita terdorong ke depan."]),
    (49.0, 62.0, ["Kaki berhenti bersama bus, tetapi badan kita masih", "\u201cingat\u201d kecepatan awalnya. Itulah inersia!"]),
]

def s3(d, t, T, at):  # HUKUM II (72s)
    k0 = fal(t, 0.2, 0.7)
    chip(d, 290, 78, "HUKUM II NEWTON", FS(24), DARK, GRN, k=k0)
    d.rounded_rectangle([90, 118, W - 90, 252], radius=20, fill=mixc(CARD2, k0))
    p = eo((t - 0.8) / 1.0)
    scaled_text(d, (W / 2, 172), "F  =  m  \u00d7  a", FB, 58, mixc(YEL, k0), scale=0.6 + 0.4 * p, is_bold=True)
    for i, (lbl, col) in enumerate((("F = gaya (N)", YEL), ("m = massa (kg)", INK), ("a = percepatan (m/s\u00b2)", RED))):
        vis, _ = pop(t, 2.6 + i * 0.5, 0.55)
        if vis:
            kk = fal(t, 2.6 + i * 0.5, 0.55)
            cx = 340 + i * 300
            fnt = FR(21); tw = d.textlength(lbl, font=fnt)
            d.rounded_rectangle([cx - tw / 2 - 18, 206, cx + tw / 2 + 18, 240], radius=16, fill=mixc(CARD, kk))
            d.text((cx, 223), lbl, font=fnt, fill=mixc(col, kk), anchor="mm")

    # demo: same F, different mass (two loop cycles 8-36)
    cyc = (t - 7.5) % 14.0
    kA = fal(t, 7.5, 0.6)
    d.rounded_rectangle([90, 278, W - 90, 452], radius=20, fill=mixc(CARD, kA))
    ground(d, 130, 1150, 428, kA)
    if t < 21.5 or t > 21.5:  # continuous demo
        pass
    prog = clamp01(cyc / 2.2)
    x1 = 330 + prog * 330
    x5 = 700 + prog * 56
    cart(d, x1, 358, 120, 60, GRN, "1 kg", k=kA)
    cart(d, x5, 338, 190, 82, RED, "5 kg", k=kA)
    for (x, wdt, col) in ((x1 + 120, 0, GRN), (x5 + 190, 0, RED)):
        pass
    pf = eo(clamp01((cyc - 0.2) / 0.8))
    if pf > 0 and cyc < 2.2:
        arrow(d, x1 + 120, 390, x1 + 120 + 84 * pf, 390, mixc(YEL, kA), w=7)
        arrow(d, x5 + 190, 380, x5 + 190 + 84 * pf, 380, mixc(YEL, kA), w=7)
        d.text((520, 315), "gaya yang SAMA", font=FS(21), fill=mixc(YEL, kA), anchor="mm")
    if prog >= 1:
        kp2 = 1 - clamp01((cyc - 2.2) / 0.6)
        chip(d, x1 + 60, 300, "a BESAR", FS(20), DARK, GRN, k=min(kA, 1 - kp2) * 1.0)
        chip(d, x5 + 95, 285, "a kecil", FS(20), INK, RED, k=min(kA, 1 - kp2) * 1.0)

    # graphs 36-60
    kg = fal(t, 36, 0.8)
    if t >= 36:
        for gi, (title, col, fn) in enumerate((
                ("a \u221d F   (massa tetap)", GRN, lambda u: u),
                ("a \u221d 1/m   (gaya tetap)", PUR, lambda u: 0.22 / max(u, 0.22)))):
            gx0, gy0 = 190 + gi * 560, 492
            gw, gh = 380, 118
            d.rounded_rectangle([gx0 - 40, gy0 - 62, gx0 + gw + 60, gy0 + gh + 40], radius=18, fill=mixc(CARD2, kg))
            d.text((gx0 + gw / 2 + 10, gy0 - 34), title, font=FS(21), fill=mixc(col, kg), anchor="mm")
            d.line([gx0, gy0 + gh, gx0 + gw, gy0 + gh], fill=mixc(MUT, kg + 0.2), width=3)
            d.line([gx0, gy0, gx0, gy0 + gh], fill=mixc(MUT, kg + 0.2), width=3)
            n_dots = 9
            for j in range(n_dots):
                u = (j + 0.5) / n_dots
                if u > clamp01((t - 37 - gi) / 8.0): break
                v = fn(u)
                vv = min(v, 1.0)
                ball(d, gx0 + u * gw, gy0 + gh - vv * gh, 7, col, kg)
    # closing strip
    kc = fal(t, 58, 0.7)
    if t >= 58:
        d.rounded_rectangle([90, 624, W - 90, 668], radius=18, fill=mixc(DARK, kc))
        d.text((W / 2, 646), "Gerobak kosong mudah dipercepat \u2022 gerobak penuh butuh gaya jauh lebih besar",
               font=FS(20), fill=mixc(YEL, kc), anchor="mm")

BEATS3 = [
    (0.3, 8.0, ["Hukum II menjawab: seberapa besar percepatan", "yang muncul karena gaya?"]),
    (8.0, 21.5, ["Dengan gaya yang sama, massa yang kecil", "menghasilkan percepatan yang BESAR."]),
    (21.5, 36.0, ["Sebaliknya, massa yang besar menghasilkan", "percepatan yang kecil."]),
    (36.0, 46.0, ["Percepatan sebanding dengan gaya,", "dan berbanding balik dengan massa."]),
    (46.0, 58.0, ["Satuan SI: massa kilogram, percepatan meter", "per sekon kuadrat, dan gaya dalam Newton."]),
    (58.0, 72.0, ["Itulah mengapa mendorong gerobak kosong", "jauh lebih mudah daripada yang penuh!"]),
]

def s4(d, t, T, at):  # HUKUM III (62s)
    k0 = fal(t, 0.2, 0.7)
    chip(d, 345, 78, "HUKUM III NEWTON", FS(24), DARK, PUR, k=k0)
    d.rounded_rectangle([90, 118, W - 90, 206], radius=20, fill=mixc(CARD2, k0))
    d.text((W / 2, 162), "\u201cSetiap aksi menimbulkan reaksi yang sama besar, berlawanan arah,",
           font=FS(25), fill=mixc(INK, k0), anchor="mm")
    d.text((W / 2, 194), "dan bekerja pada benda yang berbeda.\u201d", font=FS(25), fill=mixc(INK, k0), anchor="mm")

    def off_in(t0, dur=0.8):
        p = eo((t - t0) / dur); return (1 - p) * 130, 1 - p
    stages = [(6.0, 24.5, 0), (22.5, 43.0, 1), (41.0, 62.0, 2)]
    act = [s for s in stages if s[0] - 0.05 <= t < s[1] + 1.0]
    for (s0t, s1t, idx) in sorted(act, key=lambda st: st[0], reverse=True):
        oi, ki = off_in(s0t)
        oo, ko = 0, 0
        p = eo((t - (s1t - 0.8)) / 0.9)
        if 0 < p < 1: oo, ko = -p * 130, p * 0.85
        ox = oi if t < s1t - 0.8 else max(oi, oo)
        kf = min(ki, ko) if t < s1t - 0.8 else ko
        if idx == 0: s4_p1(d, t, ox, kf, at)
        elif idx == 1: s4_p2(d, t, ox, kf, at)
        else: s4_p3(d, t, ox, kf, at)

def s4_p1(d, t, ox, k, at):  # collide two balls
    d.rounded_rectangle([90 + ox, 230, W - 90 + ox, 560], radius=22, fill=mixc(CARD, k))
    ground(d, 170 + ox, 1110 + ox, 500, k)
    u = clamp01((t - 7.0) / 4.5)
    sep = (1 - eio(u)) * 420
    midy, r = 380, 42
    ball(d, 640 - sep / 2 - r + ox, midy, r, BLU, k)
    ball(d, 640 + sep / 2 + r + ox, midy, r, RED, k)
    if u >= 1:
        ko = 1 - clamp01((t - 12.5) / 1.2)
        if ko > 0:
            d.ellipse([640 - 60 + ox, midy - 60, 640 + 60 + ox, midy + 60], fill=mixc((255, 240, 200), (1 - ko) * 0.7))
            arrow(d, 640 - r - 8 + ox, midy, 640 - r - 118 * ko + ox, midy, mixc(PUR, k), w=7)
            arrow(d, 640 + r + 8 + ox, midy, 640 + r + 118 * ko + ox, midy, mixc(GRN, k), w=7)
            d.text((560 + ox, 300), "F reaksi", font=FS(20), fill=mixc(PUR, k), anchor="mm")
            d.text((722 + ox, 300), "F aksi", font=FS(20), fill=mixc(GRN, k), anchor="mm")
            chip(d, 640 + ox, 520, "sama besar \u2022 berlawanan arah \u2022 benda berbeda", FS(20), INK, CARD, k=k)
    else:
        d.text((560 + ox, 300), "\u2194", font=FB(40), fill=mixc(MUT, k), anchor="mm")

def s4_p2(d, t, ox, k, at):  # rocket
    d.rounded_rectangle([90 + ox, 230, W - 90 + ox, 560], radius=22, fill=mixc(CARD, k))
    rise = eo(clamp01((t - 34) / 5.5)) * 120
    rx, ry = 640 + ox, 405 - rise
    d.polygon([(rx - 34, ry - 30), (rx, ry - 92), (rx + 34, ry - 30)], fill=mixc(INK, k))
    d.rounded_rectangle([rx - 34, ry - 40, rx + 34, ry + 52], radius=12, fill=mixc(MUT, k))
    d.ellipse([rx - 13, ry - 6, rx + 13, ry + 20], fill=mixc(BLU, k))
    d.polygon([(rx - 34, ry + 28), (rx - 62, ry + 62), (rx - 34, ry + 48)], fill=mixc(RED, k))
    d.polygon([(rx + 34, ry + 28), (rx + 62, ry + 62), (rx + 34, ry + 48)], fill=mixc(RED, k))
    fl = 1.0 + 0.35 * math.sin(t * 22) + 0.2 * math.sin(t * 37)
    d.polygon([(rx - 18, ry + 54), (rx + 18, ry + 54), (rx, ry + 54 + 52 * fl)], fill=mixc(YEL, k))
    p = eo((t - 25.5) / 0.9)
    if p > 0:
        arrow(d, rx, ry + 90, rx, ry + 90 + 110 * p, mixc(RED, k), w=8)
        d.text((rx + 60, ry + 130), "aksi: gas ke bawah", font=FS(19), fill=mixc(RED, k), anchor="mm")
        arrow(d, rx, ry - 108, rx, ry - 108 - 110 * p, mixc(GRN, k), w=8)
        d.text((rx + 80, ry - 160), "reaksi: roket naik", font=FS(19), fill=mixc(GRN, k), anchor="mm")

def s4_p3(d, t, ox, k, at):  # swimmer
    d.rounded_rectangle([90 + ox, 230, W - 90 + ox, 560], radius=22, fill=mixc(CARD, k))
    d.rounded_rectangle([130 + ox, 280, 1150 + ox, 520], radius=18, fill=mixc((34, 62, 116), k))
    for i in range(6):
        wx = 200 + ((t * 60 + i * 180) % 950) + ox
        d.arc([wx, 300 + (i % 2) * 130, wx + 70, 340 + (i % 2) * 130], 200, 340, fill=mixc((90, 140, 210), k), width=4)
    sx = 640 + ox + 26 * math.sin(t * 1.8)
    sy = 400 + 10 * math.sin(t * 3.6)
    d.ellipse([sx - 16, sy - 46, sx + 16, sy - 14], fill=mixc(YEL, k))
    d.rounded_rectangle([sx - 30, sy - 14, sx + 34, sy + 22], radius=14, fill=mixc(YEL, k))
    d.line([sx + 20, sy, sx + 78 + 16 * math.sin(t * 3.6), sy - 8], fill=mixc(YEL, k), width=8)
    d.line([sx - 20, sy + 16, sx - 66, sy + 40 + 12 * math.sin(t * 3.6)], fill=mixc(YEL, k), width=8)
    p = eo((t - 44) / 0.9)
    if p > 0:
        arrow(d, sx + 110, sy - 60, sx + 110 + 100 * p, sy - 60, mixc(GRN, k), w=8)
        d.text((sx + 150, sy - 100), "tubuh maju", font=FS(20), fill=mixc(GRN, k), anchor="mm")
        arrow(d, sx - 90, sy + 30, sx - 90 - 90 * p, sy + 30, mixc(RED, k), w=8)
        d.text((sx - 160, sy + 66), "dorong air ke belakang", font=FS(19), fill=mixc(RED, k), anchor="mm")
    chip(d, 640 + ox, 540, "Aksi mendorong air \u2014 reaksi mendorong tubuh", FS(20), INK, CARD2, k=k)

BEATS4 = [
    (0.3, 7.0, ["Hukum III Newton: aksi dan reaksi."]),
    (7.0, 17.0, ["Ketika benda A memberi gaya pada benda B,", "benda B memberi gaya balik pada benda A."]),
    (17.0, 24.5, ["Keduanya sama besar, tetapi arahnya berlawanan."]),
    (24.5, 35.0, ["Contoh: roket mendorong gas panas ke bawah \u2014", "gas mendorong roket ke atas."]),
    (41.0, 51.0, ["Saat berenang, kaki mendorong air ke belakang,", "dan tubuh kita terdorong ke depan."]),
    (51.0, 62.0, ["Aksi dan reaksi bekerja pada benda berbeda,", "sehingga keduanya tidak saling meniadakan."]),
]

def s5(d, t, T, at):  # CONTOH SOAL (60s)
    k0 = fal(t, 0.2, 0.7)
    chip(d, 220, 78, "CONTOH SOAL", FS(24), DARK, YEL, k=k0)
    d.rounded_rectangle([90, 130, 660, 420], radius=22, fill=mixc(CARD2, k0))
    d.text((140, 176), "Benda bermassa 4 kg dipercepat", font=FR(27), fill=mixc(INK, k0), anchor="lm")
    d.text((140, 218), "2 m/s\u00b2. Berapa besar gayanya?", font=FR(27), fill=mixc(INK, k0), anchor="lm")
    # given boxes
    for i, (lbl, val, col) in enumerate((("diketahui", "m = 4 kg", GRN), ("", "a = 2 m/s\u00b2", BLU), ("ditanya", "F = ?", YEL))):
        vis, _ = pop(t, 8 + i * 3.0, 0.6)
        if vis:
            kk = fal(t, 8 + i * 3.0, 0.6)
            cx = 170 + i * 160
            d.rounded_rectangle([cx - 70, 270, cx + 70, 330], radius=16, fill=mixc(CARD, kk), outline=mixc(col, kk), width=3)
            d.text((cx, 300), val, font=FS(21), fill=mixc(col, kk), anchor="mm")
    vis, _ = pop(t, 17, 0.6)
    if vis:
        kk = fal(t, 17, 0.6)
        d.text((170, 378), "jawab dengan Hukum II  \u2192  F = m \u00d7 a", font=FS(22), fill=mixc(MUT, kk), anchor="lm")

    # solution panel
    d.rounded_rectangle([690, 130, W - 90, 420], radius=22, fill=mixc(CARD2, k0))
    d.text((730, 176), "PENYELESAIAN", font=FB(24), fill=mixc(YEL, k0), anchor="lm")
    steps = ["F = m \u00d7 a", "F = 4 \u00d7 2", "F = 8 Newton"]
    for i, st in enumerate(steps):
        tt0 = 24 + i * 7.0
        vis, _ = pop(t, tt0, 0.7)
        if vis:
            kk = fal(t, tt0, 0.7)
            big = i == 2
            d.text((730, 240 + i * 62), st, font=FB(34 if big else 30),
                   fill=mixc(YEL if big else INK, kk), anchor="lm")
            p = eo((t - tt0 - 0.4) / 0.5)
            d.line([730, 240 + i * 62 + 26 + (1 - p) * 10, 730 + (300 if big else 220) * p, 240 + i * 62 + 26],
                   fill=mixc(MUT, 0.25 + 0.3 * kk), width=3)
    vis, _ = pop(t, 40.5, 0.8)
    if vis:
        kk = fal(t, 40.5, 0.8)
        d.ellipse([600, 460, 680, 540], fill=mixc(GRN, kk))
        d.line([620, 500, 636, 516], fill=mixc(DARK, kk), width=9)
        d.line([636, 516, 664, 480], fill=mixc(DARK, kk), width=9)
        scaled_text(d, (730, 500), "Jadi, gayanya 8 N", FB, 40, mixc(YEL, kk), scale=0.7 + 0.3 * eo((t - 40.5) * 2), is_bold=True)
    d.text((150, 560), "Sekarang giliranmu:  benda m = 5 kg, a = 3 m/s\u00b2  \u2192  F = ?", font=FS(26),
           fill=mixc(BLU, fal(t, 48, 0.8)), anchor="mm")

BEATS5 = [
    (0.3, 9.0, ["Mari kita coba satu soal sederhana."]),
    (9.0, 17.0, ["Diketahui: massa benda 4 kilogram,", "percepatannya 2 meter per sekon kuadrat."]),
    (17.0, 24.0, ["Ditanya: berapa besar gaya F yang bekerja?"]),
    (24.0, 38.0, ["Gunakan Hukum II: F = m \u00d7 a.", "Masukkan angkanya: 4 kali 2."]),
    (38.0, 47.0, ["Sehingga F = 8 Newton. Selesai!"]),
    (47.0, 60.0, ["Sekarang giliranmu: massa 5 kg, percepatan 3 m/s\u00b2.", "Berapa gayanya? (Jawabannya 15 N)"]),
]

def s6(d, t, T, at):  # RANGKUMAN (55s)
    cardw, gap = 346, 42
    y0, cardh = 200, 330
    for i, (nm, sub, form, col, t0) in enumerate((
            ("I", "Inersia", "\u03a3F = 0\n\u2192 v tetap / diam", BLU, 1.2),
            ("II", "Hukum II", "F = m \u00d7 a", GRN, 2.0),
            ("III", "Aksi \u2013 Reaksi", "Faksi = \u2212Freaksi", PUR, 2.8))):
        p = eo((t - t0) / 0.9)
        if p <= 0: continue
        oy = (1 - p) * 90
        kk = 1 - p
        x0 = 84 + i * (cardw + gap)
        d.rounded_rectangle([x0, y0 + oy, x0 + cardw, y0 + cardh + oy], radius=24,
                            fill=mixc(CARD2, kk), outline=mixc(col, kk), width=3)
        d.ellipse([x0 + cardw / 2 - 36, y0 + oy - 36, x0 + cardw / 2 + 36, y0 + oy + 36], fill=mixc(col, kk))
        d.text((x0 + cardw / 2, y0 + oy), nm, font=FB(36), fill=mixc(DARK, kk), anchor="mm")
        d.text((x0 + cardw / 2, y0 + oy + 88), sub, font=FB(28), fill=mixc(INK, kk), anchor="mm")
        fy = y0 + oy + 150
        Box = mixc(DARK, min(1.0, kk + 0.25))
        d.rounded_rectangle([x0 + 28, fy, x0 + cardw - 28, fy + 62], radius=14, fill=Box)
        if i == 0:
            d.text((x0 + cardw / 2, fy + 31), "\u03a3F = 0", font=FB(26), fill=mixc(col, kk), anchor="mm")
            d.text((x0 + cardw / 2, fy + 96), "benda diam tetap diam,", font=FR(20), fill=mixc(MUT, kk), anchor="mm")
            d.text((x0 + cardw / 2, fy + 122), "bergerak tetap lurus", font=FR(20), fill=mixc(MUT, kk), anchor="mm")
        elif i == 1:
            d.text((x0 + cardw / 2, fy + 31), "F = m \u00d7 a", font=FB(26), fill=mixc(col, kk), anchor="mm")
            d.text((x0 + cardw / 2, fy + 96), "gaya serba bisa:", font=FR(20), fill=mixc(MUT, kk), anchor="mm")
            d.text((x0 + cardw / 2, fy + 122), "mengubah kecepatan", font=FR(20), fill=mixc(MUT, kk), anchor="mm")
        else:
            d.text((x0 + cardw / 2, fy + 31), "Faksi = \u2212Freaksi", font=FB(24), fill=mixc(col, kk), anchor="mm")
            d.text((x0 + cardw / 2, fy + 96), "sama besar, berlawanan", font=FR(20), fill=mixc(MUT, kk), anchor="mm")
            d.text((x0 + cardw / 2, y0 + cardh + oy - 46), "arah, benda berbeda", font=FR(20), fill=mixc(MUT, kk), anchor="mm")
        # icons
        if i == 0: ball(d, x0 + cardw / 2, y0 + cardh + oy - 30, 16, col, kk)
    d.text((W / 2, 148), "RANGKUMAN: TIGA HUKUM NEWTON", font=FB(36), fill=mixc(YEL, fal(t, 0.3, 0.7)), anchor="mm")

BEATS6 = [
    (0.3, 10.0, ["Mari kita rangkum tiga hukum Newton."]),
    (10.0, 26.0, ["Hukum I \u2014 Inersia: tanpa gaya resultan,", "gerak benda tidak akan berubah."]),
    (26.0, 41.0, ["Hukum II: gaya sama dengan massa", "dikali percepatan. F = m \u00d7 a."]),
    (41.0, 55.0, ["Hukum III: setiap aksi dijawab reaksi yang", "sama besar dan berlawanan arah."]),
]

def s7(d, t, T, at):  # PENUTUP (22s)
    p = eo(t / 1.0)
    scaled_text(d, (W / 2, 280), "Terima Kasih!", FB, 72, mixc(YEL, fal(t, 0.4, 0.9)), scale=0.8 + 0.2 * p, is_bold=True)
    d.text((W / 2, 356), "Sekarang kamu tahu cara kerja gaya di sekitar kita", font=FS(28),
           fill=mixc(INK, fal(t, 1.6, 0.8)), anchor="mm")
    ap = eo((t - 2.6) / 1.0)
    if ap > 0:
        ax = 240 - (1 - ap) * 120; ay = 200 + math.sin(t * 1.5) * 10
        apple(d, ax, ay, 44, 1 - ap)
        arrow(d, ax + 70, ay + 10, ax + 130, ay + 60, mixc(GRN, 1 - ap), w=6)
        ball(d, 1050, 220 + math.sin(t * 1.2 + 2) * 14, 30, mixc(BLU, 0.0) if ap else BG, 1 - ap)
    kq = fal(t, 6.0, 0.8)
    if t >= 6:
        d.rounded_rectangle([W / 2 - 430, 440, W / 2 + 430, 560], radius=22, fill=mixc(CARD2, kq), outline=mixc(YEL, kq), width=3)
        d.text((W / 2, 472), "KUIS SINGKAT", font=FB(24), fill=mixc(YEL, kq), anchor="mm")
        d.text((W / 2, 520), "Mengapa penumpang terdorong ke depan saat bus direm?", font=FR(25), fill=mixc(INK, kq), anchor="mm")
        d.text((W / 2, 628), "Jawab dengan Hukum Newton \u2014 dan selamat belajar!", font=FS(24),
               fill=mixc(MUT, fal(t, 9.0, 0.8)), anchor="mm")

BEATS7 = [
    (0.3, 6.0, ["Itulah tiga hukum Newton \u2014 kunci untuk", "memahami gerak di sekitar kita."]),
    (6.0, 14.0, ["Kuis: mengapa penumpang terdorong ke depan", "saat bus direm mendadak?"]),
    (14.0, 22.0, ["Terima kasih sudah belajar. Sampai jumpa", "di video berikutnya!"]),
]

# ---------- timeline ----------
SCENES = [(s0, 25, "Pembuka"), (s1, 45, "Apa Itu Gaya?"), (s2, 62, "Hukum I \u2014 Inersia"),
          (s3, 72, "Hukum II \u2014 F = m\u00b7a"), (s4, 62, "Hukum III \u2014 Aksi-Reaksi"),
          (s5, 60, "Contoh Soal"), (s6, 55, "Rangkuman"), (s7, 22, "Penutup")]
SCENE_DUR = [s[1] for s in SCENES]
BEATS = [BEATS0, BEATS1, BEATS2, BEATS3, BEATS4, BEATS5, BEATS6, BEATS7]
TOTAL = sum(SCENE_DUR)
NF = int(TOTAL * FPS)
NAMES = [s[2] for s in SCENES]

def render(out="hukum_newton.mp4"):
    starts, acc = [], 0
    for du in SCENE_DUR:
        starts.append(acc); acc += du
    cmd = [FF, "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    img = Image.new("RGB", (W, H), BG)
    for fi in range(NF):
        tt = fi / FPS
        si = 0
        for i, st in enumerate(starts):
            if tt >= st: si = i
            else: break
        lt = tt - starts[si]
        d = ImageDraw.Draw(img)
        backdrop(d, tt)
        SCENES[si][0](d, lt, SCENE_DUR[si], tt)
        subpill(d, BEATS[si], lt)
        hud(d, tt, TOTAL, NAMES, si, lt, SCENE_DUR[si])
        proc.stdin.write(img.tobytes())
        if fi % 480 == 0:
            print(f"frame {fi}/{NF}  t={tt:.1f}s", flush=True)
    proc.stdin.close(); proc.wait()
    print("done:", out)

if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "hukum_newton.mp4")
