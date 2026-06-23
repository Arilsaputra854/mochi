import tkinter as tk
from src.cat import Cat, State
from src.behavior import Behavior
from src.input_watcher import InputWatcher
from src.tray import TrayIcon

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

        self.cat      = Cat()
        self.behavior = Behavior(self.cat)
        self.watcher  = InputWatcher(
            on_typing=self.behavior.notify_typing,
            on_click=self.behavior.notify_click,
            root=self.root
        )
        self.tray     = TrayIcon(self)

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

        # Right-click context Menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Kasih Makan 🐟", command=self._feed_cat)
        self.menu.add_command(label="Tidur 😴", command=self._force_sleep)
        
        self.anim_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Tes Animasi 🎬", menu=self.anim_menu)
        for label, state in [
            ("Menari", State.DANCE), ("Kaget", State.SCARE), ("Menguap", State.YAWN),
            ("Peregangan", State.STRETCH), ("Mandi", State.CLEAN), ("Lompat", State.JUMP),
            ("Duduk", State.SIT), ("Garuk Telinga", State.SCRATCH), ("Sapa", State.WAVE),
            ("Marah", State.HISS)
        ]:
            self.anim_menu.add_command(label=label, command=lambda s=state: self.behavior.force_action(s))

        self.menu.add_separator()
        self.menu.add_command(label="Tampilkan / Sembunyikan", command=self.tray._toggle)
        self.menu.add_command(label="Keluar MeowMate 🚪", command=self.quit)
        self.label.bind('<Button-3>', self._show_menu)

        # Register event callbacks
        self.behavior.on_pulang_trigger = self._show_pulang_popup
        self.popup_open = False

        self._tick()

    def _show_menu(self, e):
        self.menu.post(e.x_root, e.y_root)

    def _feed_cat(self):
        self.behavior.feed_cat()

    def _force_sleep(self):
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
            # Check if dropped in the air, if so trigger falling physics!
            floor = self.cat.screen_h - self.cat.SPRITE_H
            if self.cat.y < floor - 2:
                self.cat.set_state(State.FALLING)
            else:
                self.cat.snap_to_floor()
                self.behavior._choose_action()

    def _mouse_motion(self, e):
        if self._dragging:
            return
        if self.cat.state not in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT, State.BETE):
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
        self.root.after(FRAME_MS, self._tick)

    def show(self):
        self.root.deiconify()
        self.root.attributes('-topmost', True)

    def hide(self):
        self.root.withdraw()

    def quit(self):
        self.watcher.stop()
        self.tray.stop()
        self.root.destroy()

    def run(self):
        self.tray.start()
        self.watcher.start()
        self.root.mainloop()
