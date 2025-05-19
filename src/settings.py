from dataclasses import dataclass
import os

BASE_DIR = "C:/Users/skjor/OneDrive/Documents/Projects/Code/AOD_Scrape"

@dataclass
class Paths:
    raw_data: str = os.path.join(BASE_DIR, 'data', 'raw')
    clean_data: str = os.path.join(BASE_DIR, 'data', 'clean')
    
# Token generated in login of https://urs.earthdata.nasa.gov/
ED_user = "scottkjorlien"
ED_pass = "So@e!6n^TbWRuU"
ED_token = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InNjb3R0a2pvcmxpZW4iLCJleHAiOjE3MzY1MjkxNDMsImlhdCI6MTczMTM0NTE0MywiaXNzIjoiaHR0cHM6Ly91cnMuZWFydGhkYXRhLm5hc2EuZ292In0.FCSnbXLzS3FcWrTNW0mYKZDgexy36q3AfwfV5oE3EHuRTLAD6b9sF-HtIl71Bv5UYBKON2kFDk6zVdM0Oth9btPvrxXp_TJAu_vbWgmknGmMSdXwm-W4y-CFybHvYN4gWFwKFvIfQNAWSaTRJhaZa1QFYS-lCau0ojpBJBGitU9ccGYtSQ9mXDPN55-1_m_dug_1zg1RfvP1ANo68_6pS4iKYL7GjZIxfea33IKygai4mNl35jlUw5ZIcFV6Rtb8kRfsC636_sQRDtMTJoS1smhIIgwW3Ka2upFLU0W91OnSU7AYAAZv6cDWYd5STVY2wpC2LKDsX5YanvgtIJvwNQ"
