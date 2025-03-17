USE ecommerce_analytics_db;

-- 1️⃣ **確保 `data_inventory_yesterday_clean` 表格存在**
CREATE TABLE IF NOT EXISTS data_inventory_yesterday_clean (
    InventoryDate DATE NOT NULL,
    SKU VARCHAR(255) NOT NULL,
    Warehouse VARCHAR(255) NOT NULL,
    Physical INT NOT NULL,
    PRIMARY KEY (InventoryDate, SKU, Warehouse)  -- 確保數據不重複
);

-- 2️⃣ **插入清理後的數據**
INSERT INTO data_inventory_yesterday_clean (InventoryDate, SKU, Warehouse, Physical)
SELECT 
    InventoryDate, 
    -- 🔥 **先移除 `-FBA1`，再移除 `-FBA`，確保 SKU 標準化**
    CASE 
        WHEN SKU LIKE '%-FBA1' THEN LEFT(SKU, LENGTH(SKU) - 5)
        WHEN SKU LIKE '%-FBA' THEN LEFT(SKU, LENGTH(SKU) - 4)
        ELSE SKU
    END AS SKU_Cleaned,
    
    Warehouse, 
    Physical
FROM data_inventory_yesterday_raw
WHERE 
    InventoryDate IS NOT NULL 
    AND SKU IS NOT NULL 
    AND Warehouse IS NOT NULL 
    AND TRIM(Warehouse) != ''
    AND Physical IS NOT NULL
ON DUPLICATE KEY UPDATE 
    Physical = VALUES(Physical);  -- 如果 `InventoryDate, SKU, Warehouse` 已經存在，則更新 `Physical`