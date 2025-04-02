import requests
import json

# ✅ 從 app_config.json 載入多身份 GitHub 設定
with open("app_config.json", "r") as f:
    config = json.load(f)
GITHUB_CONFIG = config["github"]

# ✅ 動態獲取身份配置
def get_github_headers(identity: str = "main"):
    account = GITHUB_CONFIG.get(identity)
    if not account:
        raise ValueError(f"GitHub identity '{identity}' not found in config.")
    return {
        "Authorization": f"Bearer {account['token']}",
        "Accept": "application/vnd.github+json"
    }, account

# ✅ 查詢最新 commit

def get_latest_commit(identity: str = "main"):
    headers, account = get_github_headers(identity)
    url = f"https://api.github.com/repos/{account['owner']}/{account['repo']}/commits/main"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {
            "error": f"Failed to fetch commit (status {res.status_code})",
            "detail": res.text
        }

    data = res.json()
    return {
        "sha": data["sha"],
        "author": data["commit"]["author"]["name"],
        "date": data["commit"]["author"]["date"],
        "message": data["commit"]["message"],
        "url": data["html_url"]
    }
