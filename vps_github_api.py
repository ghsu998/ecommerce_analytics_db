import os
import json
import base64
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔹 設定 config.json 的路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # 取得目前 .py 檔案所在的資料夾
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")  # 設定 config.json 的完整路徑

# 🔹 讀取 GitHub 設定
try:
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    print(f"✅ `config.json` 讀取成功！路徑: {CONFIG_PATH}")
except Exception as e:
    print(f"❌ 無法讀取 `config.json`，錯誤: {e}")
    exit(1)

GITHUB_TOKEN = config.get("github_token")
GITHUB_REPO = config.get("github_repo")

@app.route("/")
def home():
    return jsonify({"message": "Flask API is running! Use /get_code?file=filename to get GitHub files."})

# 🔹 取得 GitHub 內的檔案內容
@app.route("/get_code", methods=["GET"])
def get_code():
    file_path = request.args.get("file")  # 從 API 參數取得檔案名稱
    if not file_path:
        return jsonify({"error": "請提供 file 參數"}), 400

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json().get("content", "").encode('utf-8')
        decoded_content = base64.b64decode(content).decode('utf-8')  # 解碼 Base64
        return jsonify({"file": file_path, "content": decoded_content})
    else:
        return jsonify({"error": "無法讀取 GitHub 檔案", "status": response.status_code}), 400

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 只允許 GitHub Push 事件
        if request.headers.get("X-GitHub-Event") == "push":
            repo_path = "/home/ubuntu/ecommerce_analytics_db"  # ❗改成你的 Flask 目錄

            # 拉取最新代碼
            subprocess.run(["git", "-C", repo_path, "pull"], check=True)

            # 停止舊的 Flask 進程（如果有）
            subprocess.run(["pkill", "-f", "flask"])

            # 重新啟動 Flask API，並使用 nohup 讓它在背景運行
            subprocess.run("nohup python3 /home/youruser/my_flask_project/app.py > /dev/null 2>&1 &", shell=True)

            return jsonify({"message": "Flask API 更新完成（使用 nohup 運行）"}), 200
        else:
            return jsonify({"message": "不是 push 事件"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 啟動 Flask 服務
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
