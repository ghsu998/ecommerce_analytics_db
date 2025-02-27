import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy import text  # ✅ 新增這一行，讓 SQLAlchemy 識別 SQL 指令
from tqdm import tqdm  # ✅ 引入進度條

# 讀取 Excel 檔案
file_path = "/Users/gary/Documents/business_Analysis/Data/4seller_order_raw.xlsx"
df = pd.read_excel(file_path)

# 定義 Excel 欄位 → SQL Table 欄位對應 總共57個欄位
column_mapping = {
    "Platform": "OrderPlatform",
    "Shop": "Shop",
    "Platform Order Number": "Platform_Order_Number",
    "Platform Order Status": "Platform_Order_Status",
    "Platform Product ID": "Platform_Product_ID",
    "Platform Variant ID": "Platform_Variant_ID",
    "Shop SKU": "Shop_SKU",
    "Stock SKU": "Stock_SKU",
    "Title": "Title",
    "Variant Name": "Variant_Name",
    "Unit Price": "Unit_Price",
    "Quantity": "Quantity",
    "Sales Link": "Sales_Link",
    "Order Create Time": "Order_Create_Time",
    "Order Paid Time": "Order_Paid_Time",
    "Latest Ship Date": "Latest_Ship_Date",
    "Order Shipped Time": "Order_Shipped_Time",
    "Latest Delivery Date": "Latest_Delivery_Date",
    "Cancel Time": "Cancel_Time",
    "Cancel Reason": "Cancel_Reason",
    "Fulfillment Channel Type": "Fulfillment_Channel_Type",
    "Warehouse": "Warehouse",
    "Ship From": "Ship_From",
    "Tracking No": "Tracking_No",
    "Fulfillment Type And Option": "Fulfillment_Type_And_Option",
    "Shipping Service": "Shipping_Service",
    "Buyer's Name": "Buyers_Name",
    "Recipient Name": "Recipient_Name",
    "Phone": "Phone",
    "Email": "Email",
    "Country": "Country",
    "State Or Region": "State_Or_Region",
    "City": "City",
    "Zip Code": "Zip_Code",
    "Address1": "Address1",
    "Address2": "Address2",
    "Full Address": "Full_Address",
    "Weight Unit": "Weight_Unit",
    "Weight": "Weight",
    "Length Unit": "Length_Unit",
    "Length": "Length",
    "Width": "Width",
    "Height": "Height",
    "Buyer Notes": "Buyer_Notes",
    "Seller Notes": "Seller_Notes",
    "Subtotal": "Subtotal",
    "Total Shipping Fee": "Total_Shipping_Fee",
    "Total Tax": "Total_Tax",
    "Total Discount": "Total_Discount",
    "Order Total": "Order_Total",
    "Currency": "Currency",
    "Platform Marker": "Platform_Marker",
    "URL": "URL",
    "Picture URL": "Picture_URL",
    "Shipment Number": "Shipment_Number",
    "Internal Notes": "Internal_Notes",
    "Logistics Shipping Fee": "Logistics_Shipping_Fee"
}

# 欄位名稱對應
df.rename(columns=column_mapping, inplace=True)
df = df.reindex(columns=column_mapping.values(), fill_value=None)

# ✅ **處理 NaN 值，轉換為 None**
df = df.astype(object).where(pd.notna(df), None)

# ✅ **處理 Shop_SKU，讓 None 變成 'NOSKU'**
df["Shop_SKU"] = df["Shop_SKU"].apply(lambda x: "NOSKU" if x is None else x)

# 設定 MySQL 連接資訊
server = "173.201.189.56"
port = 3306  
database = "ecommerce_analytics_db"
username = "gary"
password = "gaga5288#5288#5288"

# 建立 MySQL 連接字串
engine = create_engine(f"mysql+pymysql://{username}:{password}@{server}:{port}/{database}")

# ✅ **使用 `ON DUPLICATE KEY UPDATE` 確保數據正確**
# ✅ **完整的 SQL 插入語句，涵蓋 57 個欄位**
insert_sql = text("""
    INSERT INTO 4seller_order_raw (
        OrderPlatform, Shop, Platform_Order_Number, Platform_Order_Status, 
        Platform_Product_ID, Platform_Variant_ID, Shop_SKU, Stock_SKU, 
        Title, Variant_Name, Unit_Price, Quantity, Sales_Link, 
        Order_Create_Time, Order_Paid_Time, Latest_Ship_Date, 
        Order_Shipped_Time, Latest_Delivery_Date, Cancel_Time, Cancel_Reason, 
        Fulfillment_Channel_Type, Warehouse, Ship_From, Tracking_No, 
        Fulfillment_Type_And_Option, Shipping_Service, Buyers_Name, 
        Recipient_Name, Phone, Email, Country, State_Or_Region, City, 
        Zip_Code, Address1, Address2, Full_Address, Weight_Unit, Weight, 
        Length_Unit, Length, Width, Height, Buyer_Notes, Seller_Notes, 
        Subtotal, Total_Shipping_Fee, Total_Tax, Total_Discount, Order_Total, 
        Currency, Platform_Marker, URL, Picture_URL, Shipment_Number, 
        Internal_Notes, Logistics_Shipping_Fee
    ) VALUES (
        :OrderPlatform, :Shop, :Platform_Order_Number, :Platform_Order_Status, 
        :Platform_Product_ID, :Platform_Variant_ID, :Shop_SKU, :Stock_SKU, 
        :Title, :Variant_Name, :Unit_Price, :Quantity, :Sales_Link, 
        :Order_Create_Time, :Order_Paid_Time, :Latest_Ship_Date, 
        :Order_Shipped_Time, :Latest_Delivery_Date, :Cancel_Time, :Cancel_Reason, 
        :Fulfillment_Channel_Type, :Warehouse, :Ship_From, :Tracking_No, 
        :Fulfillment_Type_And_Option, :Shipping_Service, :Buyers_Name, 
        :Recipient_Name, :Phone, :Email, :Country, :State_Or_Region, :City, 
        :Zip_Code, :Address1, :Address2, :Full_Address, :Weight_Unit, :Weight, 
        :Length_Unit, :Length, :Width, :Height, :Buyer_Notes, :Seller_Notes, 
        :Subtotal, :Total_Shipping_Fee, :Total_Tax, :Total_Discount, :Order_Total, 
        :Currency, :Platform_Marker, :URL, :Picture_URL, :Shipment_Number, 
        :Internal_Notes, :Logistics_Shipping_Fee
    )
    ON DUPLICATE KEY UPDATE 
        Order_Total = VALUES(Order_Total), 
        Currency = VALUES(Currency), 
        OrderPlatform = VALUES(OrderPlatform), 
        Shop = VALUES(Shop),
        Platform_Order_Status = VALUES(Platform_Order_Status),
        Platform_Product_ID = VALUES(Platform_Product_ID),
        Platform_Variant_ID = VALUES(Platform_Variant_ID),
        Stock_SKU = VALUES(Stock_SKU),
        Title = VALUES(Title),
        Variant_Name = VALUES(Variant_Name),
        Unit_Price = VALUES(Unit_Price),
        Quantity = VALUES(Quantity),
        Sales_Link = VALUES(Sales_Link),
        Order_Paid_Time = VALUES(Order_Paid_Time),
        Latest_Ship_Date = VALUES(Latest_Ship_Date),
        Order_Shipped_Time = VALUES(Order_Shipped_Time),
        Latest_Delivery_Date = VALUES(Latest_Delivery_Date),
        Cancel_Time = VALUES(Cancel_Time),
        Cancel_Reason = VALUES(Cancel_Reason),
        Fulfillment_Channel_Type = VALUES(Fulfillment_Channel_Type),
        Warehouse = VALUES(Warehouse),
        Ship_From = VALUES(Ship_From),
        Tracking_No = VALUES(Tracking_No),
        Fulfillment_Type_And_Option = VALUES(Fulfillment_Type_And_Option),
        Shipping_Service = VALUES(Shipping_Service),
        Buyers_Name = VALUES(Buyers_Name),
        Recipient_Name = VALUES(Recipient_Name),
        Phone = VALUES(Phone),
        Email = VALUES(Email),
        Country = VALUES(Country),
        State_Or_Region = VALUES(State_Or_Region),
        City = VALUES(City),
        Zip_Code = VALUES(Zip_Code),
        Address1 = VALUES(Address1),
        Address2 = VALUES(Address2),
        Full_Address = VALUES(Full_Address),
        Weight_Unit = VALUES(Weight_Unit),
        Weight = VALUES(Weight),
        Length_Unit = VALUES(Length_Unit),
        Length = VALUES(Length),
        Width = VALUES(Width),
        Height = VALUES(Height),
        Buyer_Notes = VALUES(Buyer_Notes),
        Seller_Notes = VALUES(Seller_Notes),
        Subtotal = VALUES(Subtotal),
        Total_Shipping_Fee = VALUES(Total_Shipping_Fee),
        Total_Tax = VALUES(Total_Tax),
        Total_Discount = VALUES(Total_Discount),
        Platform_Marker = VALUES(Platform_Marker),
        URL = VALUES(URL),
        Picture_URL = VALUES(Picture_URL),
        Shipment_Number = VALUES(Shipment_Number),
        Internal_Notes = VALUES(Internal_Notes),
        Logistics_Shipping_Fee = VALUES(Logistics_Shipping_Fee);
""")


# ✅ **確保每筆數據寫入後都會 `commit()`**
with engine.connect() as conn:
    transaction = conn.begin()  # ✅ 開啟事務
    for _, row in tqdm(df.iterrows(), total=len(df), desc="📤 上傳中", unit=" row"):
        conn.execute(insert_sql, row.to_dict())
    transaction.commit()  # ✅ 提交事務




print("✅ 數據成功上傳到 MySQL！")
