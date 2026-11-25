# TikTok-style vertical renderer (1080x1920): splits the Newton scenes into 5 short clips.
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import render_newton as R

TW, TH = 1080, 1920
FPS = 24
TOP_H = 560
CW, CH = TW, 608
CONTENT_Y = TOP_H

def pp(t0, t1):
    r = subprocess.run([])
    return (t0, t1)

CLIPS = [
    {"name": "1 APA ITU GAYA", "file": "tiktok_1_gaya.mp4", "title": ["APA ITU", "GAYA?"],
     "tag": "Fisika dasar, dijelaskan simpel", "col": R.YEL, "num": 1,
     "segs": [(0, 25), (1, 45)]},
    {"name": "2 HUKUM I", "file": "tiktok_2_hukum1.mp4", "title": ["HUKUM I", "INERSIA"],
     "tag": "Kenapa badan terdorong saat bus direm?", "col": R.BLU, "num": 2,
     "segs": [(2, 62)]},
    {"name": "3 HUKUM II", "file": "tiktok_3_hukum2.mp4", "title": ["HUKUM II", "F = m · a"],
     "tag": "Massa kecil vs massa besar", "col": R.GRN, "num": 3,
     "segs": [(3, 72)]},
    {"name": "4 HUKUM III", "file": "tiktok_4_hukum3.mp4", "title": ["HUKUM III", "AKSI-REAKSI"],
     "tag": "Roket & perenang pakai hukum ini", "col": R.PUR, "num": 4,
     "segs": [(4, 62)]},
    {"name": "5 SOAL + RANGKUMAN", "file": "tiktok_5_soal.mp4", "title": ["CONTOH SOAL", "& RANGKUMAN"],
     "tag": "Coba jawab kuisnya di komentar!", "col": R.YEL, "num": 5,
     "segs": [(5, 60), (6, 55), (7, 22)]},
]

def npow(t0, t1):  # noop
    pass

DECOS = [(0.1, 0.06, 60, 24), (0.85, 0.045, 44, -18), (0.5, 0.035, 90, 16), (0.25, 0.93, 50, -14),
         (0.8, 0.97, 64, 20), (0.12, 0.5, 36, -12), (0.92, 0.35, 40, 12)]

def vbackdrop(d, at):
    d.rectangle([0, 0, TW, TH], fill=R.BG)
    for i, (fx, fy, rr_, sp) in enumerate(DECOS):
        bx = (fx * TW + sp * at) % (TW + 200) - 100
        by = fy * TH + math.sin(at * 0.4 + i * 1.9) * 30
        col = R.mixc((58, 68, 118), 0.42)
        if i % 2 == 0:
            d.ellipse([bx - rr_, by - rr_, bx + rr_, by + rr_], outline=col, width=2)
        else:
            sz = rr_ * 0.7
            ang = at * 0.2 + i
            d.polygon([(bx + sz * math.cos(ang + a), by + sz * math.sin(ang + a))
                       for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)], fill=col)

def top_zone(d, clip, t):
    col = clip["col"]
    p = R.eo(t / 0.8)
    oy = (1 - p) * 60
    for i, line in enumerate(clip["title"]):
        f = max(6, int(96 * (0.9 + 0.1 * p)))
        fnt = ImageFont.truetype("fonts/Poppins-Bold.ttf", f)
        d.text((TW / 2, 150 + oy + i * 108), line, font=fnt, fill=R.mixc(R.INK, 1 - p), anchor="mm")
    pl = R.eo((t - 0.5) / 0.9)
    if pl > 0:
        uw = 440 * pl
        d.rounded_rectangle([TW / 2 - uw / 2, 400, TW / 2 + uw / 2, 408], radius=4, fill=col)
    kt = R.fal(t, 1.2, 0.8)
    if t >= 1.2:
        d.text((TW / 2, 470), clip["tag"], font=R.FS(30), fill=R.mixc(R.MUT, kt), anchor="mm")
    chip(d, 150, 60, f"PART {clip['num']}/5", R.FS(20), R.DARK, col, padx=18, pady=8, k=1 - p)
    d.text((TW - 40, 60), "Fisika • Newton", font=R.FS(19), fill=R.mixc(R.MUT, 0.25 + 0.3 * (1 - p)), anchor="rm")

def chip(d, cx, cy, text, fnt, fg, bgc, padx=22, pady=10, k=0.0):
    tw = d.textlength(text, font=fnt)
    bh = fnt.size + pady * 2
    bb = [cx - tw / 2 - padx, cy - bh / 2, cx + tw / 2 + padx, cy + bh / 2]
    d.rounded_rectangle(bb, radius=bh / 2, fill=R.mixc(bgc, k))
    d.text((cx, cy), text, font=fnt, fill=R.mixc(fg, k), anchor="mm")

def bottom_zone(d, clip, t, total, seg_spans):
    col = clip["col"]
    # subtitle pill
    beat = None; lt = 0
    for (start, si, dur) in seg_spans:
        if start <= t < start + dur:
            lt = t - start
            for (b0, b1, lines) in R.BEATS[si]:
                if b0 <= lt < b1:
                    beat = lines
                    lt = lt - b0
                    break
            break
    if beat:
        fnt = R.FR(31); lh = 44
        budget = int(lt * 36 + 2)
        shown = []
        for L in beat:
            take = L[:max(0, budget)]; shown.append(take); budget -= len(L)
            if budget <= 0: break
        while shown and not shown[-1]: shown.pop()
        if not shown: shown = [" "]
        maxw = min(TW - 60, max(d.textlength(L, font=fnt) for L in shown) + 80)
        cy, hh = 1330, lh * len(shown) + 30
        top = cy - hh / 2
        d.rounded_rectangle([TW / 2 - maxw / 2, top, TW / 2 + maxw / 2, top + hh],
                            radius=18, fill=R.DARK, outline=R.mixc(col, 0.3), width=2)
        d.rectangle([TW / 2 - maxw / 2 + 14, top + 14, TW / 2 - maxw / 2 + 22, top + hh - 14], fill=col)
        for i, L in enumerate(shown):
            d.text((TW / 2 + 12, top + 24 + lh * i), L, font=fnt, fill=R.INK, anchor="mm")
    # progress
    x0, x1, y = 70, TW - 70, 1730
    d.rounded_rectangle([x0, y, x1, y + 10], radius=5, fill=R.CARD)
    fx = x0 + (x1 - x0) * (t / total)
    d.rounded_rectangle([x0, y, fx, y + 10], radius=5, fill=col)
    for (start, si, dur) in seg_spans:
        px = x0 + (x1 - x0) * (start / total)
        d.ellipse([px - 5, y + 1, px + 5, y + 11], fill=R.CARD)
    d.text((x0, y - 30), clip["name"], font=R.FS(22), fill=R.mixc(R.MUT, 0.1), anchor="lm")
    d.text((TW - 70, y - 30), f"{int(t // 60)}:{int(t % 60):02d} / {int(total // 60)}:{int(total % 60):02d}",
           font=R.FR(21), fill=R.mixc(R.MUT, 0.3), anchor="rm")
    d.text((TW / 2, 1820), "Follow untuk belajar fisika tiap minggu!", font=R.FS(23),
           fill=R.mixc(R.MUT, 0.35), anchor="mm")

def render_clip(clip, out):
    seg_spans = []
    acc = 0
    for (si, dur) in clip["segs"]:
        seg_spans.append((acc, si, dur)); acc += dur
    total = acc
    NF = int(total * FPS)
    cmd = [R.FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{TW}x{TH}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    main = Image.new("RGB", (TW, TH), R.BG)
    tmp = Image.new("RGB", (R.W, R.H), R.BG)
    for fi in range(NF):
        t = fi / FPS
        dm = ImageDraw.Draw(main)
        vbackdrop(dm, t)
        si, lt = seg_spans[-1][1], 0
        for (start, s_i, dur) in seg_spans:
            if t >= start: si, lt = s_i, t - start
            else: break
        dt = ImageDraw.Draw(tmp)
        R.SCENES[si][0](dt, lt, R.SCENE_DUR[si], t)
        content = tmp.resize((CW, CH), Image.LANCZOS)
        main.paste(content, (0, CONTENT_Y))
        dm.rectangle([0, CONTENT_Y - 4, TW, CONTENT_Y], fill=R.mixc(clip["col"], 0.0))
        dm.rectangle([0, CONTENT_Y + CH, TW, CONTENT_Y + CH + 4], fill=R.mixc(clip["col"], 0.0))
        top_zone(dm, clip, t)
        bottom_zone(dm, clip, t, total, seg_spans)
        proc.stdin.write(main.tobytes())
        if fi % 480 == 0:
            print(f"  {clip['file']} frame {fi}/{NF}", flush=True)
    proc.stdin.close(); proc.wait()
    print("done:", clip["file"], flush=True)

if __name__ == "__main__":
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    for i, c in enumerate(CLIPS):
        if only is None or i == only:
            render_clip(c, c["file"])
