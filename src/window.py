import time
import threading
import tkinter as tk
from src.cat import Cat, State
from src.behavior import Behavior
from src.input_watcher import InputWatcher
from src.tray import TrayIcon
from src.sound import SoundPlayer
from src.reminders import ReminderManager
from src.health import HealthMonitor
from src.llm import LLMClient, LLMError
from src.config import Config

# States the cat can be tested into from the tray "Test Animasi" submenu.
TEST_ANIMATIONS = [
    ("Menari", State.DANCE), ("Kaget", State.SCARE), ("Menguap", State.YAWN),
    ("Peregangan", State.STRETCH), ("Mandi", State.CLEAN), ("Lompat", State.JUMP),
    ("Duduk", State.SIT), ("Garuk Telinga", State.SCRATCH), ("Sapa", State.WAVE),
    ("Marah", State.HISS),
]

FRAME_MS = 50  # ~20fps


class PetWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes('-transparentcolor', 'black')
        self.root.config(bg='black')

        self.label = tk.Label(self.root, bd=0, bg='black')
        self.label.pack()

        self.config    = Config()
        self.cat       = Cat()
        self.sound     = SoundPlayer(enabled=self.config.get('sound_enabled'))
        self.behavior  = Behavior(self.cat, sound=self.sound, config=self.config)
        self.reminders = ReminderManager(enabled=self.config.get('reminders_enabled'))
        self.health    = HealthMonitor(config=self.config,
                                       enabled=self.config.get('health_enabled'))
        self.llm       = LLMClient(config=self.config)
        self.settings_win = None

        # Speech bubble state
        self._bubble       = None
        self._bubble_until = 0.0

        # Chat state
        self._ask_dialog = None
        self._thinking   = False
        def _on_typing():
            self.behavior.notify_typing()
            self.health.notify_activity()

        def _on_click():
            self.behavior.notify_click()
            self.health.notify_activity()

        self.watcher  = InputWatcher(
            on_typing=_on_typing,
            on_click=_on_click,
            root=self.root
        )
        self.tray     = TrayIcon(self)

        # Wire LLM autonomous behavior callback
        self.behavior.on_need_llm_action = self._on_llm_action_needed

        self._drag_ox  = 0
        self._drag_oy  = 0
        self._dragging = False
        self._motion_history = []

        self.label.bind('<ButtonPress-1>',   self._press)
        self.label.bind('<Double-Button-1>', self._double_click)
        self.label.bind('<B1-Motion>',       self._drag)
        self.label.bind('<ButtonRelease-1>', self._release)
        self.label.bind('<Motion>',          self._mouse_motion)
        self.root.bind('<Escape>', lambda _: self.quit())

        # Right-click on the cat = user-facing actions only.
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Tanya Mochi 💬", command=self._ask_dialog_open)
        self.menu.add_command(label="Kasih Makan 🐟", command=self._feed_cat)
        self.menu.add_command(label="Tidur 😴", command=self._force_sleep)
        self.menu.add_separator()
        self.menu.add_command(label="Pengaturan ⚙️", command=self.open_settings)
        self.menu.add_command(label="Sembunyikan 👻", command=self.tray._toggle)
        self.menu.add_command(label="Keluar Mochi 🚪", command=self.quit)
        self.label.bind('<Button-3>', self._show_menu)

        # Register event callbacks
        self.behavior.on_pulang_trigger = self._show_pulang_popup
        self.popup_open = False

        self._tick()

    def _show_menu(self, e):
        self.menu.post(e.x_root, e.y_root)

    def _feed_cat(self):
        self.behavior.feed_cat()

    # ── Toggles & tests (driven from the tray menu) ─────────────────────────

    def toggle_sound(self):
        on = self.sound.toggle()
        self.config.set('sound_enabled', on)
        self.config.save()
        return on

    def toggle_reminders(self):
        on = self.reminders.toggle()
        self.config.set('reminders_enabled', on)
        self.config.save()
        return on

    def toggle_health(self):
        on = self.health.toggle()
        self.config.set('health_enabled', on)
        self.config.save()
        if on:
            self.health.reset_session()
        return on

    def test_animation(self, state):
        self.behavior.force_action(state)

    def test_zoomies(self):
        self.behavior._start_zoomies()

    def test_reminder(self):
        """Fire a sample reminder bubble now, ignoring schedule."""
        self.behavior.remind()
        self._show_bubble("Tes pengingat: jangan lupa makan & solat ya 🕌🍚")

    # ── Settings window ─────────────────────────────────────────────────────

    def open_settings(self):
        if self.settings_win is not None:
            try:
                self.settings_win.lift()
                self.settings_win.focus_force()
                return
            except tk.TclError:
                self.settings_win = None

        win = tk.Toplevel(self.root)
        self.settings_win = win
        win.title("Pengaturan Mochi")
        win.attributes('-topmost', True)
        win.config(bg='#2b2b2b', padx=16, pady=14)
        win.resizable(False, False)

        def on_close():
            self.settings_win = None
            win.destroy()
        win.protocol('WM_DELETE_WINDOW', on_close)
        win.bind('<Escape>', lambda _e: on_close())

        tk.Label(win, text="Pengaturan Mochi ⚙️", fg='#ffcc00', bg='#2b2b2b',
                 font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')

        def field(row, label, value, show=None, width=40):
            tk.Label(win, text=label, fg='#ddd', bg='#2b2b2b',
                     font=('Segoe UI', 9)).grid(row=row, column=0, columnspan=2, sticky='w', pady=(6, 1))
            e = tk.Entry(win, width=width, font=('Consolas', 10), bg='#3c3c3c',
                         fg='white', insertbackground='white', bd=0, show=show)
            e.insert(0, value or '')
            e.grid(row=row + 1, column=0, columnspan=2, sticky='we', ipady=4)
            return e

        # ── Persona ──────────────────────────────────────────────────────────
        tk.Label(win, text="— Persona —", fg='#888', bg='#2b2b2b',
                 font=('Segoe UI', 8)).grid(row=1, column=0, columnspan=2, sticky='w', pady=(4, 0))
        name_e = field(2, "Nama kucing:", self.config.get('pet_name'), width=20)
        personality_e = field(4, "Kepribadian (deskripsi singkat):",
                              self.config.get('pet_personality'), width=40)

        # ── AI / LLM ─────────────────────────────────────────────────────────
        tk.Label(win, text="— AI / LLM —", fg='#888', bg='#2b2b2b',
                 font=('Segoe UI', 8)).grid(row=7, column=0, columnspan=2, sticky='w', pady=(8, 0))
        url_e   = field(8,  "Base URL (OpenAI-compatible):", self.config.get('llm_url'))
        model_e = field(10, "Nama Model:", self.config.get('llm_model'))
        key_e   = field(12, "API Key:", self.config.get('llm_key'), show='•')

        show_key = tk.IntVar(value=0)
        def toggle_key():
            key_e.config(show='' if show_key.get() else '•')
        tk.Checkbutton(win, text="Tampilkan key", variable=show_key, command=toggle_key,
                       fg='#aaa', bg='#2b2b2b', selectcolor='#2b2b2b',
                       activebackground='#2b2b2b', activeforeground='#fff',
                       font=('Segoe UI', 8)).grid(row=14, column=0, sticky='w', pady=(2, 4))

        autonomous_var = tk.IntVar(value=1 if self.config.get('llm_autonomous') else 0)
        tk.Checkbutton(win, text="Kucing bergerak otomatis pakai AI (jika key diisi)",
                       variable=autonomous_var,
                       fg='#ccc', bg='#2b2b2b', selectcolor='#2b2b2b',
                       activebackground='#2b2b2b', activeforeground='#fff',
                       font=('Segoe UI', 8)).grid(row=15, column=0, columnspan=2, sticky='w', pady=(0, 8))

        status = tk.Label(win, text="", fg='#9ad', bg='#2b2b2b',
                          font=('Segoe UI', 8), wraplength=320, justify='left')
        status.grid(row=16, column=0, columnspan=2, sticky='we', pady=(4, 6))

        def apply_fields():
            self.config.set('pet_name',        name_e.get().strip() or 'Mochi')
            self.config.set('pet_personality', personality_e.get().strip())
            self.config.set('llm_url',         url_e.get().strip())
            self.config.set('llm_model',       model_e.get().strip())
            self.config.set('llm_key',         key_e.get().strip())
            self.config.set('llm_autonomous',  bool(autonomous_var.get()))

        def save():
            apply_fields()
            ok = self.config.save()
            status.config(text="✓ Tersimpan." if ok else "✗ Gagal menyimpan.",
                          fg='#7d7' if ok else '#f88')

        def test_conn():
            apply_fields()
            status.config(text="Menguji koneksi…", fg='#9ad')

            def worker():
                try:
                    self.llm.ask("ping", add_to_history=False)
                    self.root.after(0, lambda: status.config(text="✓ Koneksi OK!", fg='#7d7'))
                except LLMError as e:
                    msg = str(e)
                    self.root.after(0, lambda: status.config(text=f"✗ {msg}", fg='#f88'))
            threading.Thread(target=worker, daemon=True).start()

        btns = tk.Frame(win, bg='#2b2b2b')
        btns.grid(row=17, column=0, columnspan=2, pady=(4, 0), sticky='e')
        tk.Button(btns, text="Tes Koneksi", bg='#3a7', fg='white', bd=0, width=11,
                  activebackground='#295', command=test_conn).pack(side='left', padx=4)
        tk.Button(btns, text="Simpan", bg='#4caf50', fg='white', bd=0, width=9,
                  activebackground='#3e8e41', command=save).pack(side='left', padx=4)
        tk.Button(btns, text="Tutup", bg='#777', fg='white', bd=0, width=8,
                  activebackground='#555', command=on_close).pack(side='left', padx=4)

        # Center near the cat
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        px = self.cat.x + self.cat.SPRITE_W // 2 - w // 2
        py = self.cat.y - h - 10
        px = max(0, px)
        if py < 0:
            py = 40
        win.geometry(f'+{px}+{py}')
        key_e.focus_set()

    # ── Chat with the cat (LLM) ─────────────────────────────────────────────

    def _ask_dialog_open(self):
        if self._thinking:
            return  # already busy answering
        if self._ask_dialog:
            try:
                self._ask_dialog.lift()
                self._ask_dialog.focus_force()
            except tk.TclError:
                pass
            return

        self._ask_dialog = tk.Toplevel(self.root)
        self._ask_dialog.overrideredirect(True)
        self._ask_dialog.attributes('-topmost', True)
        self._ask_dialog.config(bg='#2b2b2b', bd=2, relief='groove')

        tk.Label(self._ask_dialog, text="Tanya Mochi 🐱", fg='#ffcc00',
                 bg='#2b2b2b', font=('Segoe UI', 9, 'bold')).pack(padx=8, pady=(6, 2))

        entry = tk.Entry(self._ask_dialog, width=34, font=('Segoe UI', 10),
                         bg='#3c3c3c', fg='white', insertbackground='white', bd=0)
        entry.pack(padx=8, pady=2, ipady=4)
        entry.focus_set()

        btns = tk.Frame(self._ask_dialog, bg='#2b2b2b')
        btns.pack(pady=6)
        tk.Button(btns, text="Tanya", bg='#4caf50', fg='white', bd=0, width=8,
                  activebackground='#3e8e41',
                  command=lambda: self._ask_submit(entry.get())).pack(side='left', padx=6)
        tk.Button(btns, text="Batal", bg='#777', fg='white', bd=0, width=8,
                  activebackground='#555',
                  command=self._ask_dialog_close).pack(side='left', padx=6)

        entry.bind('<Return>', lambda _e: self._ask_submit(entry.get()))
        self._ask_dialog.bind('<Escape>', lambda _e: self._ask_dialog_close())

        # Position above the cat
        px = self.cat.x + self.cat.SPRITE_W // 2 - 130
        py = self.cat.y - 120
        px = max(self.cat.screen_x, min(px, self.cat.screen_w - 260))
        if py < self.cat.screen_y:
            py = self.cat.y + self.cat.SPRITE_H + 4
        self._ask_dialog.geometry(f'+{px}+{py}')

    def _ask_dialog_close(self):
        if self._ask_dialog:
            try:
                self._ask_dialog.destroy()
            except tk.TclError:
                pass
            self._ask_dialog = None

    def _ask_submit(self, question):
        question = (question or '').strip()
        if not question:
            return
        self._ask_dialog_close()
        self._thinking = True
        self.behavior.start_thinking()
        self._show_bubble("Hmm, mikir dulu ya... 🤔", duration_ms=600000)

        def worker():
            try:
                answer = self.llm.ask(question)
                self.root.after(0, lambda: self._on_answer(answer, ok=True))
            except LLMError as e:
                msg = str(e)
                self.root.after(0, lambda: self._on_answer(
                    f"Aduh, gagal nyambung ke otakku 😿\n({msg})", ok=False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_answer(self, text, ok=True):
        self._thinking = False
        self.behavior.finish_thinking(ok=ok)
        # Longer bubbles linger longer (8s + 55ms/char, capped 30s)
        duration = min(30000, 8000 + len(text) * 55)
        self._show_bubble(text, duration_ms=duration, wraplength=260)

    # ── Speech bubble ───────────────────────────────────────────────────────

    def _show_bubble(self, text, duration_ms=7000, wraplength=200):
        self._dismiss_bubble()
        self._bubble = tk.Toplevel(self.root)
        self._bubble.overrideredirect(True)
        self._bubble.attributes('-topmost', True)
        self._bubble.config(bg='#d9a441', bd=0)

        inner = tk.Frame(self._bubble, bg='#fff7e0', bd=0)
        inner.pack(padx=2, pady=2)
        lbl = tk.Label(inner, text=text, bg='#fff7e0', fg='#5a3e1b',
                       font=('Segoe UI', 10, 'bold'), wraplength=wraplength,
                       justify='left', padx=12, pady=8)
        lbl.pack()
        # Click bubble to dismiss early
        for w in (self._bubble, inner, lbl):
            w.bind('<Button-1>', lambda _e: self._dismiss_bubble())

        self._bubble_until = time.time() + duration_ms / 1000.0
        self._position_bubble()

    def _position_bubble(self):
        if not self._bubble:
            return
        try:
            self._bubble.update_idletasks()
            bw = self._bubble.winfo_width()
            bh = self._bubble.winfo_height()
        except tk.TclError:
            return
        bx = self.cat.x + self.cat.SPRITE_W // 2 - bw // 2
        by = self.cat.y - bh - 4
        # Clamp horizontally to the cat's monitor work area
        bx = max(self.cat.screen_x, min(bx, self.cat.screen_w - bw))
        # If no room above, drop the bubble below the cat
        if by < self.cat.screen_y:
            by = self.cat.y + self.cat.SPRITE_H + 4
        self._bubble.geometry(f'+{bx}+{by}')

    def _dismiss_bubble(self):
        if self._bubble:
            try:
                self._bubble.destroy()
            except tk.TclError:
                pass
            self._bubble = None

    def _force_sleep(self):
        self.health.reset_session()
        self.behavior.force_sleep()

    def _show_pulang_popup(self):
        if self.popup_open:
            return
        self.popup_open = True
        
        # Create Toplevel overlay dialog
        self.popup = tk.Toplevel(self.root)
        self.popup.overrideredirect(True)
        self.popup.attributes('-topmost', True)
        self.popup.config(bg='#2b2b2b', bd=2, relief='groove')
        
        # Position it slightly above the cat
        px = self.cat.x - 40
        py = self.cat.y - 70
        self.popup.geometry(f'180x64+{px}+{py}')
        
        lbl = tk.Label(self.popup, text="Yuk pulang kerja!~", fg='#ffcc00', bg='#2b2b2b', font=('Arial', 10, 'bold'))
        lbl.pack(pady=4)
        
        btn_frame = tk.Frame(self.popup, bg='#2b2b2b')
        btn_frame.pack()
        
        btn_yes = tk.Button(btn_frame, text="Yuk!", bg='#4caf50', fg='white', command=self._pulang_yes, width=6, bd=0, activebackground='#3e8e41')
        btn_yes.pack(side='left', padx=10)
        
        btn_no = tk.Button(btn_frame, text="Nanti", bg='#f44336', fg='white', command=self._pulang_no, width=6, bd=0, activebackground='#da190b')
        btn_no.pack(side='left', padx=10)

    def _pulang_yes(self):
        self.quit()

    def _pulang_no(self):
        self.popup.destroy()
        self.popup_open = False
        self.behavior.pulang_later()

    # ── LLM autonomous action ────────────────────────────────────────────────

    def _on_llm_action_needed(self, context):
        if not self.llm.is_configured():
            self.behavior.apply_llm_action_fallback()
            return

        def worker():
            try:
                result  = self.llm.ask_for_action(context)
                action  = result.get('action', 'IDLE')
                message = result.get('message', '')
                self.root.after(0, lambda: self._apply_llm_action(action, message))
            except Exception:
                self.root.after(0, self.behavior.apply_llm_action_fallback)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_llm_action(self, action, message):
        self.behavior.apply_llm_action(action)
        if message:
            self._show_bubble(message, duration_ms=5000)

    def _press(self, e):
        self._drag_ox  = e.x_root - self.cat.x
        self._drag_oy  = e.y_root - self.cat.y
        self._dragging = False
        
    def _double_click(self, e):
        self.behavior.notify_click()

    def _drag(self, e):
        self._dragging = True
        self.cat.set_state(State.DRAGGED) # Set state to DRAGGED when wiggling!
        self.cat.x = e.x_root - self._drag_ox
        self.cat.y = e.y_root - self._drag_oy
        self.cat.clamp()
        self._place()

    def _release(self, e):
        if not self._dragging:
            self.behavior.on_clicked()
        else:
            self._dragging = False
            # Check if dropped near the top edge of the screen!
            top_threshold = self.cat.screen_y + 15
            if self.cat.y <= top_threshold:
                self.cat.y = self.cat.screen_y
                self.cat.set_state(State.CLINGING)
                self._place()
            # Check if dropped near the right edge of the screen!
            elif self.cat.x >= self.cat.screen_w - self.cat.SPRITE_W - 20:
                self.cat.x = self.cat.screen_w - self.cat.SPRITE_W
                self.cat.set_state(State.CLIMBING)
                self._place()
            # Check if dropped in the air, if so trigger falling physics!
            else:
                floor = self.cat.screen_h - self.cat.SPRITE_H
                if self.cat.y < floor - 2:
                    self.cat.set_state(State.FALLING)
                else:
                    self.cat.snap_to_floor()
                    self.behavior._choose_action()

    def _mouse_motion(self, e):
        if self._dragging:
            return
        if self.cat.state not in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT,
                                   State.RUN_LEFT, State.RUN_RIGHT, State.BETE):
            return
            
        import time
        now = time.time()
        # Clean history older than 1.0 second
        self._motion_history = [h for h in self._motion_history if now - h[0] < 1.0]
        self._motion_history.append((now, e.x))
        
        if len(self._motion_history) >= 6:
            dirs = []
            for i in range(1, len(self._motion_history)):
                dx = self._motion_history[i][1] - self._motion_history[i-1][1]
                if abs(dx) > 3: # filter jitter
                    dirs.append(1 if dx > 0 else -1)
            
            switches = 0
            last_dir = None
            for d in dirs:
                if last_dir is not None and d != last_dir:
                    switches += 1
                last_dir = d
                
            if switches >= 3:
                self._motion_history.clear()
                self.behavior.on_clicked()

    def _place(self):
        self.root.geometry(f'{self.cat.SPRITE_W}x{self.cat.SPRITE_H}+{self.cat.x}+{self.cat.y}')

    def _tick(self):
        # Query pointer position relative to the cat window's top-left corner
        # pointerx and rootx are in the same coordinate space, so subtraction cancels scaling/offsets
        rx = self.root.winfo_pointerx() - self.root.winfo_rootx()
        ry = self.root.winfo_pointery() - self.root.winfo_rooty()

        frame = self.cat.get_frame(rx, ry)
        if frame:
            self.label.configure(image=frame)
        self._place()
        self.behavior.tick(rx + self.cat.x, ry + self.cat.y) # Pass global cursor pos to behavior tick
        self.cat.tick(rx + self.cat.x, ry + self.cat.y)

        # Scheduled reminders → speech bubble + cat reaction
        due = self.reminders.check()
        if due:
            self.behavior.remind()
            self._show_bubble(due)

        # Health reminders (eye strain, water, stretch, posture)
        health_due = self.health.check()
        if health_due:
            _, health_msg = health_due
            self.behavior.remind()
            self._show_bubble(health_msg, duration_ms=12000, wraplength=280)

        # Keep an active bubble glued above the cat; auto-dismiss when expired
        if self._bubble:
            if time.time() > self._bubble_until:
                self._dismiss_bubble()
            else:
                self._position_bubble()

        self.root.after(FRAME_MS, self._tick)

    def show(self):
        self.root.deiconify()
        self.root.attributes('-topmost', True)

    def hide(self):
        self.root.withdraw()

    def quit(self):
        if self.settings_win is not None:
            try:
                self.settings_win.destroy()
            except tk.TclError:
                pass
        self._ask_dialog_close()
        self._dismiss_bubble()
        self.sound.stop()
        self.watcher.stop()
        self.tray.stop()
        self.root.destroy()

    def run(self):
        self.tray.start()
        self.watcher.start()
        self.root.mainloop()
