"""Process memory telemetry and safety guardrails."""

import os
import psutil
from typing import Optional
from .config import Config


def get_ram_mb() -> float:
    """Return the current resident set size (RSS) memory of this process in Megabytes."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


class MemoryGuard:
    """Context manager and tracker for peak RAM consumption."""

    def __init__(self, limit_mb: float = Config.MAX_ALLOWED_RAM_MB):
        self.limit_mb = limit_mb
        self.start_ram: float = 0.0
        self.peak_ram: float = 0.0

    def __enter__(self):
        self.start_ram = get_ram_mb()
        self.peak_ram = self.start_ram
        return self

    def sample(self) -> float:
        """Sample current memory and update peak."""
        current = get_ram_mb()
        if current > self.peak_ram:
            self.peak_ram = current
        if self.peak_ram > self.limit_mb:
            raise MemoryError(
                f"RAM Limit Exceeded! Current Peak: {self.peak_ram:.1f} MB > Limit: {self.limit_mb} MB"
            )
        return current

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sample()
