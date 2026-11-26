"""Keep-Awake Background Service for Render Free-Tier Web Applications.

Render Free-Tier web services spin down (sleep) after 15 minutes of inactivity.
This service periodically sends lightweight HTTP GET ping requests to a target
URL (e.g., every 10 minutes) to keep the target web application awake 24/7.
Zero extra RAM overhead using Python's standard library.
"""

import asyncio
from datetime import datetime, timezone
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from .config import Config


def sync_http_ping(url: str, timeout: float = 30.0) -> Dict[str, Any]:
    """Execute a synchronous HTTP GET request with a custom User-Agent and timeout."""
    t0 = time.perf_counter()
    headers = {
        "User-Agent": "AutoTranslate-KeepAwake/1.0 (+https://render.com)",
        "Accept": "*/*",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency_ms = (time.perf_counter() - t0) * 1000
            status = response.status
            return {
                "url": url,
                "status_code": status,
                "latency_ms": round(latency_ms, 1),
                "awake": True,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        latency_ms = (time.perf_counter() - t0) * 1000
        # Any response code (200, 404, 405, 500) received from the server means
        # the container was woken up and received the request successfully!
        return {
            "url": url,
            "status_code": e.code,
            "latency_ms": round(latency_ms, 1),
            "awake": True,
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - t0) * 1000
        return {
            "url": url,
            "status_code": 0,
            "latency_ms": round(latency_ms, 1),
            "awake": False,
            "error": str(e),
        }


class KeepAwakeService:
    """Manages the periodic pinging of external or internal Render web apps."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.enabled: bool = self.config.KEEP_AWAKE_ENABLED
        self.raw_urls: str = self.config.KEEP_AWAKE_URL
        self.interval_minutes: int = self.config.KEEP_AWAKE_INTERVAL_MINUTES

        self._task: Optional[asyncio.Task] = None
        self.initial_delay: float = 5.0

        # Telemetry metrics
        self.total_pings: int = 0
        self.successful_pings: int = 0
        self.failed_pings: int = 0
        self.last_ping_time: Optional[str] = None
        self.last_results: List[Dict[str, Any]] = []

    def get_target_urls(self) -> List[str]:
        """Parse comma-separated or single target URLs from config."""
        if not self.raw_urls:
            return []
        urls = [u.strip() for u in self.raw_urls.split(",") if u.strip()]
        return [u if u.startswith(("http://", "https://")) else f"https://{u}" for u in urls]

    def ping_all_targets(self) -> List[Dict[str, Any]]:
        """Ping all target URLs synchronously and record metrics."""
        targets = self.get_target_urls()
        if not targets:
            return []

        results = []
        for url in targets:
            result = sync_http_ping(url)
            results.append(result)

            self.total_pings += 1
            if result.get("awake", False):
                self.successful_pings += 1
            else:
                self.failed_pings += 1

            status_str = f"HTTP {result['status_code']}" if result['status_code'] else "FAILED"
            print(
                f"[KeepAwake] Pinged '{url}' | Result: {status_str} | "
                f"Latency: {result['latency_ms']:.1f} ms | Awake: {result['awake']}"
            )

        self.last_ping_time = datetime.now(timezone.utc).isoformat()
        self.last_results = results
        return results

    async def _loop(self):
        """Background loop executing pings every `interval_minutes`."""
        try:
            # Initial grace period: wait before firing first ping
            if self.initial_delay > 0:
                await asyncio.sleep(self.initial_delay)

            while True:
                try:
                    await asyncio.to_thread(self.ping_all_targets)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"[KeepAwake] Unexpected error during ping run: {e}")

                # Sleep until next ping interval (cancellable instantly by stop())
                sleep_seconds = float(self.interval_minutes * 60)
                await asyncio.sleep(sleep_seconds)
        except asyncio.CancelledError:
            pass

    def start(self):
        """Start the background keep-awake worker task if enabled."""
        if not self.enabled:
            print("[KeepAwake] Service disabled (KEEP_AWAKE_ENABLED=false).")
            return

        targets = self.get_target_urls()
        if not targets:
            print("[KeepAwake] Service enabled but no KEEP_AWAKE_URL configured. Idle.")
            return

        if self._task and not self._task.done():
            print("[KeepAwake] Worker already active.")
            return

        self._task = asyncio.create_task(self._loop())
        print(
            f"[KeepAwake] Worker started. Monitoring {len(targets)} target(s) "
            f"every {self.interval_minutes} minute(s)."
        )

    async def stop(self):
        """Gracefully terminate the keep-awake worker task without hanging."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        print("[KeepAwake] Worker stopped cleanly.")

    def is_running(self) -> bool:
        """Check if the background ping worker task is currently active."""
        return self._task is not None and not self._task.done()

    def get_status(self) -> Dict[str, Any]:
        """Return the current runtime status and telemetry."""
        targets = self.get_target_urls()
        return {
            "enabled": self.enabled,
            "is_running": self.is_running(),
            "target_urls": targets,
            "interval_minutes": self.interval_minutes,
            "total_pings": self.total_pings,
            "successful_pings": self.successful_pings,
            "failed_pings": self.failed_pings,
            "last_ping_time": self.last_ping_time,
            "last_results": self.last_results,
        }


# Global singleton instance
_keep_awake_instance: Optional[KeepAwakeService] = None


def get_keep_awake_service(config: Optional[Config] = None) -> KeepAwakeService:
    global _keep_awake_instance
    if _keep_awake_instance is None:
        _keep_awake_instance = KeepAwakeService(config)
    return _keep_awake_instance


def reset_keep_awake_service():
    """Reset singleton for clean testing across event loops."""
    global _keep_awake_instance
    _keep_awake_instance = None
