"""Engine module: Manages CTranslate2 models and SentencePiece tokenizers with automatic HF download."""

import gc
import os
from pathlib import Path
from typing import Dict, Optional
import ctranslate2
import sentencepiece as spm
from huggingface_hub import snapshot_download
from .config import Config
from .memory import get_ram_mb, release_system_memory


class ModelBundle:
    """Encapsulates a CTranslate2 Translator and its SentencePiece tokenizers."""

    def __init__(self, model_dir: str, compute_type: str = "int8", device: str = "cpu"):
        self.model_dir = model_dir
        self.translator: Optional[ctranslate2.Translator] = ctranslate2.Translator(
            model_dir,
            device=device,
            compute_type=compute_type,
            inter_threads=1,
            intra_threads=1,
        )

        source_spm = os.path.join(model_dir, "source.spm")
        target_spm = os.path.join(model_dir, "target.spm")

        self.sp_source: Optional[spm.SentencePieceProcessor] = None
        self.sp_target: Optional[spm.SentencePieceProcessor] = None

        if os.path.exists(source_spm):
            self.sp_source = spm.SentencePieceProcessor()
            self.sp_source.load(source_spm)

        if os.path.exists(target_spm):
            self.sp_target = spm.SentencePieceProcessor()
            self.sp_target.load(target_spm)
        elif self.sp_source is not None:
            # Shared spm model
            self.sp_target = self.sp_source

    def unload(self):
        """Explicitly release model weights from memory and trim system heap."""
        if self.translator is not None:
            try:
                self.translator.unload_model()
            except Exception:
                pass
            self.translator = None
        self.sp_source = None
        self.sp_target = None
        release_system_memory()

    def translate_sentence(self, text: str, beam_size: int = 4) -> str:
        """Tokenize with SentencePiece, translate via CT2, and decode."""
        clean_text = text.strip()
        if not clean_text:
            return ""

        if not self.sp_source or not self.sp_target or not self.translator:
            raise RuntimeError(f"SentencePiece tokenizers or translator missing/unloaded in {self.model_dir}")

        # In Marian models, appending '</s>' ensures proper sentence termination
        tokens = self.sp_source.encode(clean_text, out_type=str) + ["</s>"]
        results = self.translator.translate_batch([tokens], beam_size=beam_size)
        output_tokens = results[0].hypotheses[0]
        return self.sp_target.decode(output_tokens)


_loaded_models: Dict[str, ModelBundle] = {}
_active_pivot_repo: Optional[str] = None


def get_model(repo_id: str, config: Optional[Config] = None) -> ModelBundle:
    """Download (cached) and return a ModelBundle for a given Hugging Face repo ID.

    Maintains max 1 pivot model in memory at a time to strictly enforce < 512 MB RAM.
    """
    global _loaded_models, _active_pivot_repo
    cfg = config or Config()

    # Return cached if already loaded
    if repo_id in _loaded_models and _loaded_models[repo_id].translator is not None:
        return _loaded_models[repo_id]

    # If loading a different pivot model, unload the previous pivot model to conserve RAM
    if repo_id != cfg.VI_EN_REPO and _active_pivot_repo and _active_pivot_repo != repo_id:
        if _active_pivot_repo in _loaded_models:
            old_bundle = _loaded_models.pop(_active_pivot_repo)
            old_bundle.unload()
            del old_bundle
            release_system_memory()

    ram_before = get_ram_mb()

    # Try local cache first to avoid network overhead, fallback to online download
    # max_workers=1 ensures low memory overhead during snapshot download in 512MB RAM containers
    try:
        model_dir = snapshot_download(
            repo_id=repo_id,
            cache_dir=str(cfg.CACHE_DIR) if cfg.CACHE_DIR else None,
            local_files_only=True,
            max_workers=1,
        )
    except Exception:
        model_dir = snapshot_download(
            repo_id=repo_id,
            cache_dir=str(cfg.CACHE_DIR) if cfg.CACHE_DIR else None,
            max_workers=1,
        )

    # Release any buffers accumulated during file downloading/unpacking
    release_system_memory()

    bundle = ModelBundle(
        model_dir=model_dir,
        compute_type=cfg.COMPUTE_TYPE,
        device=cfg.DEVICE,
    )
    _loaded_models[repo_id] = bundle

    if repo_id != cfg.VI_EN_REPO:
        _active_pivot_repo = repo_id

    release_system_memory()
    ram_after = get_ram_mb()
    print(f"[Engine] Loaded '{repo_id}'. RAM: {ram_before:.1f} MB -> {ram_after:.1f} MB (Delta: {ram_after - ram_before:.1f} MB)")

    return bundle
