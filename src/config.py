from dataclasses import dataclass
from pathlib import Path


def get_repo_root():
    """Find the nearest parent directory containing a .git folder."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    raise RuntimeError("No .git directory found in any parent folder.")


BASE_DIR = get_repo_root()
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_DATA_DIR = BASE_DIR / "data" / "clean"
CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)


TMP_DIR = BASE_DIR / "data" / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)


import os

ED_TOKEN = os.getenv("ED_TOKEN")

if ED_TOKEN is None:
    raise EnvironmentError("ED_TOKEN not set in the environment")

