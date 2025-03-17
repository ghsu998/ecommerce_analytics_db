import re
import logging
import pandas as pd

def clean_column_names(data):
    """🔹 清理 DataFrame 欄位名稱或單個欄位名稱，確保符合 MySQL 標準"""

    def clean_column(col):
        if not isinstance(col, str):
            return col  # 如果不是字符串，直接返回
        
        col = re.sub(r"[\"']", "", col)  # 移除引號
        col = re.sub(r"[^\w\s]", "_", col)  # 替換非法字符
        col = re.sub(r"\s+", "_", col)  # 替換空格
        col = re.sub(r"__+", "_", col)  # 防止出現 `__`
        col = col.lower().strip("_")
        if col and col[0].isdigit():  # ✅ 避免數字開頭的問題
            col = f"col_{col}"
        return col
    

    if isinstance(data, pd.DataFrame):
        original_columns = data.columns.tolist()
        data.columns = [clean_column(col) for col in data.columns]
        logging.info(f"🛠️ 清理欄位名稱: \n🔹 **Before:** {original_columns} \n🔹 **After:** {data.columns.tolist()}")
        # 🔥 格式化 db_start_date & db_end_date
        data = format_date_columns(data)
        return data
        logging.info(f"🔍 清理後的欄位: {df.columns.tolist()}")
    elif isinstance(data, list):
        return [clean_column(col) for col in data]  # 清理列表中的欄位名稱
    
    elif isinstance(data, str):
        return clean_column(data)  # 如果是單個欄位名稱，直接清理後返回
    
    else:
        logging.warning(f"⚠️ clean_column_names 收到未預期的類型: {type(data)}, 跳過清理")
        return data  # 直接返回原始值，以防止錯誤
    

def format_date_columns(df):
    """🔹 統一 db_start_date 和 db_end_date 為 YYYY-MM-DD"""
    date_columns = ["db_start_date", "db_end_date"]

    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("_", "-")  # 轉換格式
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")  # 確保為日期格式
            logging.info(f"📅 已格式化 `{col}` 欄位為 `YYYY-MM-DD`")

    return df