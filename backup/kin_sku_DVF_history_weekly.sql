-- ========================================
--  🔥 DVF 計算流程 - 週期性補貨數據計算
--  主要分為 10 個步驟，確保數據準確性
-- ========================================

-- 1️⃣ 確保 `kin_sku_DVF_history_weekly` 表格存在
DROP TABLE IF EXISTS kin_sku_DVF_history_weekly;

CREATE TABLE IF NOT EXISTS kin_sku_DVF_history_weekly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    SKU VARCHAR(100) NOT NULL,
    Forecast_Date DATE NOT NULL DEFAULT (CURRENT_DATE),
    SKU_Brand VARCHAR(50),
    SKU_Type VARCHAR(50),
    SKU_Lead_Time_Week INT,
    Lookback_Period_Week INT,
    Avg_Weekly_Sales INT,
    Last_5_Weeks_Sales INT,
    FBM_Warehouse INT,
    FBA_Warehouse INT,
    Incoming_QTY INT,
    Standard_Deviation DECIMAL(12,2), 
    Coefficient_of_Variation DECIMAL(12,2), 
    Z_Factor DECIMAL(12,2), 
    Safety_Stock INT, 
    Reorder_Point INT, 
    DVF_Quantity INT, 
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (SKU, Forecast_Date) -- 確保每天每個 SKU 只有一筆數據
);

-- ========================================
--  🔥 1️⃣ 插入 SKU，確保 DVF history 表格有數據
-- ========================================
INSERT INTO kin_sku_DVF_history_weekly (SKU, Forecast_Date, SKU_Brand, SKU_Type)
SELECT 
    s.SKU, 
    CURRENT_DATE, 
    s.SKU_Brand, 
    s.SKU_Type
FROM kin_sku_master s
WHERE s.SKU_Type NOT IN ('Discontinued', 'KIT')
ON DUPLICATE KEY UPDATE Updated_At = CURRENT_TIMESTAMP;

-- ========================================
--  🔥 2️⃣ 設定 Lead Time & Lookback Period
-- ========================================
UPDATE kin_sku_DVF_history_weekly 
SET 
    SKU_Lead_Time_Week = CASE 
        WHEN SKU_Type = 'Seasonal' AND MONTH(CURRENT_DATE) IN (2, 3, 8, 9) THEN 16
        WHEN SKU_Type = 'Seasonal' THEN 12
        ELSE 12
    END,
    Lookback_Period_Week = CASE 
        WHEN SKU_Type = 'Seasonal' THEN 52
        WHEN SKU_Type = 'Not_Seasonal' THEN 26
        ELSE 12
    END;

-- ========================================
--  🔥 3️⃣ 計算 `Avg_Weekly_Sales` (基於 Lookback_Period_Week)
-- ========================================
UPDATE kin_sku_DVF_history_weekly h
LEFT JOIN (
    SELECT 
        d.SKU, 
        ROUND(COALESCE(
            SUM(
                CASE 
                    WHEN d.End_Date >= DATE_SUB(CURDATE(), INTERVAL h.Lookback_Period_Week WEEK) 
                    THEN d.QtySold 
                    ELSE 0 
                END
            ) / NULLIF(h.Lookback_Period_Week, 0), 0), 
        0) AS Avg_Weekly_Sales
    FROM data_weekly_sales_clean d
    LEFT JOIN kin_sku_DVF_history_weekly h ON d.SKU = h.SKU
    GROUP BY d.SKU
) sales ON h.SKU = sales.SKU
SET h.Avg_Weekly_Sales = sales.Avg_Weekly_Sales;

-- ========================================
--  🔥 4️⃣ 計算 `Last_5_Weeks_Sales`
-- ========================================
UPDATE kin_sku_DVF_history_weekly h
LEFT JOIN (
    SELECT 
        d.SKU, 
        ROUND(COALESCE(
            SUM(CASE 
                    WHEN d.End_Date >= DATE_SUB(DATE_SUB(CURDATE(), INTERVAL 1 WEEK), INTERVAL 5 WEEK) 
                    AND d.End_Date IS NOT NULL 
                    THEN d.QtySold 
                    ELSE 0 
                END), 
        0), 
        0) AS Last_5_Weeks_Sales
    FROM data_weekly_sales_clean d
    LEFT JOIN kin_sku_master s ON d.SKU = s.SKU
    WHERE s.SKU_Type NOT IN ('Discontinued', 'KIT')
    GROUP BY d.SKU
) sales ON h.SKU = sales.SKU
SET h.Last_5_Weeks_Sales = sales.Last_5_Weeks_Sales;

-- ========================================
--  🔥 5️⃣ 計算 `FBM_Warehouse` & `FBA_Warehouse`
-- ========================================
UPDATE kin_sku_DVF_history_weekly h
LEFT JOIN (
    SELECT 
        i.SKU, 
        SUM(i.Physical) AS FBM_Warehouse
    FROM data_inventory_yesterday_clean i
    WHERE i.Warehouse NOT LIKE '%FBA%'
    AND i.InventoryDate = (SELECT MAX(InventoryDate) FROM data_inventory_yesterday_clean)
    GROUP BY i.SKU
) fbm_data ON h.SKU = fbm_data.SKU
SET h.FBM_Warehouse = COALESCE(fbm_data.FBM_Warehouse, 0);

UPDATE kin_sku_DVF_history_weekly h
LEFT JOIN (
    SELECT 
        i.SKU, 
        SUM(i.Physical) AS FBA_Warehouse
    FROM data_inventory_yesterday_clean i
    WHERE i.Warehouse LIKE '%FBA%'
    AND i.InventoryDate = (SELECT MAX(InventoryDate) FROM data_inventory_yesterday_clean)
    GROUP BY i.SKU
) fba_data ON h.SKU = fba_data.SKU
SET h.FBA_Warehouse = COALESCE(fba_data.FBA_Warehouse, 0);

-- ========================================
--  🔥 6️⃣ 計算 `Incoming_QTY`
-- ========================================
UPDATE kin_sku_DVF_history_weekly h
LEFT JOIN (
    SELECT 
        p.container_SKU AS SKU, 
        SUM(p.Received_QTY) AS Incoming_QTY
    FROM kin_sku_purchase_master p
    WHERE p.Container_Received_Date IS NULL
    GROUP BY p.container_SKU
) incoming_data ON h.SKU = incoming_data.SKU
SET h.Incoming_QTY = COALESCE(incoming_data.Incoming_QTY, 0);

-- ========================================
--  🔥 7️⃣ 計算 `Standard_Deviation`
-- ========================================
UPDATE kin_sku_DVF_history_weekly h
LEFT JOIN (
    SELECT 
        SKU, 
        CAST(ROUND(COALESCE(STDDEV(QtySold), 0), 2) AS DECIMAL(12,2)) AS Standard_Deviation
    FROM data_weekly_sales_clean
    WHERE QtySold > 0  
    GROUP BY SKU
) sales ON h.SKU = sales.SKU
SET h.Standard_Deviation = COALESCE(sales.Standard_Deviation, 0);

-- ========================================
--  🔥 8️⃣ 計算 `Coefficient_of_Variation`
-- ========================================
UPDATE kin_sku_DVF_history_weekly 
SET Coefficient_of_Variation = 
    CASE 
        WHEN Avg_Weekly_Sales > 0 
        THEN ROUND(Standard_Deviation / NULLIF(Avg_Weekly_Sales, 0), 2)
        ELSE 0
    END;

-- ========================================
--  🔥 9️⃣ 計算 `Z-Factor`
-- ========================================
UPDATE kin_sku_DVF_history_weekly 
SET Z_Factor = 
    CASE 
        WHEN Coefficient_of_Variation <= 0.2 THEN 1.65
        WHEN Coefficient_of_Variation <= 0.5 THEN 2.00
        ELSE 2.33
    END;

-- ========================================
--  🔥 🔟 計算 `Safety Stock`
-- ========================================
UPDATE kin_sku_DVF_history_weekly 
SET Safety_Stock = ROUND(Standard_Deviation * SQRT(NULLIF(SKU_Lead_Time_Week, 0)) * Z_Factor, 0);

-- ========================================
--  🔥 🔟 計算 `Reorder Point`
-- ========================================
UPDATE kin_sku_DVF_history_weekly 
SET Reorder_Point = (Avg_Weekly_Sales * SKU_Lead_Time_Week) + Safety_Stock;

-- ========================================
--  🔥 🔟 計算 `DVF_Quantity`
-- ========================================
UPDATE kin_sku_DVF_history_weekly 
SET DVF_Quantity = GREATEST(
        (Avg_Weekly_Sales * SKU_Lead_Time_Week) + Safety_Stock - (FBM_Warehouse + FBA_Warehouse + Incoming_QTY), 
        0
    );