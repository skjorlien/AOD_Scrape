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


# Token expires 8/9/2025
ED_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InNjb3R0a2pvcmxpZW4iLCJleHAiOjE3NTQ3NjM5MjYsImlhdCI6MTc0OTU3OTkyNiwiaXNzIjoiaHR0cHM6Ly91cnMuZWFydGhkYXRhLm5hc2EuZ292IiwiaWRlbnRpdHlfcHJvdmlkZXIiOiJlZGxfb3BzIiwiYWNyIjoiZWRsIiwiYXNzdXJhbmNlX2xldmVsIjozfQ.PuwjQQr7M6vwYvXE2pxXd-jkNxLbaIrMfeKFn66iHgr29BzG8hIPfu8x7XojUsY7L2SK24KeqjRy5cDkaXG_fkqojh6OlGTJ716f4ce7tV9cYZCyhfgO7LUUylvLuL4zqcz_O11DZac7Lx5gNfXJP9I2EPD4SAL6_pSM8nIgKVYCbqZt2dKBhPOhZEgA48ejFlxJ9gFy5bz342EQ-S_dgjJJ4PoRfQgWs6dUl1QQvn_-DHm89Hw3M29Lf1WeiioV_xEw4GKsluRrx2xCFD_6Yx5J4jCs_vcfnLTvWlltY37y4duuB20zTMYRXegEXYN-L48gbouwOmjp8a00f5e45g"
