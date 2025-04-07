# ecommerce_analytics_db/tyro_data_db/raw_writer.py

from .db_connection import get_db_connection
from datetime import datetime
import json

def insert_raw_master_file(client_id, file_type, filename, raw_data, source="manual"):
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ 無法取得資料庫連線")

    batch_id = f"{client_id}_{file_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with conn.cursor() as cursor:
        sql = """
            INSERT INTO client_master_raw_files
            (client_id, upload_batch_id, filename, file_type, raw_data_json, row_count, uploaded_at, source, processed)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, FALSE)
        """
        cursor.execute(sql, (
            client_id,
            batch_id,
            filename,
            file_type,
            json.dumps(raw_data, ensure_ascii=False),
            len(raw_data),
            source
        ))
    conn.commit()
    conn.close()
    return batch_id
