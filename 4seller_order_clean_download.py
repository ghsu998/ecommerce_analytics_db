import pandas as pd
from sqlalchemy import create_engine

# 1️⃣ 設定 MySQL 連接資訊
server = "173.201.189.56"
port = 3306
database = "ecommerce_analytics_db"
username = "gary"
password = "gaga5288#5288#5288"

try:
    # 2️⃣ 使用 SQLAlchemy 建立連線
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{server}:{port}/{database}")
    print("✅ 成功連接 MySQL")

    # 3️⃣ 查詢數據（SQLAlchemy 連線方式）
    query = "SELECT * FROM order_4seller_clean"
    df = pd.read_sql(query, engine)  # ✅ 使用 SQLAlchemy 來執行 SQL 查詢

    # 4️⃣ 存入 Excel
    excel_path = "/Users/gary/Documents/business_Analysis/Data/4seller_order_clean.xlsx"
    df.to_excel(excel_path, index=False)

    print(f"✅ 數據已導出至 {excel_path}")

except Exception as e:
    print(f"❌ MySQL 連接失敗: {e}")

finally:
    # SQLAlchemy 的 engine 會自動管理連線，這裡不用手動關閉
    print("🔌 MySQL 連接已關閉")