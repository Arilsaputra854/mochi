# MeowMate — Desktop Pet Kucing

## 🎯 Tujuan
Buat desktop pet yang ringan, lucu, dan interaktif di Windows — lebih matang dari repo referensi [1ilit/Desktop-Cat](https://github.com/1ilit/Desktop-Cat), tanpa jadi beban sistem.

> **Design principle:** *Ringan lebih dari segalanya. Kalau berat, jangan dipake.*

---

## 🛠️ Tech Stack

| Layer | Pilihan | Alasan |
|-------|---------|--------|
| **GUI** | Tkinter (built-in Python) | Tidak perlu install framework tambahan |
| **Image handling** | Pillow (PIL) | Resize, transparency, sprite handling |
| **Input hook** | `keyboard` | Deteksi aktivitas ketik user |
| **Packaging** | PyInstaller | Build `.exe` tanpa perlu Python terinstall |

**Total dependency tambahan cuma 2:** `Pillow` + `keyboard`

---

## 📁 Struktur Project

```
Desktop-Pet/
├── assets/
│   ├── sprites/          # Frame per aksi
│   │   ├── idle_1.png ... idle_12.png
│   │   ├── sleeping_1.png ... sleeping_6.png
│   │   ├── walk_left_1.png ... walk_left_4.png
│   │   ├── walk_right_1.png ... walk_right_4.png
│   │   ├── play_1.png ... play_6.png
│   │   ├── angry_1.png
│   │   └── zzz_1.png ... zzz_4.png
│   └── icons/
│       ├── tray_icon.ico
│       └── tray_icon_active.ico
├── src/
│   ├── cat.py            # State machine + animasi
│   ├── window.py         # Tkinter overlay window
│   ├── behavior.py       # AI perilaku (mood, event, random action)
│   ├── input_watcher.py  # Deteksi aktivitas ketik user
│   └── tray.py           # System tray: show/hide, settings, quit
├── config.yaml           # Speed, interval, mood decay rate
├── main.py
└── requirements.txt
```

---

## 🚀 MVP Fitur (Prioritas 1)

| # | Fitur | Deskripsi |
|---|-------|-----------|
| 1 | **Idle animation** | 8–12 frame idle yang varied — tidak statis |
| 2 | **Random walk** | Jalan kiri/kanan secara acak dengan boundary detection |
| 3 | **Sleep mode** | Setelah X menit idle → turun ke lantai, snooze, Zzz particles |
| 4 | **Tray icon** | Minimize ke tray, klik untuk toggle visibility |
| 5 | **Click interaction** | Klik kucing → reaction (menggaruk, lompat kecil, marah) |
| 6 | **Drag & drop** | Bisa drag kucing ke posisi mana pun di layar |

---

## 🎮 Fitur "Plus" (Stretch Goals)

| # | Fitur | Deskripsi |
|---|-------|-----------|
| 7 | **Follow mouse** | Kadang mengikuti cursor saat mouse diam |
| 8 | **Keyboard awareness** | Saat user ketik banyak, kucing kadang muncul mengganggu atau turun tidur |
| 9 | **Mood system** | Hunger, energy, happiness — berkurang seiring waktu, perlu "dirawat" |
| 10 | **Multiple cats** | Unlock 2–3 karakter (beda asset, beda mood) |
| 11 | **Mini games** | Catch the laser pointer, chase toy |
| 12 | **Config panel** | Tray → Settings: atur speed, interval, auto-hide fullscreen |

---

## 📝 Langkah Pengembangan

### Phase 1: Core Engine (1–2 hari)
1. Setup project, install `Pillow`
2. Buat `window.py` — transparent Tkinter overlay, always-on-top, frameless
3. Buat `cat.py` — state machine dasar (`idle`, `sleep`, `walk_left`, `walk_right`)
4. Load sprite frames + animasi looping

### Phase 2: Behavior (1–2 hari)
5. Buat `behavior.py` — random event trigger, timer untuk sleep
6. Implementasi boundary detection (jangan keluar layar)
7. Click handler untuk interaksi dasar

### Phase 3: Polish (1 hari)
8. Tray icon + show/hide toggle
9. Drag & drop repositioning
10. Keyboard watcher dasar

### Phase 4: Packaging (½ hari)
11. Build `.exe` dengan PyInstaller
12. Test di Windows, cek memory usage (target: <50MB idle)

---

## ⚠️ Catatan Teknis

| Issue | Solusi |
|-------|--------|
| **Tkinter performance** | Jangan update `after()` terlalu cepat — 30–50ms per frame cukup |
| **Transparency** | Gunakan color key (`-transparentcolor`) dengan warna yang tidak ada di asset |
| **Memory leak** | Simpan semua `PhotoImage` di list, jangan bikin baru tiap frame |
| **Multi-monitor** | `win32api.GetMonitorInfo` untuk detect work area |
| **Packaging** | `pyinstaller --onefile --noconsole --icon=assets/icons/icon.ico main.py` |

---

## 🎨 Kebutuhan Asset (MVP)

| Aksi | Frame | Ukuran |
|------|-------|--------|
| Idle | 8–12 | 72x64px |
| Sleeping | 6–8 | 72x64px |
| Walk left | 4 | 72x64px |
| Walk right | 4 | 72x64px |
| Zzz particles | 2–3 | 32x32px |

Format: PNG 32-bit + transparency. Untuk development, pakai placeholder asset dulu sebelum diganti asset asli.

---

## 📦 Deliverable Akhir

- `dist/MeowMate.exe` — single file, jalan di Windows tanpa Python terinstall
- Source code di repo GitHub
- Memory usage < 50MB saat idle

---

## ⏱️ Estimasi Total

**MVP: 3–4 hari kerja (full-time)**
**Full version: 1–2 minggu** (termasuk asset design, game features)

---

*Dibuat: 2026-06-22*
*Status: Planning — Menunggu konfirmasi lanjut*
