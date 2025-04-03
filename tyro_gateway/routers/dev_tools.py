# tyro_gateway/routers/dev_tools.py

from fastapi import APIRouter
from project_loader import list_project_files
import os

router = APIRouter()

@router.get("/api/dev/project_tree")
def get_project_tree():
    """
    📂 產生主目錄樹狀圖（for GPT internal / 開發用）
    """
    root_dir = "."
    tree = {}

    for path, info in list_project_files(root_dir).items():
        parts = info["rel_path"].split(os.sep)
        cursor = tree
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = f"{info['size_kb']} KB"

    def render_tree(node, prefix=""):
        lines = []
        for k, v in sorted(node.items()):
            if isinstance(v, dict):
                lines.append(f"{prefix}📁 {k}/")
                lines += render_tree(v, prefix + "    ")
            else:
                lines.append(f"{prefix}📄 {k} ({v})")
        return lines

    return {
        "project_root": os.path.abspath(root_dir),
        "tree_output": render_tree(tree)
    }