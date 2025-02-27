USE ecommerce_analytics_db;

-- 1️⃣ 插入新的數據（確保 clean table 有最新的訂單，並移除 SKU 的 -FBA）
INSERT INTO 4seller_order_clean (
    OrderPlatform, Shop, Platform_Order_Number, Platform_Order_Status, 
    Platform_Variant_ID, Shop_SKU, Quantity, Order_Create_Time, Cancel_Time, 
    Fulfillment_Channel_Type, Recipient_Name, Phone, Email, Country, 
    State_Or_Region, City, Zip_Code, Address1, Address2, Full_Address, 
    Subtotal, Total_Shipping_Fee, Total_Tax, Total_Discount, Order_Total, Currency
)
SELECT 
    r.OrderPlatform, r.Shop, r.Platform_Order_Number, r.Platform_Order_Status, 
    r.Platform_Variant_ID, 
    REPLACE(r.Shop_SKU, '-FBA', '') AS Shop_SKU, -- 🔹 清理 SKU
    r.Quantity, r.Order_Create_Time, r.Cancel_Time, 
    r.Fulfillment_Channel_Type, r.Recipient_Name, r.Phone, r.Email, r.Country, 
    r.State_Or_Region, r.City, r.Zip_Code, r.Address1, r.Address2, r.Full_Address, 
    r.Subtotal, r.Total_Shipping_Fee, r.Total_Tax, r.Total_Discount, r.Order_Total, r.Currency
FROM 4seller_order_raw r
WHERE NOT EXISTS (
    SELECT 1 
    FROM order_4seller_clean c
    WHERE r.Platform_Order_Number = c.Platform_Order_Number
    AND r.Shop_SKU = c.Shop_SKU
    AND r.Order_Create_Time = c.Order_Create_Time
);

-- 2️⃣ 更新訂單狀態 & 數量（確保 clean table 內的訂單狀態、數量最新，並清理 SKU）
UPDATE 4seller_order_clean c
JOIN 4seller_order_raw r
ON c.OrderPlatform = r.OrderPlatform
AND c.Shop = r.Shop
AND c.Platform_Order_Number = r.Platform_Order_Number
AND c.Order_Create_Time = r.Order_Create_Time
SET 
    c.Platform_Order_Status = r.Platform_Order_Status,
    c.Shop_SKU = REPLACE(r.Shop_SKU, '-FBA', ''), -- 🔹 確保更新狀態時也清理 SKU
    c.Quantity = r.Quantity -- 🔹 更新數量，確保數據同步
WHERE c.Platform_Order_Status <> r.Platform_Order_Status
   OR c.Shop_SKU LIKE '%-FBA'
   OR c.Quantity <> r.Quantity; -- 只有需要更新的才執行