"""Pre-download Hugging Face model weights during the build step.

When run inside Dockerfile or Render build step, the model weights are baked
directly into the deployed image so:
1. Zero downloads at runtime (instant responses).
2. Models survive container sleep and restart cycles permanently.
3. No RAM spikes from downloading while serving requests.
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

