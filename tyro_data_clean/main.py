import os
import sys

# ✅ 加入主目錄 ecommerce_analytics_db 到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tyro_data_clean.tasks.client_process_raw_data import main

if __name__ == "__main__":
    main()