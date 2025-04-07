import os
from openpyxl import Workbook

def generate_datacenter_filename(client_name: str) -> str:
    prefix = client_name.strip().split()[0]
    return f"{prefix}_DataCenter.xlsx"

def ensure_datacenter_file_exists(client_id: str, client_name: str, storage_type: str) -> None:
    """
    根據客戶 ID 與儲存來源，在對應雲端位置自動建立 DataCenter.xlsx（若尚未存在）
    """
    filename = generate_datacenter_filename(client_name)

    # 根據儲存來源決定儲存路徑
    base_dir = "/onedrive/clients/" if storage_type == "onedrive" else "/gdrive/clients/"
    file_path = os.path.join(base_dir, client_id, filename)

    # ✅ 自動建立資料夾
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # ✅ 若尚未存在就建立
    if not os.path.exists(file_path):
        wb = Workbook()
        wb.active.title = "Data_Inventory_Clean"
        wb.create_sheet("Data_Sales_Clean")
        wb.save(file_path)
        print(f"[Tyro] ✅ 建立 DataCenter: {file_path}")
    else:
        print(f"[Tyro] ⏩ 已存在 DataCenter: {file_path}")