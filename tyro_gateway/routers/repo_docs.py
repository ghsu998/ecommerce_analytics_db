# tyro_gateway/routers/repo_docs.py

from fastapi import APIRouter, Query
from utils import repo_reader
# 已整合進 repo_reader.py
# from utils.repo_docgen_utils import generate_dependency_graph, generate_module_doc

router = APIRouter()

@router.get("/api/repo/tree")
def get_repo_tree():
    """📂 列出整個 GitHub Repo 的目錄結構（含所有 .py 檔）"""
    try:
        tree = repo_reader.list_repo_tree()
        return {"total": len(tree), "files": tree}
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/repo/file")
def get_repo_file(path: str = Query(..., description="要讀取的 GitHub 檔案路徑 eg. tyro_gateway/main.py")):
    """📄 讀取特定檔案內容（自 GitHub repo）"""
    try:
        content = repo_reader.get_file_content(path)
        return {"path": path, "content": content}
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/repo/search")
def search_repo(keyword: str = Query(..., description="關鍵字搜尋 repo 所有 .py 檔案")):
    """🔍 搜尋整個 repo（只搜尋 .py）是否有包含關鍵字的檔案"""
    try:
        matches = repo_reader.search_in_repo(keyword)
        return {"keyword": keyword, "matches": matches, "total": len(matches)}
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/repo/dependencies")
def get_repo_dependencies():
    """🧩 回傳整個 repo 的 Python 檔案 import 依賴結構"""
    try:
        graph = repo_reader.generate_dependency_graph()
        return {"total_modules": len(graph), "dependency_graph": graph}
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/repo/docgen")
def get_module_doc(path: str = Query(..., description="指定 .py 檔案路徑產出摘要 doc")):
    """🧠 自動產出指定模組的 Markdown 摘要"""
    try:
        doc = repo_reader.generate_module_doc(path)
        return {"path": path, "markdown_doc": doc}
    except Exception as e:
        return {"error": str(e)}
