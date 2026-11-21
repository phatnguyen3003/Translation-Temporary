"""Quality Gate 2: Multi-Language Translation Golden Tests."""

import pytest
from src.auto_translate.translator import Translator


@pytest.fixture(scope="module")
def translator():
    return Translator()


def test_vietnamese_to_english(translator):
    text = "Xin chào bạn, bạn có khỏe không?"
    out = translator.translate(text, "English")
    print(f"\nVI -> EN: {out}")
    assert any(w in out.lower() for w in ["hello", "how are you", "fine"])


def test_vietnamese_to_french(translator):
    text = "Cảm ơn bạn rất nhiều."
    out = translator.translate(text, "French")
    print(f"\nVI -> FR: {out}")
    assert "merci" in out.lower()


def test_vietnamese_to_german(translator):
    text = "Hôm nay thời tiết rất đẹp."
    out = translator.translate(text, "German")
    print(f"\nVI -> DE: {out}")
    assert any(w in out.lower() for w in ["wetter", "schön", "tag"])


def test_vietnamese_to_spanish(translator):
    text = "Chúc một ngày tốt lành."
    out = translator.translate(text, "Spanish")
    print(f"\nVI -> ES: {out}")
    assert any(w in out.lower() for w in ["día", "buen", "tenga"])


def test_vietnamese_to_korean(translator):
    text = "Xin chào, rất vui được gặp bạn."
    out = translator.translate(text, "Korean")
    print(f"\nVI -> KO: {out}")
    # Korean characters reside in the range AC00-D7A3
    assert any('\uac00' <= char <= '\ud7a3' for char in out)


def test_vietnamese_to_russian(translator):
    text = "Xin chào người bạn của tôi."
    out = translator.translate(text, "Russian")
    print(f"\nVI -> RU: {out}")
    # Cyrillic characters reside in the range 0400-04FF
    assert any('\u0400' <= char <= '\u04ff' for char in out)
