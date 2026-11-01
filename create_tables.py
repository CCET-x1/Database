import os
import psycopg2
from dotenv import load_dotenv

# 載入 .env 檔案中的資料庫連線密碼
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_tables():
    # 定義 SQL 語法：建立 tracks 資料表與 B-Tree 索引
    # 定義 SQL 語法：先刪除舊表，再建立新表與索引
    commands = (
        """
        DROP TABLE IF EXISTS tracks CASCADE;
        CREATE TABLE tracks (
            track_id VARCHAR(50) PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            lyrics TEXT,
            energy FLOAT,
            valence FLOAT,
            tempo FLOAT,
            danceability FLOAT,
            preview_url TEXT
        );
        """,
        """
        -- 建立 B-Tree 複合索引
        CREATE INDEX IF NOT EXISTS idx_vibe ON tracks (energy, valence, tempo);
        """
    )
    
    conn = None
    try:
        # 連線至 Neon 資料庫
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 依序執行 SQL 語法
        for command in commands:
            cur.execute(command)
            
        # 提交異動 (Commit) 讓改變生效
        conn.commit()
        cur.close()
        
        print("✅ Spotify tracks 資料表與 B-Tree 索引建立成功！")
        
    except Exception as error:
        print("❌ 執行失敗，錯誤訊息：")
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
