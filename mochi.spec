# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files

block_cipher = None

# Collect pywin32 native DLLs (pywintypes##.dll, win32api.pyd, etc.)
pywin32_bins = collect_dynamic_libs('win32')
pywin32_bins += collect_dynamic_libs('win32api')

# All src.* submodules — ensures PyInstaller picks up the package
src_hidden = collect_submodules('src')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=pywin32_bins,
    datas=[
        ('assets/sprites', 'assets/sprites'),
        ('assets/sounds',  'assets/sounds'),
        ('assets/icons',   'assets/icons'),
    ],
    hiddenimports=src_hidden + [
        # pywin32
        'win32api', 'win32con', 'win32gui', 'win32process',
        'win32event', 'win32security', 'winerror',
        'pywintypes',
        # pystray + Pillow
        'pystray', 'pystray._win32',
        'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageTk',
        'PIL._imaging',
        # keyboard
        'keyboard',
        # stdlib that PyInstaller sometimes misses
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.simpledialog',
        'ctypes', 'ctypes.wintypes',
        'json', 'threading', 'urllib.request', 'urllib.error',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'unittest', 'xmlrpc', 'distutils', 'setuptools'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Mochi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/tray_icon.ico',
)
