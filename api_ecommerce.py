import json
import subprocess
import os
import requests
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 啟用 CORS，允許跨域請求

# API 首頁
@app.route("/api/")
def home():
    return "Hello, api_ecommerce is running!"

# 服務啟動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
