import subprocess
import os
import sys
from app_config import logger

# 🔍 自動偵測環境（Localhost 或 VPS）
IS_VPS = "ubuntu" in os.uname().nodename.lower()
logger.info(f"🌍 環境偵測: {'VPS' if IS_VPS else 'Localhost'}")

# 🔍 設定 Python 路徑
if IS_VPS:
    VENV_PYTHON = os.path.expanduser("~/ecommerce_analytics_db/venv/bin/python3")
else:
    # 🔥 修正 Localhost 的 Python 位置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3") if sys.platform != "win32" else os.path.join(BASE_DIR, "venv\\Scripts\\python.exe")

if not os.path.exists(VENV_PYTHON):
    logger.error(f"❌ 找不到 Python: {VENV_PYTHON}，請確認 `venv` 是否已建立！")
    sys.exit(1)

# 🛠 定義可執行的任務
TASKS = {
    "data_cleaning": f"{VENV_PYTHON} client_process_raw_data.py"
}

def run_task(task_name):
    """
    根據 task_name 執行對應的 Python 指令
    """
    if task_name in TASKS:
        command = TASKS[task_name]
        logger.info(f"🚀 開始執行任務: {task_name} -> {command}")

        try:
            subprocess.run(command.split(), check=True)
            logger.info(f"✅ 任務 `{task_name}` 執行完成！")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 任務 `{task_name}` 失敗: {e}")

    else:
        logger.warning(f"⚠️ 任務 `{task_name}` 不存在，請確認名稱是否正確。")

if __name__ == "__main__":
    run_task("data_cleaning")