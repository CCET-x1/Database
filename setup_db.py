import os
import psycopg2
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數取得資料庫連線字串
DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    try:
        # 嘗試連線至資料庫
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 執行簡單的 SQL 查詢來驗證版本
        cur.execute("SELECT version();")
        db_version = cur.fetchone()

        print("✅ 連線成功！")
        print("資料庫版本:", db_version[0])

        # 關閉連線
        cur.close()
        conn.close()

    except Exception as e:
        print("❌ 連線失敗，錯誤訊息：")
        print(e)

if __name__ == "__main__":
    test_connection()
    