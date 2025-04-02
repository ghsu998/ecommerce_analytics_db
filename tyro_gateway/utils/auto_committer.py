
# tyro_gateway/utils/auto_committer.py

import subprocess
from datetime import datetime

def auto_commit_and_push(file_paths: list[str], commit_prefix="🔧 Auto Update"):
    try:
        # 確保 git status 是乾淨的（可省略視需求）
        subprocess.run(["git", "add"] + file_paths, check=True)
        
        # 自動產生訊息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{commit_prefix} @ {timestamp}"
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        return {
            "status": "✅ Commit & pushed",
            "files": file_paths,
            "message": message
        }

    except subprocess.CalledProcessError as e:
        return {
            "status": "❌ Error",
            "detail": str(e)
        }
