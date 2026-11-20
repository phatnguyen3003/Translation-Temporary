"""Translation pipeline for Vietnamese to Any Language using Direct and Pivot translation."""

import threading
from typing import Optional
from .config import Config, LANGUAGE_MAP
from .engine import get_model, ModelBundle


class Translator:
    """Translates text from Vietnamese into English or other languages via English pivot."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._lock = threading.Lock()
        # Pre-load base Vietnamese -> English model
        self.vi_en_model: ModelBundle = get_model(self.config.VI_EN_REPO, self.config)

    def translate(self, text: str, target_lang: str = "English") -> str:
        """Translate Vietnamese text to the target language in a thread-safe manner.

        If target is English, runs directly.
        If target is another language, translates Vietnamese -> English -> Target.
        """
        clean_text = text.strip()
        if not clean_text:
            return ""

        lang_key = target_lang.lower().strip()

        with self._lock:
            # Step 1: Translate Vietnamese to English
            english_text = self.vi_en_model.translate_sentence(
                clean_text, beam_size=self.config.BEAM_SIZE
            )

            if lang_key in ("en", "english"):
                return english_text

            # Step 2: Pivot from English to target language
            target_repo = LANGUAGE_MAP.get(lang_key)
            if not target_repo:
                raise ValueError(
                    f"Unsupported target language '{target_lang}'. "
                    f"Supported languages: {', '.join(sorted(set(LANGUAGE_MAP.keys())))}"
                )

            pivot_model = get_model(target_repo, self.config)
            return pivot_model.translate_sentence(
                english_text, beam_size=self.config.BEAM_SIZE
            )
