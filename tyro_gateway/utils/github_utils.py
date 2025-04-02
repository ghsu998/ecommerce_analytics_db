# tyro_gateway/utils/github_utils.py

from fastapi import APIRouter, Query
from tyro_gateway.utils import github_client

router = APIRouter()

@router.get("/api/github/latest_commit")
def get_latest_commit_info(identity: str = Query(default="main", description="GitHub 身份名稱")):
    """
    ✅ 查詢 GitHub main 分支最新 commit 資訊
    支援 identity 切換，例如：main、bot
    """
    return github_client.get_latest_commit(identity)
