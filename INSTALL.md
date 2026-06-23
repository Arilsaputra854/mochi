# Cara Install Mochi 🐱

Sekarang setelah aplikasimu jauh lebih canggih, kamu mungkin ingin menjalankannya secara otomatis atau menjadikannya aplikasi mandiri (`.exe`)! Berikut adalah panduannya:

## Opsi 1: Menjadikan Aplikasi Standalone (.exe)
Jika kamu ingin membuat file `.exe` yang bisa diklik dua kali (tanpa perlu membuka Terminal atau mengetik `python main.py`), kamu bisa menggunakan `pyinstaller`.

1. Buka Terminal/PowerShell di folder aplikasimu (`d:\Aril Saputra\Project\pet`).
2. Install PyInstaller dengan mengetik: 
   ```bash
   pip install pyinstaller
   ```
3. Buat file `.exe` dengan mengetik:
   ```bash
   pyinstaller --noconsole --onefile main.py
   ```
   *Catatan: Bendera `--noconsole` berguna agar jendela terminal hitam tidak ikut muncul saat kamu menjalankan aplikasinya.*
4. Tunggu prosesnya selesai. Kamu akan menemukan file `main.exe` di dalam folder `dist`. Pindahkan file tersebut dan folder `assets` ke manapun kamu mau!

## Opsi 2: Berjalan Otomatis Saat Komputer Nyala
Jika kamu ingin Mochi selalu menemanimu sejak kamu menyalakan komputer:

1. Tekan tombol `Windows + R` di keyboardmu.
2. Ketik `shell:startup` dan tekan Enter. Folder *Startup* Windows akan terbuka.
3. Buat **Shortcut** dari file `main.exe` yang sudah kamu buat pada Opsi 1 (Klik kanan `main.exe` -> Create Shortcut).
4. Pindahkan file *Shortcut* tersebut ke dalam folder *Startup* tadi.
5. Selesai! Kucingmu akan langsung muncul setiap kali kamu menyalakan PC/Laptop!
