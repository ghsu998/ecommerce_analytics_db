CREATE TABLE IF NOT EXISTS clients_raw_parsed_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(50),
    client_file_name VARCHAR(255),
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
SELECT DISTINCT 
    JSON_UNQUOTE(JSON_EXTRACT(client_raw_data, '$[0]')) AS json_keys
FROM clients_raw_json_table
WHERE client_id = 'client_002'
AND client_file_name = '4seller_inventory_fbm_raw_master.xlsx';

SELECT DISTINCT 
    REPLACE(REPLACE(REPLACE(JSON_UNQUOTE(JSON_EXTRACT(client_raw_data, '$[0]')), ' ', '_'), '-', '_'), '.', '_') AS clean_key
FROM clients_raw_json_table
WHERE client_id = 'client_002'
AND client_file_name = '4seller_inventory_fbm_raw_master.xlsx';

SET SESSION group_concat_max_len = 100000; -- 確保 GROUP_CONCAT 支援長字串

SET @json_keys = (
    SELECT GROUP_CONCAT(DISTINCT
        CONCAT(
            'ADD COLUMN ', 
            REPLACE(REPLACE(REPLACE(JSON_UNQUOTE(JSON_EXTRACT(client_raw_data, '$[0]')), ' ', '_'), '-', '_'), '.', '_'), 
            ' TEXT'
        )
    )
    FROM clients_raw_json_table
    WHERE client_id = 'client_002'
    AND client_file_name = '4seller_inventory_fbm_raw_master.xlsx'
);

SET @alter_sql = CONCAT('ALTER TABLE clients_raw_parsed_table ', @json_keys);
PREPARE stmt FROM @alter_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
