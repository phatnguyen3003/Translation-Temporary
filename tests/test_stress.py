"""Quality Gate 3: Memory stability & leak test across sequential requests."""

import pytest
from src.auto_translate.memory import get_ram_mb
from src.auto_translate.translator import Translator


def test_memory_stability_across_requests():
    """Ensure consecutive requests do not cause monotonic memory leaks."""
    translator = Translator()

    # Warm-up request
    translator.translate("Khởi động hệ thống.", "English")
    initial_ram = get_ram_mb()

    # 15 sequential cycles
    for i in range(15):
        translator.translate(f"Đây là câu thử nghiệm số {i+1}.", "English")

    final_ram = get_ram_mb()
    ram_drift = final_ram - initial_ram

    print(f"\n[Stress Test] Initial: {initial_ram:.1f} MB, Final: {final_ram:.1f} MB, Drift: {ram_drift:+.1f} MB")
    assert final_ram < 512.0, f"Final RAM exceeded 512MB: {final_ram:.1f} MB"
    assert ram_drift < 20.0, f"Excessive memory drift detected: {ram_drift:.1f} MB"
