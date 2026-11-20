"""Quality Gate 1: Assert peak memory never breaches 512 MB."""

import pytest
from src.auto_translate.memory import get_ram_mb, MemoryGuard
from src.auto_translate.translator import Translator


def test_peak_memory_beneath_512mb():
    """Verify that process RSS memory stays strictly beneath 512 MB."""
    base_ram = get_ram_mb()
    print(f"\n[Memory Test] Initial base RAM: {base_ram:.1f} MB")
    assert base_ram < 200.0, f"Base RAM too high before loading model: {base_ram:.1f} MB"

    with MemoryGuard(limit_mb=512.0) as guard:
        translator = Translator()
        guard.sample()

        test_sentences = [
            ("Xin chào, bạn khỏe không?", "English"),
            ("Hôm nay thời tiết rất đẹp.", "French"),
            ("Tôi đang học lập trình Python.", "German"),
            ("Cảm ơn bạn rất nhiều.", "Spanish"),
        ]

        for text, lang in test_sentences:
            output = translator.translate(text, lang)
            guard.sample()
            assert len(output) > 0

    peak_ram = guard.peak_ram
    print(f"[Memory Test] Peak RAM: {peak_ram:.1f} MB / Limit: 512.0 MB (Headroom: {512.0 - peak_ram:.1f} MB)")
    assert peak_ram < 512.0, f"FAILED: Memory exceeded 512MB limit! Peak was {peak_ram:.1f} MB"
