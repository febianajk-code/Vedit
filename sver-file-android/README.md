# Sver File — Android

APK wrapper native untuk web app Sver File. WebView fullscreen memuat
seluruh aplikasi dari `app/src/main/assets/www/` (offline, tanpa internet).

- Package: `com.sver.file` (minSdk 24 / Android 7.0, targetSdk 34)
- Ikon: pixel-art disket (`res/mipmap-xxhdpi/ic_launcher.png`)
- Izin penyimpanan lokal diminta saat aplikasi pertama dibuka
  (`READ/WRITE_EXTERNAL_STORAGE`, hanya untuk Android ≤ 12; Android 13+
  tidak membutuhkannya karena penyimpanan memakai internal + MediaStore)
- Tombol unduh di editor menyimpan file ke folder **Downloads** via
  `AndroidBlob` JS bridge (MediaStore API)
- "Buka dari Perangkat" memakai file chooser sistem (ACTION_GET_CONTENT)

## Build

```bash
gradle -p sver-file-android assembleDebug
# hasil: sver-file-android/app/build/outputs/apk/debug/app-debug.apk
```

Atau otomatis: workflow `.github/workflows/build-apk.yml` membuild APK di
setiap push dan mengunggahnya sebagai artifact `SverFile-APK`.

## Update app di dalam APK

Setelah mengubah file di `sver-file/`, sinkronkan ulang:

```bash
cp -r sver-file/index.html sver-file/css sver-file/js sver-file/icons \
      sver-file/manifest.webmanifest sver-file/sw.js \
      sver-file-android/app/src/main/assets/www/
```

lalu build ulang.
