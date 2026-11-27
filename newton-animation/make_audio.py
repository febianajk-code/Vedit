# Adds audio to all videos: synthesized lo-fi music bed + Indonesian TTS narration
# synced to each video's subtitle beats. Outputs 16-bit WAV mixes for muxing.
import asyncio, math, os, subprocess, sys, tempfile, wave
import numpy as np
import edge_tts
import imageio_ffmpeg
import render_newton as R

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
VOICE = "id-ID-ArdiNeural"

L = [(i, d) for i, (_, d, _) in enumerate(R.SCENES)]
VIDEOS = [
    ("hukum_newton.mp4", L),
    ("tiktok_1_gaya.mp4", [(0, 25), (1, 45)]),
    ("tiktok_2_hukum1.mp4", [(2, 62)]),
    ("tiktok_3_hukum2.mp4", [(3, 72)]),
    ("tiktok_4_hukum3.mp4", [(4, 62)]),
    ("tiktok_5_soal.mp4", [(5, 60), (6, 55), (7, 22)]),
]

TTS_CACHE = {}

def tts(text, rate="+0%"):
    key = (text, rate)
    if key in TTS_CACHE:
        return TTS_CACHE[key]
    async def gen():
        c = edge_tts.Communicate(text, VOICE, rate=rate)
        await c.save(tmpname)
    tmpname = tempfile.mktemp(suffix=".mp3")
    asyncio.run(gen())
    raw = subprocess.run([FF, "-i", tmpname, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    arr = np.frombuffer(raw, dtype=np.float32).copy()
    os.unlink(tmpname)
    TTS_CACHE[key] = arr
    return arr

def music_bed(total):
    n = int(total * SR)
    t_all = np.arange(n) / SR
    bed = np.zeros(n)
    A3, C4, E4 = 220.0, 261.63, 329.63
    F3, G3, B3 = 174.61, 196.0, 246.94
    G2, D3, C3, E3, F2, F3a = 98.0, 146.83, 130.81, 164.81, 87.31, 174.61
    chords = [
        [A3, C4, E4, 440.0],
        [F3, A3, C4, F3a],
        [C3 * 2, E3 * 2, G3, C4],
        [G2 * 2, B3, D3 * 2, G3],
    ]
    chord_dur = 3.2
    for ci in range(int(total / chord_dur) + 1):
        t0 = ci * chord_dur
        ch = chords[ci % 4]
        dur = chord_dur * 1.25
        i0 = int(t0 * SR); i1 = min(n, i0 + int(dur * SR))
        if i0 >= n: break
        tt = np.arange(i1 - i0) / SR
        env = np.clip(tt / 1.0, 0, 1) * np.clip((dur - tt) / 1.1, 0, 1)
        pad = np.zeros(i1 - i0)
        for f in ch:
            pad += np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tt) \
                   + 0.5 * np.sin(2 * np.pi * (f + 0.7) * tt)
        bed[i0:i1] += 0.085 * env * pad
        bass_f = ch[0] / 2
        for b in (0.0, 1.6):
            j0 = int((t0 + b) * SR)
            if j0 >= n: continue
            bj = min(n - j0, int(1.2 * SR))
            tb = np.arange(bj) / SR
            e = np.exp(-tb / 0.45)
            bed[j0:j0 + bj] += 0.16 * e * np.sin(2 * np.pi * bass_f * tb)
    # kick + hat every 0.8s (2/4 feel at 75bpm-ish)
    beat = 0.8
    k0 = np.arange(int(0.22 * SR)) / SR
    kick = np.sin(2 * np.pi * (42 + 60 * np.exp(-k0 / 0.03)) * k0) * np.exp(-k0 / 0.09)
    hk = int(beat * SR)
    for j in range(int(n / hk) + 1):
        j0 = j * hk
        if j0 + len(kick) < n:
            bed[j0:j0 + len(kick)] += 0.22 * kick
        h0 = j0 + hk // 2
        if h0 + int(0.05 * SR) < n:
            nz = np.random.default_rng(j).standard_normal(int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.012)
            bed[h0:h0 + len(nz)] += 0.045 * nz
    fade = np.ones(n)
    fi = int(1.5 * SR); fo = int(2.5 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    return bed * fade

def env_downsample(x, sr=100):
    step = SR // sr
    m = len(x) // step * step
    if m == 0: return np.zeros(1)
    e = np.abs(x[:m]).reshape(-1, step).mean(axis=1)
    k = np.ones(8) / 8
    e = np.convolve(e, k, mode="same")
    return e

def build_for(video, segs):
    spans = []
    acc = 0
    for (si, dur) in segs:
        spans.append((acc, si, dur)); acc += dur
    total = acc
    n = int(total * SR)
    narr = np.zeros(n)
    for (start, si, dur) in spans:
        for (b0, b1, lines) in R.BEATS[si]:
            text = " ".join(lines).replace("\u2014", ",").replace("\u2019", "'")
            window = (b1 - b0) - 0.35
            a = tts(text)
            d = len(a) / SR
            rate = "+0%"
            if d > window:
                rate = f"+{min(40, int((d / window - 1) * 100))}%"
                a = tts(text, rate)
                d = len(a) / SR
            i0 = int((start + b0) * SR)
            i1 = min(n, i0 + len(a))
            if i0 < n:
                f = np.linspace(0, 1, min(600, i1 - i0))
                narr[i0:i0 + len(f)] *= (1 - f)
                narr[i0:i1] += a[:i1 - i0] * 0.95
                print(f"  beat @{start+b0:6.1f}s  {d:4.1f}s/{window:4.1f}s  {rate:>5}  {text[:44]}", flush=True)
    music = music_bed(total)
    e = env_downsample(narr)
    duck = np.interp(np.arange(n) / SR * 100, np.arange(len(e)) / 100 * 1, np.clip(1 - e * 2.2, 0.25, 1))
    mix = narr + music * duck * 0.75
    peak = np.max(np.abs(mix)) or 1.0
    if peak > 0.97:
        mix *= 0.97 / peak
    out = f"/tmp/audio_{video}"
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"== {out} ({total:.0f}s) ==", flush=True)
    return out

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for (video, segs) in VIDEOS:
        if only and only not in video: continue
        wav = build_for(video, segs)
        subprocess.run([FF, "-y", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", f"with_audio_{video}"], check=True)
        os.replace(f"with_audio_{video}", video)
        print(f"muxed -> {video}", flush=True)
