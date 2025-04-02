import os
import json
import pandas as pd

SUPPORTED_TEXT = (".py", ".json", ".txt", ".csv", ".md")
SUPPORTED_BINARY = (".xlsx", ".html", ".xml")  # can extend as needed


def is_text_file(filename):
    return filename.endswith(SUPPORTED_TEXT)

def is_binary_file(filename):
    return filename.endswith(SUPPORTED_BINARY)

def list_project_files(root_dir="."):
    print("\n📁 Project File Index:\n")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, root_dir)
            print(f"- {rel_path}")

def load_text_files(root_dir="."):
    content_map = {}
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if is_text_file(file):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content_map[full_path] = f.read()
                except Exception as e:
                    content_map[full_path] = f"[⚠️ Failed to read: {str(e)}]"
    return content_map

def load_csv_or_excel(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            return None
        return df.head().to_dict()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    list_project_files("../")  # Replace with actual project root

    # Load text files
    content = load_text_files("../")
    print("\n✅ Loaded .py/.json/.txt files:")
    for k in list(content.keys())[:5]:
        print(f"- {k} ({len(content[k])} chars)")

    # Example: Load Excel if needed
    # excel_preview = load_csv_or_excel("../data/sample.xlsx")
    # print(json.dumps(excel_preview, indent=2))
