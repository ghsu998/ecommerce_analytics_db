import json
import subprocess
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🟢 從環境變量中讀取 GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 🔹 確保 GITHUB_TOKEN 存在
if not GITHUB_TOKEN:
    raise EnvironmentError("GitHub Token is not set in the environment variables.")

# 🟢 讀取 config.json (仍然保持 repo_path 配置)
with open("/home/ubuntu/ecommerce_analytics_db/config.json", "r") as f:
    config = json.load(f)

REPO_PATH = config["repo_path"]  # 設置 repo_path

# 🔹 GitHub Webhook: 自動拉取最新代碼
@app.route("/github_webhook", methods=["POST"])
def github_webhook():
    try:
        # 使用具體的分支名稱，這裡是 main
        result = subprocess.run(
            ["git", "pull", "origin", "main"], cwd=REPO_PATH, check=True, capture_output=True, text=True
        )
        # 返回標準輸出，方便檢查
        return jsonify({"status": "✅ 更新成功", "details": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        # 如果 git 命令失敗，返回錯誤信息
        return jsonify({"error": str(e), "details": e.stderr}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
