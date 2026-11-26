"""Unit tests for KeepAwakeService and keep-awake API endpoints."""

import asyncio
import io
import urllib.error
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from src.auto_translate.api import (
    app,
    root,
    keep_awake_status,
    trigger_keep_awake_ping,
    KeepAwakePingRequest,
)
from src.auto_translate.config import Config
from src.auto_translate.keep_awake import (
    KeepAwakeService,
    sync_http_ping,
    reset_keep_awake_service,
)


def test_url_parsing_and_normalization():
    """Verify single and multiple comma-separated URLs with automatic https prefixing."""
    cfg = Config()
    svc = KeepAwakeService(cfg)
    
    # Test empty
    svc.raw_urls = ""
    assert svc.get_target_urls() == []

    # Test single URL without https
    svc.raw_urls = "my-web-app.onrender.com"
    assert svc.get_target_urls() == ["https://my-web-app.onrender.com"]

    # Test multiple URLs with whitespace and mixed schemes
    svc.raw_urls = "https://app1.onrender.com/health ,  app2.onrender.com, http://app3.org "
    assert svc.get_target_urls() == [
        "https://app1.onrender.com/health",
        "https://app2.onrender.com",
        "http://app3.org",
    ]


def test_sync_http_ping_success():
    """Verify successful ping with 200 OK response."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = sync_http_ping("https://test-service.onrender.com/health")
        assert res["url"] == "https://test-service.onrender.com/health"
        assert res["status_code"] == 200
        assert res["awake"] is True
        assert res["error"] is None
        assert res["latency_ms"] >= 0.0


def test_sync_http_ping_http_error_still_wakes():
    """Verify HTTPError (e.g. 404 or 503) still registers as 'awake' because the container responded."""
    http_err = urllib.error.HTTPError(
        url="https://test.onrender.com",
        code=404,
        msg="Not Found",
        hdrs={},
        fp=io.BytesIO(b"Not Found"),
    )

    with patch("urllib.request.urlopen", side_effect=http_err):
        res = sync_http_ping("https://test.onrender.com")
        assert res["status_code"] == 404
        assert res["awake"] is True
        assert "HTTP 404" in res["error"]


def test_sync_http_ping_network_failure():
    """Verify network connection timeout or DNS error registers as not awake without raising."""
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        res = sync_http_ping("https://down.onrender.com")
        assert res["status_code"] == 0
        assert res["awake"] is False
        assert "Connection refused" in res["error"]


def test_keep_awake_service_telemetry():
    """Verify state transitions and telemetry tracking."""
    reset_keep_awake_service()
    cfg = Config()
    svc = KeepAwakeService(cfg)
    svc.enabled = True
    svc.raw_urls = "https://app1.onrender.com"
    svc.interval_minutes = 10

    # Test initial status
    status = svc.get_status()
    assert status["enabled"] is True
    assert status["interval_minutes"] == 10
    assert status["target_urls"] == ["https://app1.onrender.com"]
    assert status["is_running"] is False
    assert status["total_pings"] == 0

    # Test is_running state transitions
    mock_task = MagicMock()
    mock_task.done.return_value = False
    svc._task = mock_task
    assert svc.is_running() is True
    mock_task.done.return_value = True
    assert svc.is_running() is False


def test_keep_awake_api_endpoints():
    """Verify root, /keep-awake/status, and /keep-awake/ping FastAPI endpoints."""
    reset_keep_awake_service()

    # Check root includes keep_awake_status link
    root_data = root()
    assert "keep_awake_status" in root_data

    # Check status endpoint
    status_data = keep_awake_status()
    assert "enabled" in status_data
    assert "target_urls" in status_data
    assert "interval_minutes" in status_data

    # Check ping endpoint when idle
    ping_resp = trigger_keep_awake_ping()
    assert "results" in ping_resp.model_dump()
    assert ping_resp.results == []

    # Check ping endpoint with custom URL
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        custom_req = KeepAwakePingRequest(url="https://external-service.onrender.com/health")
        custom_ping_resp = trigger_keep_awake_ping(custom_req)
        assert len(custom_ping_resp.results) == 1
        assert custom_ping_resp.results[0].url == "https://external-service.onrender.com/health"
        assert custom_ping_resp.results[0].awake is True
