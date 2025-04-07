import os
from openpyxl import Workbook

def generate_datacenter_filename(client_name: str) -> str:
    prefix = client_name.strip().split()[0]
    return f"{prefix}_DataCenter.xlsx"

def ensure_datacenter_file_exists(client_id: str, client_name: str, base_dir: str = "/onedrive/clients/"):
    filename = generate_datacenter_filename(client_name)
    file_path = os.path.join(base_dir, client_id, filename)

    if not os.path.exists(file_path):
        wb = Workbook()
        wb.active.title = "Data_Inventory_Clean"
        wb.create_sheet("Data_Sales_Clean")
        wb.save(file_path)
        print(f"[Tyro] Created new DataCenter file: {file_path}")
    else:
        print(f"[Tyro] DataCenter file already exists: {file_path}")