"""Configuration module for Auto_Translate with .env file support."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

# Automatically load variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


@dataclass(frozen=True)
class Config:
    # Server port (Render automatically injects PORT, default 8000 locally)
    PORT: int = int(os.getenv("PORT", "8000"))

    # Default Vietnamese to English base model repository on Hugging Face
    VI_EN_REPO: str = os.getenv("VI_EN_REPO", "dekthedev/opus-mt-vi-en-ct2-int8")

    # Translation parameters
    # Beam size: 1 is greedy search (lowest RAM, fastest on 0.1 CPU), 2-4 gives slight nuance
    BEAM_SIZE: int = int(os.getenv("BEAM_SIZE", "1"))
    DEVICE: str = os.getenv("DEVICE", "cpu")
    COMPUTE_TYPE: str = os.getenv("COMPUTE_TYPE", "int8")

    # Maximum concurrency limit for the API worker pool
    MAX_CONCURRENCY: int = int(os.getenv("MAX_CONCURRENCY", "20"))

    # Memory limit guard (Megabytes)
    MAX_ALLOWED_RAM_MB: float = float(os.getenv("MAX_ALLOWED_RAM_MB", "512.0"))

    # Storage paths
    BASE_DIR: Path = BASE_DIR
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", str(BASE_DIR / "hf_cache")))


# Target language mapping to CT2 models (can be overridden via environment variables if desired)
LANGUAGE_MAP: Dict[str, str] = {
    "en": os.getenv("MODEL_VI_EN", "dekthedev/opus-mt-vi-en-ct2-int8"),
    "english": os.getenv("MODEL_VI_EN", "dekthedev/opus-mt-vi-en-ct2-int8"),
    "fr": os.getenv("MODEL_EN_FR", "michaelfeil/ct2fast-opus-mt-en-fr"),
    "french": os.getenv("MODEL_EN_FR", "michaelfeil/ct2fast-opus-mt-en-fr"),
    "de": os.getenv("MODEL_EN_DE", "michaelfeil/ct2fast-opus-mt-en-de"),
    "german": os.getenv("MODEL_EN_DE", "michaelfeil/ct2fast-opus-mt-en-de"),
    "es": os.getenv("MODEL_EN_ES", "michaelfeil/ct2fast-opus-mt-en-es"),
    "spanish": os.getenv("MODEL_EN_ES", "michaelfeil/ct2fast-opus-mt-en-es"),
    "zh": os.getenv("MODEL_EN_ZH", "gaudi/opus-mt-en-zh-ctranslate2"),
    "chinese": os.getenv("MODEL_EN_ZH", "gaudi/opus-mt-en-zh-ctranslate2"),
    "ja": os.getenv("MODEL_EN_JA", "craftwise/ct2-opus-mt-en-ja-int8"),
    "japanese": os.getenv("MODEL_EN_JA", "craftwise/ct2-opus-mt-en-ja-int8"),
    "ko": os.getenv("MODEL_EN_KO", "ooeoeo/opus-mt-tc-big-en-ko-ct2-float16"),
    "korean": os.getenv("MODEL_EN_KO", "ooeoeo/opus-mt-tc-big-en-ko-ct2-float16"),
    "ru": os.getenv("MODEL_EN_RU", "ooeoeo/opus-mt-en-ru-ct2-float16"),
    "russian": os.getenv("MODEL_EN_RU", "ooeoeo/opus-mt-en-ru-ct2-float16"),
}
