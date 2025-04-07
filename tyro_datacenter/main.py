# tyro_datacenter/main.py
from app_config import logger
from tyro_data_clean.utils.client_file_mapping_config import get_clients_list
from tyro_datacenter.utils.client_datacenter_mapping_loader import parse_client_datacenter_columns


def main():
    logger.info("\n🚀 開始解析所有客戶的 Datacenter 欄位...")
    clients = get_clients_list()

    for client_id in clients:
        logger.info(f"\n🔍 處理客戶: {client_id}")
        parse_client_datacenter_columns(client_id)

    logger.info("\n✅ Datacenter 欄位自動擷取完成！")


if __name__ == "__main__":
    main()
