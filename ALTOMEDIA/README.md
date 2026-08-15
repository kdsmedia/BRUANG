# ALTOMEDIA — Paket Rilis BERUANG (Play Store Ready)

Folder ini berisi **seluruh paket rilis** aplikasi **BERUANG** yang siap
diunggah ke Google Play Console. Semua artifact sudah ditandatangani dengan
keystore ALTOMEDIA.jks dan memenuhi persyaratan Play Store terkini.

- **Aplikasi:** BERUANG
- **Package:** `com.altomedia.beruang`
- **Versi:** 1.0.0 (versionCode 1)
- **Pengembang:** ALTOMEDIA
- **Backend:** Supabase

---

## Struktur Folder

```
ALTOMEDIA/
├── release/                         # Artifact rilis siap upload
│   ├── beruang-v1.0.0-release.aab   # AAB (WAJIB untuk Play Store)
│   ├── beruang-v1.0.0-release.apk   # APK release (uji sideload)
│   └── beruang-v1.0.0-debug.apk     # APK debug (pengujian)
├── playstore/                       # Aset grafis Play Store
│   ├── app_icon_512.png             # Ikon 512x512
│   ├── feature_graphic.png          # Grafik fitur 1024x500
│   ├── screenshots/                 # 5 screenshot 1080x1920
│   └── assets_src/                 # Sumber SVG + script generator
├── legal/
│   ├── PRIVACY_POLICY.md            # Kebijakan Privasi (detail)
│   └── TERMS_OF_SERVICE.md         # Ketentuan Layanan (detail)
├── docs/
│   ├── UPLOAD_GUIDE.txt             # Panduan upload rilis & listing
│   ├── STORE_LISTING_GUIDE.txt      # Panduan mengisi store listing
│   ├── RELEASE_NOTES.txt           # Catatan rilis + format update
│   ├── store_full_description.txt  # Deskripsi lengkap untuk listing
│   └── BLOG_ARTICLE.txt            # Artikel blog (4000+ karakter)
├── keystore/
│   └── ALTOMEDIA.jks               # Keystore signing (PENTING, jaga aman)
└── README.md                        # File ini
```

---

## Persyaratan Teknis (sesuai Play Store saat ini)

| Properti            | Nilai                              |
|---------------------|------------------------------------|
| applicationId       | `com.altomedia.beruang`            |
| minSdkVersion      | 23 (Android 6.0 Marshmallow)      |
| targetSdkVersion   | 37 (Android 16)                   |
| compileSdkVersion  | 37                                |
| buildToolsVersion  | 37.0.0                            |
| Format rilis       | AAB (Android App Bundle)          |
| Signing scheme     | v2 (APK Signature Scheme v2)      |
| Signing identity   | CN=ALTOMEDIA, O=ALTOMEDIA, L=Karawang, ST=Jawa Barat, C=ID |
| Keystore           | ALTOMEDIA.jks (alias kdsmedia)    |
| Validity           | 10000 hari                        |

---

## Keystore (PENTING)

- **File:** `keystore/ALTOMEDIA.jks`
- **Keystore password:** `Kdsmedia@123`
- **Alias:** `kdsmedia`
- **Key password:** `Kdsmedia@123`

> PERINGATAN: Simpan keystore ini dengan aman dan buat backup. Untuk
> memperbarui aplikasi di Play Store, Anda **WAJIB** menggunakan keystore
> yang sama. Jika hilang, aplikasi tidak bisa diperbarui dengan package
> name yang sama.

---

## Cara Upload ke Play Store

1. Baca panduan lengkap di `docs/UPLOAD_GUIDE.txt`.
2. Untuk mengisi formulir listing, lihat `docs/STORE_LISTING_GUIDE.txt`.
3. Upload `release/beruang-v1.0.0-release.aab` ke Play Console.
4. Gunakan grafik di `playstore/` untuk store listing.
5. Host `legal/PRIVACY_POLICY.md` ke URL publik untuk form Privacy Policy.
6. Salin `docs/store_full_description.txt` ke kolom deskripsi lengkap.

---

## Cara Build Ulang (untuk update)

```bash
cd android
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export ANDROID_HOME=/opt/android-sdk
./gradlew :app:bundleRelease --no-daemon
cp app/build/outputs/bundle/release/app-release.aab \
   ../ALTOMEDIA/release/beruang-vX.Y.Z-release.aab
```

Naikkan `versionCode` dan `versionName` di `android/app/build.gradle.kts`
setiap rilis baru, lalu tambahkan entri di `docs/RELEASE_NOTES.txt`.

---

## Dokumen yang Tersedia

| Dokumen                          | Kegunaan                            |
|----------------------------------|-------------------------------------|
| `docs/UPLOAD_GUIDE.txt`          | Panduan langkah-demi-langkah upload |
| `docs/STORE_LISTING_GUIDE.txt`   | Panduan mengisi store listing        |
| `docs/RELEASE_NOTES.txt`         | Catatan rilis + template update     |
| `docs/store_full_description.txt`| Deskripsi listing Play Store        |
| `docs/BLOG_ARTICLE.txt`          | Artikel blog promosi (4000+ char)   |
| `legal/PRIVACY_POLICY.md`        | Kebijakan Privasi                   |
| `legal/TERMS_OF_SERVICE.md`      | Ketentuan Layanan                   |

---

© 2026 ALTOMEDIA. Semua hak dilindungi.
