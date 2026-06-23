import os
import json
import urllib.request
import urllib.error

# ── Config (edit here or via environment variables) ────────────────────────────
# Point this at any OpenAI-compatible server (LM Studio, vLLM, llama.cpp server,
# your hermes agent, etc). URL is the base — '/chat/completions' is appended.
LLM_URL   = os.environ.get('MOCHI_LLM_URL',   'https://api.groq.com/openai/v1')
LLM_MODEL = os.environ.get('MOCHI_LLM_MODEL', 'llama-3.3-70b-versatile')
LLM_KEY   = os.environ.get('MOCHI_LLM_KEY',   '')  # set via env var, jangan hardcode!

SYSTEM_PROMPT = (
    "Kamu Mochi, kucing virtual lucu yang nemenin user di desktop. "
    "Jawab singkat, ramah, santai pakai Bahasa Indonesia. Maksimal 3-4 kalimat. "
    "Sesekali boleh nyelipin 'meow' atau emoji kucing, tapi jangan berlebihan."
)


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, config=None, system=None, timeout=60):
        # When a Config is supplied, url/model/key are read live on each call so
        # changes made in the Settings window apply without restarting the app.
        self.config  = config
        self.system  = system or SYSTEM_PROMPT
        self.timeout = timeout

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

    def ask(self, question):
        """Blocking call. Returns answer text or raises LLMError.

        Run this off the Tk main thread (it does network I/O).
        """
        if not self.is_configured():
            raise LLMError('Belum diset. Buka Settings di tray, isi API key/URL/model.')

        endpoint = self.url + '/chat/completions'
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': self.system},
                {'role': 'user',   'content': question},
            ],
            'temperature': 0.7,
            'stream': False,
        }
        data = json.dumps(payload).encode('utf-8')
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
