import os
import json
from datetime import datetime

SUPPORTED_TEXT = (".py", ".json", ".txt", ".csv", ".md")
SUPPORTED_BINARY = (".xlsx", ".html", ".pdf")
EXCLUDE_DIRS = {"venv", ".git", "__pycache__", ".idea", ".vscode", "node_modules"}

project_file_map = {}

def is_text_file(filename):
    return filename.endswith(SUPPORTED_TEXT)

def is_binary_file(filename):
    return filename.endswith(SUPPORTED_BINARY)

def log_scan(message):
    os.makedirs("logs", exist_ok=True)
    with open("logs/project_loader.log", "a", encoding="utf-8") as f:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def list_project_files(root_dir="."):
    log_scan("🔍 Starting project file scan...")
    project_file_map.clear()
    excluded_count = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            full_path = os.path.abspath(os.path.join(root, file))
            if any(part in EXCLUDE_DIRS for part in full_path.split(os.sep)):
                excluded_count += 1
                continue
            project_file_map[full_path] = {
                "rel_path": os.path.relpath(full_path, root_dir),
                "size_kb": round(os.path.getsize(full_path) / 1024, 2),
                "ext": os.path.splitext(file)[1],
            }
    log_scan(f"✅ Indexed {len(project_file_map)} files, excluded {excluded_count} files.")
    return project_file_map

def load_text_files(root_dir="."):
    content_map = {}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
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
    index = list_project_files()
    contents = load_text_files()
    log_scan(f"📦 Loaded {len(contents)} text files.")
    return {
        "indexed": len(index),
        "loaded": len(contents),
        "sample": list(contents.keys())[:5]
    }