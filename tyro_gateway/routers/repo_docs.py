# tyro_gateway/routers/repo_docs.py

from fastapi import APIRouter, Query, Request
from tyro_gateway.utils import repo_reader
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📂 列出整個 GitHub Repo 的目錄結構（含所有 .py 檔）
@router.get("/api/repo/tree")
def get_repo_tree(request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    tree = repo_reader.list_repo_tree()
    log_api_trigger(
        action_name="List Git Repo Tree",
        endpoint="/api/repo/tree",
        data_summary={"total": len(tree)},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return {"total": len(tree), "files": tree}


# 📄 讀取特定檔案內容（自 GitHub repo）
@router.get("/api/repo/file")
def get_repo_file(
    path: str = Query(..., description="GitHub 檔案路徑"), request: Request = None
):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    content = repo_reader.get_file_content(path)
    log_api_trigger(
        action_name="Get Git File Content",
        endpoint="/api/repo/file",
        data_summary={"path": path},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return {"path": path, "content": content}


# 🔍 搜尋整個 repo 是否有包含關鍵字的 .py 檔案
@router.get("/api/repo/search")
def search_repo(
    keyword: str = Query(..., description="搜尋關鍵字"), request: Request = None
):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    matches = repo_reader.search_in_repo(keyword)
    log_api_trigger(
        action_name="Search Keyword in Git Repo",
        endpoint="/api/repo/search",
        data_summary={"keyword": keyword, "matches": len(matches)},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return {"keyword": keyword, "matches": matches, "total": len(matches)}


# 🧩 回傳整個 repo 的 Python 檔案 import 依賴結構
@router.get("/api/repo/dependencies")
def get_repo_dependencies(request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    graph = repo_reader.generate_dependency_graph()
    log_api_trigger(
        action_name="Generate Dependency Graph",
        endpoint="/api/repo/dependencies",
        data_summary={"total_modules": len(graph)},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return {"total_modules": len(graph), "dependency_graph": graph}


# 🧠 自動產出指定模組的 Markdown 摘要
@router.get("/api/repo/docgen")
def get_module_doc(
    path: str = Query(..., description="指定 .py 檔案路徑"), request: Request = None
):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    doc = repo_reader.generate_module_doc(path)
    log_api_trigger(
        action_name="Generate Doc from Git File",
        endpoint="/api/repo/docgen",
        data_summary={"path": path},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return {"path": path, "markdown_doc": doc}
