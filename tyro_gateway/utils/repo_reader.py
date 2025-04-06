import requests
import base64
import ast
from collections import defaultdict
from app_config import get_config_value

# 🔐 定義 GitHub token 的彈性取得方式
def get_github_token(identity="main"):
    return get_config_value(["github", identity, "token"])

GITHUB_REPO = "ghsu998/ecommerce_analytics_db"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = get_github_token("main")  # ✅ 你也可以改成 "bot" 來切換

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",  # ✅ 改為 token 而不是 Bearer
    "Accept": "application/vnd.github.v3+json"
}


def list_repo_tree():
    """列出整個 GitHub Repo 的目錄樹"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/git/trees/{GITHUB_BRANCH}?recursive=1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        tree = response.json().get("tree", [])
        return [item["path"] for item in tree if item["type"] == "blob"]
    else:
        raise Exception(f"❌ 無法讀取 repo tree: {response.status_code} - {response.text}")

def get_file_content(path: str) -> str:
    """讀取特定檔案內容（自 GitHub repo，base64 解碼）"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")
    else:
        raise Exception(f"❌ 無法讀取檔案 {path}: {response.status_code} - {response.text}")

def search_in_repo(keyword: str):
    """搜尋整個 repo 的 .py 檔案是否含有特定關鍵字"""
    matches = []
    for path in list_repo_tree():
        if not path.endswith(".py"):
            continue
        try:
            content = get_file_content(path)
            if keyword in content:
                matches.append(path)
        except Exception as e:
            print(f"⚠️ 無法讀取 {path}: {str(e)}")
    return matches

def parse_imports(file_path: str, content: str):
    """回傳該檔案所 import 的模組"""
    imports = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        print(f"⚠️ 無法解析 {file_path}: {e}")
    return imports

def generate_dependency_graph():
    """產出 repo 所有 Python 模組之間的依賴圖 (import-based)"""
    files = [f for f in list_repo_tree() if f.endswith(".py")]
    graph = defaultdict(list)
    for path in files:
        try:
            content = get_file_content(path)
            imported_modules = parse_imports(path, content)
            for mod in imported_modules:
                graph[path].append(mod)
        except Exception as e:
            print(f"❌ 無法處理 {path}: {e}")
    return dict(graph)

def generate_module_doc(path: str):
    """根據檔案產出 Markdown-style doc string"""
    content = get_file_content(path)
    lines = [f"# `{path}`\n"]
    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        if docstring:
            lines.append(f"\n📘 Module docstring:\n> {docstring}\n")
        lines.append("\n## Functions / Classes\n")
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                lines.append(f"### def {node.name}({', '.join(arg.arg for arg in node.args.args)})")
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    lines.append(f"> {node.body[0].value.s}\n")
            elif isinstance(node, ast.ClassDef):
                lines.append(f"### class {node.name}")
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    lines.append(f"> {node.body[0].value.s}\n")
    except Exception as e:
        lines.append(f"⚠️ 無法分析內容: {e}")
    return "\n".join(lines)
