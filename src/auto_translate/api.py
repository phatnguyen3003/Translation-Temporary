"""FastAPI REST API for Auto_Translate with CORS and memory telemetry."""

import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .translator import Translator
from .memory import get_ram_mb
from .config import LANGUAGE_MAP
from .keep_awake import get_keep_awake_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to start/stop the keep-awake background pinger."""
    keep_awake = get_keep_awake_service()
    keep_awake.start()
    yield
    await keep_awake.stop()


app = FastAPI(
    title="Auto_Translate API",
    description="Ultra-lightweight Vietnamese-to-Any-Language neural translation service running under 512MB RAM.",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for external callers (web frontends, mobile apps, third-party services)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_memory_middleware(request, call_next):
    """Log real-time RAM usage for every incoming HTTP request."""
    ram_before = get_ram_mb()
    t_start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - t_start) * 1000
    ram_after = get_ram_mb()
    print(
        f"[Live Telemetry] {request.method} {request.url.path} | "
        f"Latency: {duration_ms:.1f} ms | "
        f"RAM: {ram_after:.1f} MB (Δ: {ram_after - ram_before:+.2f} MB)"
    )
    return response

# Lazy-loaded singleton translator
_translator_instance: Translator = None


def get_translator() -> Translator:
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = Translator()
    return _translator_instance


# ------------------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------------------
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Vietnamese text to translate", example="Xin chào, bạn có khỏe không?")
    target: str = Field("English", description="Target language", example="English")


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    target_language: str
    latency_ms: float
    current_ram_mb: float
    ram_limit_mb: float = 512.0


class HealthResponse(BaseModel):
    status: str
    service: str
    current_ram_mb: float
    ram_limit_mb: float = 512.0


class LanguagesResponse(BaseModel):
    supported_languages: List[str]
    count: int


class PingResult(BaseModel):
    url: str
    status_code: int
    latency_ms: float
    awake: bool
    error: Optional[str] = None


class KeepAwakeStatusResponse(BaseModel):
    enabled: bool
    is_running: bool
    target_urls: List[str]
    interval_minutes: int
    total_pings: int
    successful_pings: int
    failed_pings: int
    last_ping_time: Optional[str] = None
    last_results: List[PingResult] = []


class KeepAwakePingResponse(BaseModel):
    message: str
    results: List[PingResult]


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@app.get("/", tags=["General"])
def root():
    """Welcome endpoint with service information and links."""
    return {
        "service": "Auto_Translate API",
        "description": "Vietnamese-to-Any-Language translation service (< 512MB RAM)",
        "docs_url": "/docs",
        "health_check": "/health",
        "languages_url": "/languages",
        "keep_awake_status": "/keep-awake/status",
        "current_ram_mb": round(get_ram_mb(), 1),
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """Health check endpoint for Render to verify service uptime."""
    return HealthResponse(
        status="ok",
        service="auto-translate",
        current_ram_mb=round(get_ram_mb(), 1),
    )


@app.get("/languages", response_model=LanguagesResponse, tags=["Translation"])
def list_languages():
    """List all supported target languages."""
    unique_langs = sorted(set(k.capitalize() for k in LANGUAGE_MAP.keys() if len(k) > 2))
    return LanguagesResponse(
        supported_languages=unique_langs,
        count=len(unique_langs),
    )


@app.post("/translate", response_model=TranslationResponse, tags=["Translation"])
def translate_text(req: TranslationRequest):
    """Translate Vietnamese text to the desired target language."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    translator = get_translator()
    t_start = time.perf_counter()

    try:
        translated = translator.translate(req.text, req.target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

    latency_ms = (time.perf_counter() - t_start) * 1000

    return TranslationResponse(
        original_text=req.text,
        translated_text=translated,
        target_language=req.target,
        latency_ms=round(latency_ms, 1),
        current_ram_mb=round(get_ram_mb(), 1),
    )


# ------------------------------------------------------------------------------
# Keep-Awake Endpoints
# ------------------------------------------------------------------------------
@app.get("/keep-awake/status", response_model=KeepAwakeStatusResponse, tags=["Keep-Awake"])
def keep_awake_status():
    """Retrieve the current status, configuration, and telemetry of the keep-awake service."""
    service = get_keep_awake_service()
    return service.get_status()


@app.post("/keep-awake/ping", response_model=KeepAwakePingResponse, tags=["Keep-Awake"])
def trigger_keep_awake_ping():
    """Manually trigger an immediate keep-awake ping to all configured target URLs."""
    service = get_keep_awake_service()
    results = service.ping_all_targets()
    return KeepAwakePingResponse(
        message=f"Pinged {len(results)} target(s) successfully.",
        results=results,
    )


if __name__ == "__main__":
    import uvicorn
    # Render assigns the port via the PORT environment variable (default 10000 on Render, 8000 locally)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.auto_translate.api:app", host="0.0.0.0", port=port, reload=False)
