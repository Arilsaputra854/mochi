import random
import time
import datetime
from src.cat import Cat, State


class Behavior:
    IDLE_TO_SLEEP   = 120    # seconds idle before auto-sleep
    SLEEP_MIN       = 60     # min sleep duration
    SLEEP_EXTRA     = 120    # extra random sleep duration
    WALK_MIN        = 100
    WALK_MAX        = 300

    # Energy: 0-100. Depletes while awake, restores while sleeping.
    ENERGY_DRAIN    = 0.004  # per tick (~100 units over 20 min awake)
    ENERGY_RESTORE  = 0.012  # per tick (~100 units over 7 min sleeping)

    # Play need: 0-100. Builds while not playing, drains while playing/running.
    PLAY_BUILD      = 0.003  # per tick (~100 units over 25 min)
    PLAY_DRAIN      = 0.030  # per tick (~100 units over 3 min of play)

    def __init__(self, cat: Cat, sound=None):
        self.cat               = cat
        self.sound             = sound
        self._last_active      = time.time()
        self._last_typing_time = 0.0
        self._walk_steps       = 0
        self._run_steps        = 0
        self._play_ticks       = 0
        self._sleep_until      = None
        self._idle_ticks       = 0
        self._idle_max         = random.randint(300, 800)

        # Needs
        self._energy           = 80.0  # start well-rested
        self._play_need        = 0.0

        # Sleep anger tracking
        self._sleep_start      = None  # when SLEEPING state began (deep sleep)
        self._anger_ticks      = 0     # ticks of BETE aftermath remaining
        self._hiss_anger       = False # True when HISS is from sleep disturbance

        # Zoomies
        self._zoomies_remaining = 0

        # Weekday event flags
        self._fed_today           = False
        self._last_fed_date       = datetime.date.today()
        self._pulang_date         = None
        self._pushed_pulang_later = False

        self.on_pulang_trigger = None
        cat.on_anim_end = self._on_anim_end
        self._choose_action()

    def _sfx(self, name, loop=False):
        if self.sound:
            self.sound.play(name, loop=loop)

    def _sfx_stop(self):
        if self.sound:
            self.sound.stop()

    def _get_time_info(self):
        now = datetime.datetime.now()
        return now.weekday() < 5, now.hour, now.minute

    def _is_play_time(self):
        """Cats are naturally playful in morning (7-9) and evening (18-20)."""
        _, hr, _ = self._get_time_info()
        return (7 <= hr < 9) or (18 <= hr < 20)

    def _is_bedtime(self, is_wk, hr):
        return is_wk and (hr >= 21 or hr < 4)

    # ── Public ────────────────────────────────────────────────────────────────

    def tick(self, mx=None, my=None):
        now   = time.time()
        state = self.cat.state

        if state in (State.FALLING, State.LANDING):
            return

        # Hold the thinking pose until the LLM answer arrives (no auto actions,
        # no sleep, no hunger/pulang override while waiting).
        if state == State.THINKING:
            return

        # Daily reset
        today = datetime.date.today()
        if self._last_fed_date != today:
            self._fed_today           = False
            self._last_fed_date       = today
            self._pushed_pulang_later = False

        is_wk, hr, mn = self._get_time_info()

        # Update energy
        if state == State.SLEEPING:
            self._energy = min(100.0, self._energy + self.ENERGY_RESTORE)
        elif state not in (State.SLEEP_ENTER, State.SLEEP_EXIT):
            self._energy = max(0.0, self._energy - self.ENERGY_DRAIN)

        # Update play need
        if state in (State.PLAYING, State.RUN_LEFT, State.RUN_RIGHT,
                     State.JUMP, State.DANCE):
            self._play_need = max(0.0, self._play_need - self.PLAY_DRAIN)
        elif state not in (State.SLEEPING, State.SLEEP_ENTER, State.SLEEP_EXIT):
            self._play_need = min(100.0, self._play_need + self.PLAY_BUILD)

        # OVERRIDE: Weekday lunch hunger (12:00 - until fed)
        if is_wk and hr == 12 and not self._fed_today:
            if state != State.HUNGRY:
                self.cat.set_state(State.HUNGRY)
            return

        # OVERRIDE: Weekday pulang event (17:30+)
        if is_wk and (hr > 17 or (hr == 17 and mn >= 30)) and self._pulang_date != today:
            if not self._pushed_pulang_later:
                if state != State.PULANG:
                    self.cat.set_state(State.PULANG)
                    if self.on_pulang_trigger:
                        self.on_pulang_trigger()
                return

        if state == State.IDLE:
            if self._energy <= 5:
                self._enter_sleep()
                return

            idle_sleep_timeout = self.IDLE_TO_SLEEP
            if self._is_bedtime(is_wk, hr):
                idle_sleep_timeout = 20

            if now - self._last_active > idle_sleep_timeout:
                self._enter_sleep()
                return

            self._idle_ticks += 1
            if self._idle_ticks >= self._idle_max:
                self._idle_ticks = 0
                self._idle_max   = random.randint(300, 800)
                self._choose_action()

        elif state == State.BETE:
            if self._anger_ticks > 0:
                self._anger_ticks -= 1
                if self._anger_ticks == 0:
                    self._choose_action()
            else:
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
            if self._walk_steps <= 0:
                self._choose_action()
            elif self.cat.at_edge():
                # Hit wall — turn around like a real cat, don't call choose_action
                new_dir = State.WALK_RIGHT if state == State.WALK_LEFT else State.WALK_LEFT
                self.cat.set_state(new_dir)
                self._walk_steps = random.randint(60, 180)

        elif state in (State.RUN_LEFT, State.RUN_RIGHT):
            self._run_steps -= 1
            if self._run_steps <= 0 or self.cat.at_edge():
                if self._zoomies_remaining > 0:
                    self._zoomies_remaining -= 1
                    new_dir = State.RUN_RIGHT if state == State.RUN_LEFT else State.RUN_LEFT
                    self.cat.set_state(new_dir)
                    self._run_steps = random.randint(80, 220)
                else:
                    # Zoomies done — catch breath in IDLE, then normal cycle handles next action
                    self._energy = max(0.0, self._energy - 20.0)
                    self._last_active = time.time()
                    self._idle_ticks = 0
                    self._idle_max = random.randint(60, 160)  # ~3-8s panting idle
                    self.cat.set_state(State.IDLE)

        elif state == State.HISS and self._hiss_anger:
            # Anger hiss from sleep disturbance — driven by on_anim_end, not _play_ticks.
            pass

        elif state in (State.PLAYING, State.DANCE, State.SCARE, State.YAWN,
                       State.STRETCH, State.CLEAN, State.JUMP, State.SIT,
                       State.SCRATCH, State.WAVE, State.HISS):
            self._play_ticks -= 1
            if self._play_ticks <= 0:
                # SCARE sometimes triggers panic zoomies!
                if state == State.SCARE and random.random() < 0.55:
                    self._start_zoomies()
                else:
                    self._choose_action()

        elif state == State.EATING:
            self._play_ticks -= 1
            if self._play_ticks <= 0:
                self._energy = min(100.0, self._energy + 20.0)  # food restores energy
                self._choose_action()

        elif state == State.SLEEPING:
            if self._sleep_until and now > self._sleep_until:
                self._exit_sleep()

        elif state == State.TYPING:
            if now - self._last_typing_time > 1.5:
                self._choose_action()

        elif state in (State.MOUSE_CLICK, State.PAT):
            pass

    def feed_cat(self):
        self._fed_today   = True
        self._last_active = time.time()
        self.cat.set_state(State.EATING)
        self._play_ticks  = 150
        self._sfx('eat')

    def force_sleep(self):
        self._last_active = 0.0
        self._enter_sleep()

    def pulang_later(self):
        self._pushed_pulang_later = True
        self._pulang_date         = datetime.date.today()
        self._anger_ticks         = 300  # pout for 15 seconds
        self.cat.set_state(State.BETE)

    def force_action(self, state):
        self._last_active = time.time()
        if self.cat.state in (State.SLEEPING, State.SLEEP_ENTER):
            self._sfx_stop()
            self._sleep_start = None
            self._sleep_until = None
            self.cat.set_state(State.SLEEP_EXIT)
        self.cat.set_state(state)
        self._play_ticks = 150
        if state == State.HISS:
            self._sfx('hiss')

    def on_clicked(self):
        self._last_active = time.time()
        if self.cat.state in (State.SLEEPING, State.SLEEP_ENTER):
            self._wake_with_anger()
        elif self.cat.state in (State.HUNGRY, State.PULANG, State.THINKING):
            pass  # busy — don't interrupt
        else:
            self.cat.set_state(State.PAT)
            self._sfx('meow')

    def notify_typing(self):
        self._last_active      = time.time()
        self._last_typing_time = time.time()
        state = self.cat.state

        if state in (State.SLEEPING, State.SLEEP_ENTER):
            # Keyboard wakes sleeping cat — less angry than direct click
            self._wake_with_anger(mild=True)
        elif state in (State.HUNGRY, State.PULANG, State.EATING):
            pass
        elif state in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT,
                       State.RUN_LEFT, State.RUN_RIGHT, State.TYPING,
                       State.BETE, State.MOUSE_CLICK, State.PAT):
            self.cat.set_state(State.TYPING)

    def start_thinking(self):
        """Enter the thinking pose while waiting for an LLM answer."""
        self._last_active = time.time()
        if self.cat.state in (State.SLEEPING, State.SLEEP_ENTER):
            self._sfx_stop()
            self._sleep_start = None
            self._sleep_until = None
        self._zoomies_remaining = 0
        self._anger_ticks       = 0
        self._hiss_anger        = False
        self.cat.set_state(State.THINKING)

    def finish_thinking(self, ok=True):
        """Answer arrived — wave happily (or hiss on error), then resume."""
        self._last_active = time.time()
        self.cat.set_state(State.WAVE)
        self._play_ticks = 80
        self._sfx('meow' if ok else 'hiss')

    def remind(self):
        """React to a scheduled reminder — wave and meow to grab attention."""
        self._last_active = time.time()
        state = self.cat.state
        if state in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT,
                     State.RUN_LEFT, State.RUN_RIGHT, State.BETE):
            self._zoomies_remaining = 0
            self.cat.set_state(State.WAVE)
            self._play_ticks = 90
        self._sfx('meow')

    def notify_click(self):
        """Global mouse click anywhere on screen — cat reacts like it does to
        typing. A sleeping cat is left alone (so it can nap while you work)."""
        self._last_active = time.time()
        state = self.cat.state
        if state in (State.IDLE, State.WALK_LEFT, State.WALK_RIGHT,
                     State.RUN_LEFT, State.RUN_RIGHT, State.TYPING,
                     State.BETE, State.MOUSE_CLICK, State.PAT):
            self.cat.set_state(State.MOUSE_CLICK)

    # ── Private ───────────────────────────────────────────────────────────────

    def _wake_with_anger(self, mild=False):
        """Wake cat. Anger level scales with how long it was sleeping."""
        self._sfx_stop()  # cut the purr loop
        sleep_duration = (time.time() - self._sleep_start) if self._sleep_start else 0

        if mild and sleep_duration < 20:
            # Barely asleep — just wake, a bit grumpy but not hissing
            self._exit_sleep()
            self._anger_ticks = 60  # grumpy for 3 seconds
            return

        if sleep_duration > 120:
            # Deep sleep interrupted — FURIOUS
            self._sleep_start  = None
            self._sleep_until  = None
            self._anger_ticks  = 500   # angry for 25 seconds
            self._hiss_anger   = True
            self.cat.set_state(State.HISS)
            self._sfx('hiss')
        elif sleep_duration > 30:
            # Moderate sleep — annoyed, skips HISS but goes straight BETE
            self._sleep_start  = None
            self._sleep_until  = None
            self._anger_ticks  = 250   # annoyed for 12 seconds
            self.cat.set_state(State.SLEEP_EXIT)
        else:
            # Light sleep — normal wake, tiny grump
            self._exit_sleep()
            self._anger_ticks = 40

    def _on_anim_end(self, state: State):
        if state == State.SLEEP_ENTER:
            self.cat.set_state(State.SLEEPING)
            self._sleep_start = time.time()
            self._sfx('purr', loop=True)
            is_wk, hr, mn = self._get_time_info()
            base  = self.SLEEP_MIN
            extra = self.SLEEP_EXTRA
            if self._is_bedtime(is_wk, hr):
                base  = 180
                extra = 300
            self._sleep_until = time.time() + base + random.randint(0, extra)

        elif state == State.SLEEP_EXIT:
            self._sleep_start = None
            self._last_active = time.time()
            if self._anger_ticks > 0:
                # Woke up angry — show BETE immediately
                self.cat.set_state(State.BETE)
            else:
                self._choose_action()

        elif state == State.HISS:
            if self._hiss_anger:
                # Anger hiss done — stay angry in BETE
                self._hiss_anger = False
                self.cat.set_state(State.BETE)
            # else: normal hiss from choose_action, tick handles it via _play_ticks

        elif state in (State.CLICKED, State.MOUSE_CLICK, State.PAT, State.LANDING):
            self._choose_action()

    def _choose_action(self):
        self._last_active = time.time()
        self._idle_ticks  = 0
        is_wk, hr, mn    = self._get_time_info()
        today             = datetime.date.today()
        is_pouting        = self._pushed_pulang_later and today == self._pulang_date

        # Anger still active — stay angry
        if self._anger_ticks > 0:
            self.cat.set_state(State.BETE)
            return

        # Exhausted — must sleep
        if self._energy < 15:
            self._enter_sleep()
            return

        # ZOOMIES — play need critically high and has energy for it
        if self._play_need > 82 and self._energy > 30:
            self._start_zoomies()
            return

        # Bedtime behavior
        if self._is_bedtime(is_wk, hr):
            low_energy = self._energy < 50
            r = random.random()
            if r < (0.60 + (0.30 if low_energy else 0.0)):
                self._enter_sleep()
            elif r < 0.90:
                self.cat.set_state(State.BETE if is_pouting else State.IDLE)
            else:
                direction = random.choice([State.WALK_LEFT, State.WALK_RIGHT])
                self.cat.set_state(direction)
                self._walk_steps = random.randint(50, 130)
            return

        # Normal daytime — weighted choices
        is_play_time    = self._is_play_time()
        play_w          = (self._play_need / 100.0 * 0.25) + (0.12 if is_play_time else 0.0)
        sleep_w         = max(0.0, (55.0 - self._energy) / 55.0 * 0.22)

        r = random.random()

        if is_pouting:
            self.cat.set_state(State.BETE)
        elif r < sleep_w:
            self._enter_sleep()
        elif r < sleep_w + 0.27:
            self.cat.set_state(State.IDLE)
        elif r < sleep_w + 0.40:
            self.cat.set_state(State.WALK_LEFT)
            self._walk_steps = random.randint(self.WALK_MIN, self.WALK_MAX)
        elif r < sleep_w + 0.53:
            self.cat.set_state(State.WALK_RIGHT)
            self._walk_steps = random.randint(self.WALK_MIN, self.WALK_MAX)
        elif r < sleep_w + 0.53 + play_w:
            self.cat.set_state(State.PLAYING)
            self._play_ticks = random.randint(180, 460)
        else:
            specials = [
                State.DANCE, State.SCARE, State.YAWN, State.STRETCH,
                State.CLEAN, State.JUMP, State.SIT, State.SCRATCH,
                State.WAVE, State.HISS,
            ]
            pick = random.choice(specials)
            self.cat.set_state(pick)
            self._play_ticks = random.randint(60, 150)
            if pick == State.HISS:
                self._sfx('hiss')
            elif pick == State.SCARE:
                self._sfx('chirp')

    def _start_zoomies(self):
        """Cat gets the zoomies — runs back and forth like a maniac."""
        self.cat.snap_to_floor()
        self._zoomies_remaining = random.randint(2, 5)
        self._run_steps = random.randint(100, 260)
        direction = random.choice([State.RUN_LEFT, State.RUN_RIGHT])
        self.cat.set_state(direction)
        self._sfx('chirp')

    def _enter_sleep(self):
        self.cat.snap_to_floor()
        self.cat.set_state(State.SLEEP_ENTER)

    def _exit_sleep(self):
        self._sfx_stop()  # cut the purr loop
        self._sleep_until = None
        self._sleep_start = None
        self.cat.set_state(State.SLEEP_EXIT)
