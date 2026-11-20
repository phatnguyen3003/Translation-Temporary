"""Auto Translate: Ultra-lightweight Vietnamese-to-Any-Language translator."""

from .config import Config, LANGUAGE_MAP
from .engine import get_model, ModelBundle
from .memory import get_ram_mb, MemoryGuard
from .translator import Translator

__version__ = "0.1.0"
__all__ = ["Config", "LANGUAGE_MAP", "get_model", "ModelBundle", "get_ram_mb", "MemoryGuard", "Translator"]
