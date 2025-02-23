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

@app.before_request
def redirect_https():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return jsonify({"error": "HTTPS only"}), 403


# 🔹 讀取 GitHub 設定
try:
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    print(f"✅ `config.json` 讀取成功！路徑: {CONFIG_PATH}")
except Exception as e:
    print(f"❌ 無法讀取 `config.json`，錯誤: {e}")
    exit(1)

# 讀取新增的 repo_path 和 script_path
GITHUB_TOKEN = config.get("github_token")
GITHUB_REPO = config.get("github_repo")
REPO_PATH = config.get("repo_path")
SCRIPT_PATH = config.get("script_path")

# 你可以將 REPO_PATH 和 SCRIPT_PATH 用於 webhook 路徑等位置



@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 只允許 GitHub Push 事件
        if request.headers.get("X-GitHub-Event") == "push":
            repo_path = "/home/ubuntu/ecommerce_analytics_db"  # ❗改成你的 Flask 目錄
            script_path = "/home/ubuntu/ecommerce_analytics_db/vps_github_api.py"  # ❗改成你的 Flask 主程式名稱

            # 拉取最新代碼
            subprocess.run(["git", "-C", repo_path, "pull"], check=True)

            # 停止舊的 Flask 進程（如果有）
            subprocess.run(["pkill", "-f", "vps_github_api.py"])

            # 重新啟動 Flask API，並使用 nohup 讓它在背景運行
            subprocess.run(f"nohup python3 {script_path} > /dev/null 2>&1 &", shell=True)

            return jsonify({"message": "Flask API 更新完成（使用 nohup 運行）"}), 200
        else:
            return jsonify({"message": "不是 push 事件"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"message": "Flask API is running! Use /get_code?file=filename to get GitHub files."})


# 🔹 取得 GitHub 內的檔案內容
@app.route('/get_code', methods=['GET'])
def get_code():
    file_path = request.args.get("file")  # 取得 API 請求的檔案名稱
    if not file_path:
        return jsonify({"error": "請提供 file 參數"}), 400
    
    github_owner = config["github_owner"]
    github_repo = config["github_repo"]
    
    # ✅ 檢查 GitHub API URL
    github_api_url = f"https://api.github.com/repos/{github_owner}/{github_repo}/contents/{file_path}"
    print(f"GitHub API URL: {github_api_url}")  # 🛠 Debug: 檢查 API URL
    
    headers = {"Authorization": f"token {config['github_token']}"}
    
    # ✅ 請求 GitHub API 取得檔案內容
    response = requests.get(github_api_url, headers=headers)
    print(f"GitHub API Response Status: {response.status_code}")  # 🛠 Debug: 檢查 API 回應狀態碼
    print(f"GitHub API Response JSON: {response.json()}")  # 🛠 Debug: 檢查 API 回應內容
    
    if response.status_code == 200:
        content = response.json().get("content", "")
        decoded_content = base64.b64decode(content).decode('utf-8')  # 解碼 Base64
        return jsonify({"file": file_path, "content": decoded_content})
    else:
        return jsonify({"error": "無法讀取 GitHub 檔案", "details": response.json()}), response.status_code


@app.route('/list_files', methods=['GET'])
def list_files():
    repo_owner = config.get("github_owner")
    repo_name = config.get("github_repo")

    if not repo_owner or not repo_name:
        return jsonify({"error": "GitHub owner or repo name not configured"}), 400

    github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(github_api_url, headers=headers)

    if response.status_code == 200:
        file_list = [item['path'] for item in response.json()]
        return jsonify({"files": file_list}), 200
    else:
        return jsonify({"error": "Unable to fetch file list", "details": response.json()}), response.status_code


# 🔹 啟動 Flask 服務
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    print("🚀 Webhook 測試成功！")

