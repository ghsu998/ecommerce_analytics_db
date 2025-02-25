import json
import subprocess
from flask import Flask, request

app = Flask(__name__)

# 🟢 讀取 config.json
with open("/home/ubuntu/ecommerce_analytics_db/config.json", "r") as f:
    config = json.load(f)

REPO_PATH = config["repo_path"]  # 設置 repo_path

# 🔹 GitHub Webhook: 自動拉取最新代碼
@app.route("/github_webhook", methods=["POST"])
def github_webhook():
    try:
        subprocess.run(["git", "pull"], cwd=REPO_PATH)
        return {"status": "✅ 更新成功"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)