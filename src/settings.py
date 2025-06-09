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


ED_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InNjb3R0a2pvcmxpZW4iLCJleHAiOjE3MzY1MjkxNDMsImlhdCI6MTczMTM0NTE0MywiaXNzIjoiaHR0cHM6Ly91cnMuZWFydGhkYXRhLm5hc2EuZ292In0.FCSnbXLzS3FcWrTNW0mYKZDgexy36q3AfwfV5oE3EHuRTLAD6b9sF-HtIl71Bv5UYBKON2kFDk6zVdM0Oth9btPvrxXp_TJAu_vbWgmknGmMSdXwm-W4y-CFybHvYN4gWFwKFvIfQNAWSaTRJhaZa1QFYS-lCau0ojpBJBGitU9ccGYtSQ9mXDPN55-1_m_dug_1zg1RfvP1ANo68_6pS4iKYL7GjZIxfea33IKygai4mNl35jlUw5ZIcFV6Rtb8kRfsC636_sQRDtMTJoS1smhIIgwW3Ka2upFLU0W91OnSU7AYAAZv6cDWYd5STVY2wpC2LKDsX5YanvgtIJvwNQ"

# Token generated in login of https://urs.earthdata.nasa.gov/
ED_user = "scottkjorlien"
ED_pass = "So@e!6n^TbWRuU"
