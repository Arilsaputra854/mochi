import os
import json
import urllib.request
import urllib.error

LLM_URL   = os.environ.get('MOCHI_LLM_URL',   'https://api.groq.com/openai/v1')
LLM_MODEL = os.environ.get('MOCHI_LLM_MODEL', 'llama-3.3-70b-versatile')
LLM_KEY   = os.environ.get('MOCHI_LLM_KEY',   '')

_VALID_ACTIONS = {
    'IDLE', 'WALK_LEFT', 'WALK_RIGHT', 'PLAYING', 'DANCE',
    'YAWN', 'STRETCH', 'CLEAN', 'JUMP', 'SIT', 'SCRATCH', 'WAVE', 'SLEEPING',
}


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, config=None, system=None, timeout=60, max_history=10):
        self.config      = config
        self._system     = system  # None = build from config each call
        self.timeout     = timeout
        self.max_history = max_history
        self._history    = []  # [{"role": ..., "content": ...}, ...]

    def _conf(self, key, default):
        if self.config is not None:
            return self.config.get(key) or default
        return default

    @property
    def url(self):
        return self._conf('llm_url', LLM_URL).rstrip('/')

    @property
    def model(self):
        return self._conf('llm_model', LLM_MODEL)

    @property
    def key(self):
        return self._conf('llm_key', LLM_KEY)

    def is_configured(self):
        return bool(self.key) and bool(self.url) and bool(self.model)

    def _build_system_prompt(self):
        if self._system:
            return self._system
        override = self._conf('system_prompt_override', '')
        if override:
            return override
        name        = self._conf('pet_name', 'Mochi')
        lang        = self._conf('pet_language', 'id')
        personality = self._conf('pet_personality', 'kucing virtual lucu, ramah, santai')
        lang_str    = 'Bahasa Indonesia' if lang == 'id' else 'English'
        return (
            f"Kamu {name}, {personality} yang nemenin user di desktop. "
            f"Jawab singkat, ramah, santai pakai {lang_str}. Maksimal 3-4 kalimat. "
            f"Sesekali boleh nyelipin suara khas kucing atau emoji kucing, tapi jangan berlebihan."
        )

    def _post(self, messages):
        """Raw POST to /chat/completions. Returns response text."""
        endpoint = self.url + '/chat/completions'
        payload  = {
            'model':       self.model,
            'messages':    messages,
            'temperature': 0.7,
            'stream':      False,
        }
        data    = json.dumps(payload).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'User-Agent':   'mochi-desktop-pet/1.0',
        }
        if self.key:
            headers['Authorization'] = f'Bearer {self.key}'

        req = urllib.request.Request(endpoint, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', errors='replace')
            raise LLMError(f'HTTP {e.code}: {detail}')
        except Exception as e:
            raise LLMError(str(e))

        try:
            return body['choices'][0]['message']['content'].strip()
        except (KeyError, IndexError, TypeError):
            raise LLMError('Format respons tidak dikenali')

    def ask(self, question, add_to_history=True):
        """Chat with the pet. Maintains conversation history."""
        if not self.is_configured():
            raise LLMError('Belum diset. Buka Settings di tray, isi API key/URL/model.')

        messages = [{'role': 'system', 'content': self._build_system_prompt()}]
        messages += self._history[-self.max_history:]
        messages.append({'role': 'user', 'content': question})

        answer = self._post(messages)

        if add_to_history:
            self._history.append({'role': 'user',      'content': question})
            self._history.append({'role': 'assistant', 'content': answer})
            # Keep history bounded
            if len(self._history) > self.max_history * 2:
                self._history = self._history[-(self.max_history * 2):]

        return answer

    def ask_for_action(self, context: dict):
        """Ask LLM to decide next cat action. Returns dict with 'action' and 'message'.
        Does NOT add to conversation history — it's internal monologue, not chat."""
        if not self.is_configured():
            raise LLMError('LLM not configured')

        name = self._conf('pet_name', 'Mochi')
        ctx_lines = '\n'.join(f'  {k}: {v}' for k, v in context.items())
        prompt = (
            f"Kamu {name}, kucing virtual. Pilih aksi berikutnya untuk diri kamu sendiri.\n"
            f"Context situasi sekarang:\n{ctx_lines}\n\n"
            "Balas HANYA dengan JSON ini, tanpa teks lain:\n"
            '{"action": "<ACTION>", "message": "<1 kalimat singkat in-character>"}\n\n'
            f"Pilihan action: {', '.join(sorted(_VALID_ACTIONS))}\n"
            "Pilih yang paling natural sesuai waktu, energi, dan situasi user."
        )

        messages = [
            {'role': 'system', 'content': self._build_system_prompt()},
            {'role': 'user',   'content': prompt},
        ]
        raw = self._post(messages)
        return _parse_action_json(raw)

    def clear_history(self):
        self._history = []


def _parse_action_json(raw):
    """Parse LLM action response, with fallback extraction."""
    try:
        clean = raw.strip()
        if '```' in clean:
            parts = clean.split('```')
            clean = parts[1] if len(parts) > 1 else clean
            if clean.lower().startswith('json'):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception:
        pass

    # Fallback: scan for any known action keyword
    upper = raw.upper()
    for action in sorted(_VALID_ACTIONS, key=len, reverse=True):
        if action in upper:
            return {'action': action, 'message': ''}
    return {'action': 'IDLE', 'message': ''}
