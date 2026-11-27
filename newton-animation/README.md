# Animasi Hukum-Hukum Newton (Flat Motion Graphic)

Video animasi edukasi fisika tentang gaya & Hukum Newton, siap dipakai untuk TikTok / Reels / Shorts.
Semua video sudah bersuara: **narasi bahasa Indonesia** (TTS voice `id-ID-ArdiNeural`) + **musik latar lo-fi** yang otomatis mengecil (ducking) saat narasi berbicara.

## File video

| File | Format | Durasi | Isi |
|---|---|---|---|
| `hukum_newton.mp4` | 1280x720 (16:9) | 6:43 | Video lengkap: semua materi |
| `tiktok/tiktok_1_gaya.mp4` | 1080x1920 (9:16) | 1:10 | Apa itu gaya (dorongan, tarikan, satuan N) |
| `tiktok/tiktok_2_hukum1.mp4` | 1080x1920 (9:16) | 1:02 | Hukum I — Inersia + demo bus direm |
| `tiktok/tiktok_3_hukum2.mp4` | 1080x1920 (9:16) | 1:12 | Hukum II — F = m·a + grafik a vs F, a vs 1/m |
| `tiktok/tiktok_4_hukum3.mp4` | 1080x1920 (9:16) | 1:02 | Hukum III — Aksi-Reaksi (bola, roket, renang) |
| `tiktok/tiktok_5_soal.mp4` | 1080x1920 (9:16) | 2:17 | Contoh soal F=ma + rangkuman + kuis |

## Render ulang / modifikasi

Butuh Python 3.10+, lalu:

```bash
pip install pillow numpy imageio-ffmpeg edge-tts
python3 render_newton.py hukum_newton.mp4      # versi landscape 6:43
python3 render_tiktok.py                        # 5 klip vertikal TikTok
python3 render_tiktok.py 2                      # render hanya klip nomor 2
python3 make_audio.py                           # narasi TTS + musik, mux ke semua video
python3 make_audio.py tiktok_2                  # audio hanya untuk satu video
```

Catatan: `make_audio.py` butuh internet karena narasi di-generate via edge-tts (gratis, tanpa API key). Ganti suara dengan mengubah `VOICE`, mis. `id-ID-GadisNeural` untuk suara perempuan.

Font Poppins (OFL license) sudah disertakan di `fonts/`, jadi tidak perlu unduh apa pun lagi.

### Kustomisasi cepat di `render_newton.py`
- `SCENES` — daftar scene, durasi, dan nama (mengubah durasi juga otomatis mengubah timeline).
- `BEATS*` — teks narasi/subtitle per scene (muncul dengan efek typewriter).
- Warna: `BG, YEL, RED, GRN, BLU, PUR` di bagian atas file.

## Ide jadwal posting TikTok
1. Part 1 (gaya) → hook pemula
2. Part 2 (inersia) → pakai Barrett text "kenapa kamu terlempar pas bus direm?"
3. Part 3 (F=ma) → moms soal cepat
4. Part 4 (aksi-reaksi) → visual roket paling viral-friendly
5. Part 5 (soal) → CTA "jawab di komentar"
