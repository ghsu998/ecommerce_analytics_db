import re
import logging
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.styles.stylesheet")

def clean_column_names(data):
    """
    🔹 清理欄位名稱（DataFrame、list 或單個欄位），統一為符合 MySQL 的格式：
    - 移除特殊符號
    - 轉為小寫、底線命名
    - 防止欄位以數字開頭
    - 若為 DataFrame，附加處理日期欄位格式
    """
    def clean_column(col):
        if not isinstance(col, str):
            return col  # 非字串則跳過

        col = re.sub(r'["\']', '', col)           # 移除引號
        col = re.sub(r'[^\w\s]', '_', col)         # 替換非法符號為底線
        col = re.sub(r'\s+', '_', col)              # 空白轉底線
        col = re.sub(r'__+', '_', col)               # 多重底線簡化
        col = col.lower().strip('_')
        if col and col[0].isdigit():
            col = f"col_{col}"
        return col

    if isinstance(data, pd.DataFrame):
        original_columns = data.columns.tolist()
        data.columns = [clean_column(col) for col in data.columns]
        logging.info(f"🛠️ 清理欄位名稱: \n🔹 **Before:** {original_columns} \n🔹 **After:** {data.columns.tolist()}")
        data = format_date_columns(data)
        return data

    elif isinstance(data, list):
        return [clean_column(col) for col in data]

    elif isinstance(data, str):
        return clean_column(data)

    else:
        logging.warning(f"⚠️ clean_column_names 收到未預期的類型: {type(data)}, 跳過清理")
        return data

def format_date_columns(df):
    """
    🔹 統一格式化欄位 db_start_date 和 db_end_date 為 YYYY-MM-DD
    """
    date_columns = ["db_start_date", "db_end_date"]

    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("_", "-")
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
            logging.info(f"📅 已格式化 `{col}` 欄位為 `YYYY-MM-DD`")

    return df



def main():
    """模組內部測試"""
    sample_df = pd.DataFrame({
        'DB Start Date': ['2024_01_01', '2024_02_01'],
        'Some Column!': [1, 2],
        '123 Wrong Start': ["a", "b"]
    })
    cleaned = clean_column_names(sample_df)
    print("\n🧪 測試結果:")
    print(cleaned.head())

if __name__ == "__main__":
    main()
