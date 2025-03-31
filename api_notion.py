import requests
from collections import defaultdict

NOTION_TOKEN = "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"
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# 🧩 1. 抓出所有 database 並分類（按前綴模組）
def fetch_all_databases_grouped():
    url = "https://api.notion.com/v1/search"
    payload = {
        "filter": {"value": "database", "property": "object"},
        "page_size": 100
    }

    res = requests.post(url, headers=HEADERS, json=payload)
    if res.status_code != 200:
        print(f"❌ Failed to fetch DB list. Status: {res.status_code}")
        print(res.text)
        return {}

    grouped = defaultdict(dict)
    for db in res.json().get("results", []):
        if not db.get("title"):
            continue
        name = db["title"][0]["text"]["content"]
        db_id = db["id"]

        # 分析前綴，例如 1.2 → module = "1", label = "1.2 Resume ..."
        parts = name.split(" ", 1)
        if "." in parts[0]:
            module_prefix = parts[0].split(".")[0]
            grouped[module_prefix][name] = db_id

    return grouped

# 🧩 2. 抓單個 schema 並顯示
def fetch_schema(database_name, database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    res = requests.get(url, headers=HEADERS)

    print(f"### {database_name}")
    print(f"- **Database ID**: `{database_id}`\n")

    if res.status_code != 200:
        print(f"⚠️ Failed to load schema. Status: {res.status_code}")
        print(f"Response: {res.text}\n")
        return

    properties = res.json().get("properties", {})
    for name, meta in properties.items():
        prop_type = meta.get("type")
        print(f"- **{name}** ({prop_type})")
    print()

# 🧠 3. 主函數：先按模組分群，再印出 schema
# 🧠 3. 主函數：先按模組分群，再印出 schema
def main():
    grouped_dbs = fetch_all_databases_grouped()
    print("# 🧠 TYRO Database Schema (Auto-Fetched)\n")

    module_titles = {
        "1": "🧩 Strategic Output（價值輸出）",
        "2": "🧑‍💼 Personal System（職涯系統）",
        "3": "🛡 Financial Defense（財務防守）",
        "4": "📈 Asset Growth（資產成長）",
        "5": "⚙️ Execution Engine（執行引擎）",
        "6": "🧠 Decision Brain（決策中樞）"
    }

    for module_number in sorted(grouped_dbs.keys(), key=int):
        module_dbs = grouped_dbs[module_number]
        module_title = module_titles.get(module_number, f"📁 Module {module_number}")

        print(f"## {module_title}\n")

        for db_name in sorted(module_dbs.keys()):
            fetch_schema(db_name, module_dbs[db_name])


# ✅ 執行
if __name__ == "__main__":
    main()
