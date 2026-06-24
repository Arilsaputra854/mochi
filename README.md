# Mochi 🐱

Desktop pet kucing pixel art untuk Windows. Mochi hidup di layarmu, bereaksi ke aktivitas keyboard & mouse, bisa diajak ngobrol pakai AI, dan ngingetin kamu istirahat kalau kelamaan duduk.

![Mochi idle](assets/sprites/idle_1.png)

## Fitur

- Animasi idle, jalan, tidur, makan, main, manjat, gelantungan, dan banyak lagi
- Bereaksi ke typing & klik mouse
- **Tanya Mochi** — chat dengan kucing via LLM (OpenAI-compatible, opsional)
- **AI Autonomous** — LLM kendaliin aksi kucing otomatis (opsional)
- **Health reminders** — ingetin mata istirahat, minum air, gerak, cek postur
- Pengingat harian (solat, makan) yang bisa dikustomisasi
- Persona kucing bisa diubah (nama, kepribadian, bahasa)
- Windows 10/11

---

## Instalasi

### 1. Requirement

- **Python 3.10+** — [python.org](https://python.org)
- **Windows 10 atau 11**

### 2. Clone repo

```bash
git clone https://github.com/Arilsaputra854/mochi.git
cd mochi
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan

```bash
python main.py
```

Mochi akan muncul di pojok bawah layar. Klik kanan untuk menu.

---

## Konfigurasi AI (Opsional)

Tanpa API key, Mochi tetap berjalan normal dengan behavior random.

Untuk aktifkan AI:

1. Klik kanan Mochi → **Pengaturan ⚙️**
2. Isi:
   - **Base URL** — endpoint OpenAI-compatible (contoh: `https://api.groq.com/openai/v1`)
   - **Model** — nama model (contoh: `llama-3.3-70b-versatile`)
   - **API Key** — key dari provider
3. Klik **Simpan**

Provider gratis yang bisa dipakai: [Groq](https://console.groq.com) (Llama 3.3 70B, gratis).

Atau via environment variable / file `.env` di root project:

```env
MOCHI_LLM_URL=https://api.groq.com/openai/v1
MOCHI_LLM_MODEL=llama-3.3-70b-versatile
MOCHI_LLM_KEY=gsk_xxxxxxxx
```

Config tersimpan di `~/.mochi/config.json`.

---

## Health Reminders

Mochi track durasi nonstop kamu di depan layar dan ngingetin:

| Reminder | Default interval |
|---|---|
| Istirahat mata (20-20-20) | 20 menit |
| Minum air | 45 menit |
| Berdiri & stretch | 90 menit |
| Cek postur | 120 menit |

Toggle via tray icon → **Kesehatan 💪**, atau ubah interval di `~/.mochi/config.json`.

---

## Kontrol

| Aksi | Efek |
|---|---|
| Klik kiri | Pat Mochi |
| Klik kanan | Menu |
| Double klik | Klik global |
| Drag | Angkat & lempar Mochi |
| Goyang mouse cepat | Kaget |

---

## Build .exe (standalone, tanpa Python)

Jalankan `build.bat` (double-click atau lewat terminal):

```bat
build.bat
```

Atau manual:

```bash
pip install pyinstaller
pyinstaller mochi.spec --clean
```

Output: `dist/Mochi.exe` — satu file, tidak perlu Python terinstall, siap dibagikan.

### Auto-start saat Windows nyala

1. `Win + R` → ketik `shell:startup` → Enter
2. Buat shortcut dari `dist/Mochi.exe` ke folder Startup tersebut

---

## Struktur Project

```
mochi/
├── main.py
├── requirements.txt
├── assets/
│   ├── sprites/       # PNG animasi (96x96, transparan hitam)
│   └── icons/
└── src/
    ├── cat.py         # State machine & sprite loader
    ├── behavior.py    # Logic perilaku & AI integration
    ├── llm.py         # LLM client (history, action, chat)
    ├── health.py      # Health reminder engine
    ├── reminders.py   # Pengingat harian terjadwal
    ├── window.py      # Tkinter window & UI
    ├── tray.py        # System tray
    ├── sound.py       # Sound player
    ├── input_watcher.py  # Global keyboard & mouse hook
    └── config.py      # Config persistence (~/.mochi/config.json)
```
