import time
import ctypes
from ctypes import wintypes
import threading

try:
    import keyboard as _kb
    _HAS_KB = True
except ImportError:
    _HAS_KB = False


# WinAPI Hooking Constants
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


class InputWatcher:
    BURST_WINDOW = 2.0
    BURST_COUNT  = 1

    def __init__(self, on_typing=None, on_click=None, root=None):
        self._on_typing = on_typing
        self._on_click  = on_click
        self._root      = root        # Tkinter root for thread-safe scheduling
        self._last_key  = 0.0
        self._key_count = 0
        
        self._mouse_hook = None
        self._mouse_thread = None
        self._hook_running = False

    def start(self):
        # Start keyboard watcher
        if _HAS_KB:
            _kb.on_press(self._handle)
            
        # Start system-wide mouse watcher
        if self._on_click:
            self._hook_running = True
            self._mouse_thread = threading.Thread(target=self._run_mouse_hook, daemon=True)
            self._mouse_thread.start()

    def stop(self):
        # Stop keyboard watcher
        if _HAS_KB:
            try:
                _kb.unhook_all()
            except Exception:
                pass
                
        # Stop mouse watcher
        self._hook_running = False
        if self._mouse_hook:
            try:
                user32.UnhookWindowsHookEx(self._mouse_hook)
                # Post WM_QUIT to terminate the background message loop
                user32.PostThreadMessageW(self._mouse_thread.ident, 18, 0, 0)
            except Exception:
                pass

    def _handle(self, _event):
        now = time.time()
        if now - self._last_key < self.BURST_WINDOW:
            self._key_count += 1
        else:
            self._key_count = 1
        self._last_key = now
        if self._key_count >= self.BURST_COUNT and self._on_typing:
            self._key_count = 0
            if self._root:
                self._root.after(0, self._on_typing)
            else:
                self._on_typing()

    def _run_mouse_hook(self):
        def hook_callback(nCode, wParam, lParam):
            if nCode >= 0:
                if wParam in (WM_LBUTTONDOWN, WM_RBUTTONDOWN):
                    if self._on_click:
                        if self._root:
                            self._root.after(0, self._on_click)
                        else:
                            self._on_click()
            return user32.CallNextHookEx(self._mouse_hook, nCode, wParam, lParam)

        self._proc = HOOKPROC(hook_callback)
        self._mouse_hook = user32.SetWindowsHookExW(
            WH_MOUSE_LL, self._proc, kernel32.GetModuleHandleW(None), 0
        )
        
        if not self._mouse_hook:
            return

        # Message loop required for low-level hooks
        msg = wintypes.MSG()
        while self._hook_running and user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
