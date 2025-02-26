import mysql.connector
import json

# 讀取 config.json 檔案
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def get_db_connection():
    return mysql.connector.connect(
        host=config["server"],
        port=config["port"],
        user=config["username"],
        password=config["password"],
        database=config["database"]
    )
