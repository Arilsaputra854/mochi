import os
import json

# Stored in the user's home so it survives app updates and works from a frozen exe.
CONFIG_DIR  = os.path.join(os.path.expanduser('~'), '.mochi')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

DEFAULTS = {
    # LLM
    'llm_url':           'https://api.groq.com/openai/v1',
    'llm_model':         'llama-3.3-70b-versatile',
    'llm_key':           '',
    # General
    'sound_enabled':     True,
    'reminders_enabled': True,
    # Persona
    'pet_name':               'Mochi',
    'pet_language':           'id',
    'pet_personality':        'kucing virtual lucu, ramah, santai',
    'system_prompt_override': '',
    # LLM autonomous behavior
    'llm_autonomous':         True,
    'llm_action_cooldown':    45,   # seconds between LLM-driven actions
    # Health reminders (minutes)
    'health_enabled':         True,
    'health_break_gap_min':   5,    # gap without typing = session reset
    'health_eye_min':         20,
    'health_water_min':       45,
    'health_move_min':        90,
    'health_posture_min':     120,
}

# Map config keys to env-var fallbacks (used only when the file has no value).
_ENV_FALLBACK = {
    'llm_url':   'MOCHI_LLM_URL',
    'llm_model': 'MOCHI_LLM_MODEL',
    'llm_key':   'MOCHI_LLM_KEY',
}


class Config:
    def __init__(self):
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, encoding='utf-8') as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data.update(loaded)
            except Exception:
                pass
        # Env vars fill in only what the file/defaults left empty.
        for key, env in _ENV_FALLBACK.items():
            if not self.data.get(key) and os.environ.get(env):
                self.data[key] = os.environ[env]

    def save(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception:
            return False

    def get(self, key):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
