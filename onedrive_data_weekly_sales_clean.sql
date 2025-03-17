USE ecommerce_analytics_db;

-- 🟢 檢查並建立 Table
CREATE TABLE IF NOT EXISTS data_weekly_sales_clean (
    SKU VARCHAR(255) NOT NULL,
    QtySold INT NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    PRIMARY KEY (SKU, Start_Date, End_Date)
);

-- 🟢 插入乾淨的數據
INSERT INTO data_weekly_sales_clean (SKU, QtySold, Start_Date, End_Date)
SELECT 
    SKU, 
    QtySold, 
    Start_Date, 
    End_Date
FROM data_weekly_sales_raw r
WHERE NOT EXISTS (
    SELECT 1 FROM data_weekly_sales_clean c
    WHERE c.SKU = r.SKU 
    AND c.Start_Date = r.Start_Date 
    AND c.End_Date = r.End_Date
);