# Sver File

Aplikasi editor file ringan yang jalan langsung di browser HP maupun desktop.
Tanpa build step, tanpa dependensi — buka `index.html` dan langsung pakai.

## Fitur

- **Dua gaya UI**: *Material Style* (permukaan solid, ripple effect) dan *Liquid Glass Style* (panel blur transparan dengan latar gradien bergerak).
- **Editor teks lengkap**: undo/redo (stack sendiri + shortcut `Ctrl+Z` / `Ctrl+Y`), cut, copy, paste, select all, clear, unduh, autosave, statistik baris/karakter/kursor.
- **Buat file baru**: 20 jenis file (txt, md, html, css, js, json, xml, csv, py, java, c, cpp, cs, php, sh, yaml, ini, sql, svg, log) lengkap dengan template awal.
- **Folder proyek**: buat, ganti nama, hapus, dan pindahkan file antar folder.
- **Riwayat edit**: daftar file yang baru saja diedit beserta waktunya.
- **Kustomisasi penuh**: warna aksen, mode gelap/terang, latar belakang (preset gradien, warna kustom, atau gambar dari perangkat), intensitas blur, transparansi panel, dan ukuran teks.
- **Izin penyimpanan lokal**: diminta saat aplikasi pertama kali dibuka (`navigator.storage.persist()`), plus opsi menghubungkan folder perangkat nyata via File System Access API.
- **Loading screen** animasi logo pixel, tombol dengan animasi tekan/ripple, dan layout responsif (bottom-nav di HP, side-rail di layar lebar) yang aman untuk notch/safe-area.

## Menjalankan

Statis murni — tidak perlu build:

```bash
cd sver-file
python3 -m http.server 8080
```

Buka `http://localhost:8080`, atau deploy folder ini ke GitHub Pages /
hosting statis mana pun. Terpasang sebagai PWA (installable, offline via
service worker).

## Struktur

```
sver-file/
├── index.html          # kerangka aplikasi
├── css/style.css       # tema Material + Liquid Glass
├── js/app.js           # logika editor, storage, riwayat, pengaturan
├── manifest.webmanifest
├── sw.js               # service worker (offline)
├── icons/              # ikon pixel-art
└── tools/gen_icons.py  # generator ikon (Pillow)
```

Data disimpan di `localStorage` perangkat; tersedia cadangan/pemulihan JSON
dari menu Pengaturan.
