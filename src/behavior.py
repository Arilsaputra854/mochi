import random
import time
from src.cat import Cat, State


class Behavior:
    IDLE_TO_SLEEP = 120  # 2 minutes before auto-sleep
    SLEEP_MIN     = 60   # min sleep seconds
    SLEEP_EXTRA   = 120  # max extra sleep seconds
    WALK_MIN      = 100  # min walk steps (longer walk)
    WALK_MAX      = 300

    def __init__(self, cat: Cat):
        self.cat          = cat
        self._last_active = time.time()
        self._last_typing_time = 0.0
        self._walk_steps  = 0
        self._play_ticks  = 0
        self._sleep_until = None
        self._idle_ticks  = 0
        self._idle_max    = random.randint(300, 800)  # 15s to 40s ticks

        # Weekday Event Flags
        self._fed_today = False
        import datetime
        self._last_fed_date = datetime.date.today()
        self._pulang_date = None
        self._pushed_pulang_later = False

        # Callback registered by PetWindow to open go-home dialog
        self.on_pulang_trigger = None

        cat.on_anim_end = self._on_anim_end
        self._choose_action()

    def _get_time_info(self):
        import datetime
        now = datetime.datetime.now()
        is_weekday = now.weekday() < 5  # Mon-Fri
        hour = now.hour
        minute = now.minute
        return is_weekday, hour, minute

    # ── Public ────────────────────────────────────────────────────────────────

    def tick(self, mx=None, my=None):
        now   = time.time()
        state = self.cat.state

        if state in (State.FALLING, State.LANDING):
            return

        # Daily reset of event flags
        import datetime
        today = datetime.date.today()
        if self._last_fed_date != today:
            self._fed_today = False
            self._last_fed_date = today
            # If it's a new day, clear the packing choice
            self._pushed_pulang_later = False

        is_wk, hr, mn = self._get_time_info()

        # OVERRIDE 1: Weekday Lunch Hunger (12:00 PM - until fed)
        if is_wk and hr == 12 and not self._fed_today:
            if state != State.HUNGRY:
                self.cat.set_state(State.HUNGRY)
            return

        # OVERRIDE 2: Weekday Pulang Event (5:30 PM - until decided)
        if is_wk and (hr > 17 or (hr == 17 and mn >= 30)) and self._pulang_date != today:
            if not self._pushed_pulang_later:
                if state != State.PULANG:
                    self.cat.set_state(State.PULANG)
                    # Trigger popup dialog
                    if self.on_pulang_trigger:
                        self.on_pulang_trigger()
                return

        if state == State.IDLE:
            # Check for Sleepy Bedtime (9:00 PM - 4:00 AM)
            # Sleep transition is much faster if it's bedtime
            idle_sleep_timeout = self.IDLE_TO_SLEEP
            if is_wk and (hr >= 21 or hr < 4):
                idle_sleep_timeout = 20  # falls asleep in 20s if bedtime

            if now - self._last_active > idle_sleep_timeout:
                self._enter_sleep()
                return
            self._idle_ticks += 1
            if self._idle_ticks >= self._idle_max:
                self._idle_ticks = 0
                self._idle_max   = random.randint(300, 800)
                self._choose_action()

        elif state == State.BETE:
            # Same idle countdown for the annoyed state
            if now - self._last_active > self.IDLE_TO_SLEEP:
                self._enter_sleep()
                return
            self._idle_ticks += 1
            if self._idle_ticks >= self._idle_max:
                self._idle_ticks = 0
                self._idle_max   = random.randint(300, 800)
                self._choose_action()

        elif state in (State.WALK_LEFT, State.WALK_RIGHT):
            self._walk_steps -= 1
            if self._walk_steps <= 0 or self.cat.at_edge():
                self._choose_action()

        elif state in (State.PLAYING, State.DANCE, State.SCARE, State.YAWN, 
                       State.STRETCH, State.CLEAN, State.JUMP, State.SIT, 
                       State.SCRATCH, State.WAVE, State.HISS):
            self._play_ticks -= 1
            if self._play_ticks <= 0:
                self._choose_action()

        elif state == State.EATING:
            self._play_ticks -= 1
            if self._play_ticks <= 0:
                self._choose_action()

        elif state == State.SLEEPING:
            if self._sleep_until and now > self._sleep_until:
                self._exit_sleep()

        elif state == State.TYPING:
            # If user stopped typing for more than 1.5 seconds, return to normal action
            if now - self._last_typing_time > 1.5:
                self._choose_action()

        elif state == State.MOUSE_CLICK:
            # Revert to normal loop once click animation finishes
            pass

        elif state == State.PAT:
            # Revert to normal loop once patting animation finishes
            pass

    def feed_cat(self):
        """Satisfies cat hunger and plays eating/happy animation."""
        self._fed_today = True
        self._last_active = time.time()
        self.cat.set_state(State.EATING)
        self._play_ticks = 150  # eat for ~7.5 seconds

    def force_sleep(self):
        """Forces the cat to go to sleep immediately from context menu."""
        self._last_active = 0.0  # Reset activity
        self._enter_sleep()

    def pulang_later(self):
        """Called when user selects Nanti to go-home prompt."""
        import datetime
        self._pushed_pulang_later = True
        self._pulang_date = datetime.date.today()
        self.cat.set_state(State.BETE)

    def force_action(self, state):
        """Forces the cat to perform a specific animation for testing."""
        self._last_active = time.time()
        
        # Wake up if sleeping
        if self.cat.state in (State.SLEEPING, State.SLEEP_ENTER):
            self._exit_sleep()
            
        self.cat.set_state(state)
        # Give it a longer duration for testing so user can see it
        self._play_ticks = 150 
        
    def on_clicked(self):
        self._last_active = time.time()
        # If sleeping, wake up first
        if self.cat.state in (State.SLEEPING, State.SLEEP_ENTER):
            self._exit_sleep()
        elif self.cat.state in (State.HUNGRY, State.PULANG):
            # Don't interrupt important events on click
            pass
        else:
            # Show patting (love heart) animation!
            self.cat.set_state(State.PAT)

    def notify_typing(self):
        """Call when user is actively typing."""
        self._last_active = time.time()
        self._last_typing_time = time.time()
        
        state = self.cat.state
        if state in (State.SLEEPING, State.SLEEP_ENTER):
            self._exit_sleep()
        elif state in (State.HUNGRY, State.PULANG, State.EATING):
            # Too busy/hungry to type
            pass
        elif state in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT, State.TYPING, State.BETE, State.MOUSE_CLICK, State.PAT):
            self.cat.set_state(State.TYPING)

    def notify_click(self):
        """Call when system-wide mouse click is detected."""
        self._last_active = time.time()
        state = self.cat.state
        if state in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT, State.BETE, State.MOUSE_CLICK):
            self.cat.set_state(State.MOUSE_CLICK)

    # ── Private ───────────────────────────────────────────────────────────────

    def _on_anim_end(self, state: State):
        if state == State.SLEEP_ENTER:
            self.cat.set_state(State.SLEEPING)
            
            # Stays asleep longer if it's bedtime
            is_wk, hr, mn = self._get_time_info()
            base_sleep = self.SLEEP_MIN
            extra_sleep = self.SLEEP_EXTRA
            if is_wk and (hr >= 21 or hr < 4):
                base_sleep = 180  # sleeps for at least 3 minutes
                extra_sleep = 240
                
            self._sleep_until = (time.time() + base_sleep +
                                 random.randint(0, extra_sleep))
        elif state == State.SLEEP_EXIT:
            self._last_active = time.time()
            self._choose_action()
        elif state in (State.CLICKED, State.MOUSE_CLICK, State.PAT, State.LANDING):
            # Once action animation loop completes, choose new action
            self._choose_action()

    def _choose_action(self):
        self._last_active = time.time()
        self._idle_ticks  = 0
        is_wk, hr, mn = self._get_time_info()

        # Sleepy Bedtime choices (60% sleep, 30% idle, 10% walk)
        if is_wk and (hr >= 21 or hr < 4):
            r = random.random()
            if r < 0.60:
                self._enter_sleep()
            elif r < 0.90:
                # If cat is pouting from delayed pulang, show BETE instead of IDLE
                import datetime
                if self._pushed_pulang_later and datetime.date.today() == self._pulang_date:
                    self.cat.set_state(State.BETE)
                else:
                    self.cat.set_state(State.IDLE)
            else:
                self.cat.set_state(random.choice([State.WALK_LEFT, State.WALK_RIGHT]))
                self._walk_steps = random.randint(self.WALK_MIN // 2, self.WALK_MAX // 2)
            return

        # Normal choices
        r = random.random()
        if r < 0.30:
            import datetime
            if self._pushed_pulang_later and datetime.date.today() == self._pulang_date:
                self.cat.set_state(State.BETE)
            else:
                self.cat.set_state(State.IDLE)
        elif r < 0.45:
            self.cat.set_state(State.WALK_LEFT)
            self._walk_steps = random.randint(self.WALK_MIN, self.WALK_MAX)
        elif r < 0.60:
            self.cat.set_state(State.WALK_RIGHT)
            self._walk_steps = random.randint(self.WALK_MIN, self.WALK_MAX)
        elif r < 0.70:
            self.cat.set_state(State.PLAYING)
            self._play_ticks = random.randint(200, 500)
        else:
            # Pick a random special action and let it run for a few seconds!
            specials = [State.DANCE, State.SCARE, State.YAWN, State.STRETCH, State.CLEAN, State.JUMP, State.SIT, State.SCRATCH, State.WAVE, State.HISS]
            self.cat.set_state(random.choice(specials))
            self._play_ticks = random.randint(60, 150)  # Runs for 3 to 7.5 seconds

    def _enter_sleep(self):
        self.cat.snap_to_floor()
        self.cat.set_state(State.SLEEP_ENTER)

    def _exit_sleep(self):
        self._sleep_until = None
        self.cat.set_state(State.SLEEP_EXIT)
