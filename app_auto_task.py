import subprocess
from app_config import logger


# 定義要執行的任務
TASKS = {
    "data_cleaning": "python client_process_raw_data.py"
}

def run_task(task_name):
    """
    根據 task_name 執行對應的 Python 指令
    """
    if task_name in TASKS:
        command = TASKS[task_name]
        logger.info(f"🚀 開始執行任務: {task_name} -> {command}")

        try:
            subprocess.run(command, shell=True, check=True)
            logger.info(f"✅ 任務 `{task_name}` 執行完成！")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 任務 `{task_name}` 失敗: {e}")

    else:
        logger.warning(f"⚠️ 任務 `{task_name}` 不存在，請確認名稱是否正確。")

if __name__ == "__main__":
    run_task("data_cleaning")