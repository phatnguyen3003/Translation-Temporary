"""Pre-download Hugging Face model weights during the build step.

When run in Render's 'Build Command' (e.g. `pip install -r requirements.txt && python preload_models.py`),
the model weights are baked directly into the deployed image.
This means:
1. Instant translations (no 10-18s download delay on first request).
2. Zero memory spikes from downloading files while the server is running.
3. Models survive container sleep/wake cycles on the free tier.
"""

import sys
from huggingface_hub import snapshot_download
from src.auto_translate.config import Config, LANGUAGE_MAP

def preload():
    cfg = Config()
    cache_dir = str(cfg.CACHE_DIR)
    
    # Collect all unique Hugging Face repositories to cache
    repos = set()
    repos.add(cfg.VI_EN_REPO)
    for repo in LANGUAGE_MAP.values():
        repos.add(repo)

    print(f"[*] Pre-downloading {len(repos)} translation models into '{cache_dir}'...")
    
    for i, repo in enumerate(sorted(repos), start=1):
        print(f"[{i}/{len(repos)}] Caching '{repo}'...")
        try:
            snapshot_download(
                repo_id=repo,
                cache_dir=cache_dir,
                max_workers=2,
            )
            print(f"    ✓ Successfully cached: {repo}")
        except Exception as e:
            print(f"    ⚠️ Warning caching {repo}: {e}")

    print("\n[*] All models pre-downloaded and baked into build artifact successfully!")

if __name__ == "__main__":
    preload()
