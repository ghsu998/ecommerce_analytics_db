import os
import json

# 定義支援的檔案類型
SUPPORTED_TEXT = (".py", ".json", ".txt", ".csv", ".md")
SUPPORTED_BINARY = (".xlsx", ".html", ".pdf")

project_file_map = {}

def is_text_file(filename):
    return filename.endswith(SUPPORTED_TEXT)

def is_binary_file(filename):
    return filename.endswith(SUPPORTED_BINARY)

def list_project_files(root_dir="."):
    """
    建立專案內所有檔案的絕對路徑索引
    """
    print("🔍 Indexing project files...")
    project_file_map.clear()
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            full_path = os.path.abspath(os.path.join(root, file))
            project_file_map[full_path] = {
                "rel_path": os.path.relpath(full_path, root_dir),
                "size_kb": round(os.path.getsize(full_path) / 1024, 2),
                "ext": os.path.splitext(file)[1],
            }
    return project_file_map

def load_text_files(root_dir="."):
    """
    載入所有 text 型檔案（py/json/txt/md/csv）
    """
    content_map = {}
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if is_text_file(file):
                full_path = os.path.abspath(os.path.join(root, file))
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content_map[full_path] = f.read()
                except Exception as e:
                    content_map[full_path] = f"⚠️ Failed to read: {str(e)}"
    return content_map

def sync_project():
    """
    同步主目錄內所有檔案（可即時刷新）
    """
    index = list_project_files()
    contents = load_text_files()
    return {
        "indexed": len(index),
        "loaded": len(contents),
        "sample": list(contents.keys())[:5]
    }
