import os
import time
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import pandas as pd
import uuid

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_sample_data():
    csv_file = "spotify_data.csv" 
    MAX_RECORDS = 700000
    
    if os.path.exists(csv_file):
        print(f"📂 找到 {csv_file}，開始讀取與分割資料...")
        df = pd.read_csv(csv_file)
        
        # 🌟 核心修改：資料切割與另存新檔
        if len(df) > MAX_RECORDS:
            df_db = df.head(MAX_RECORDS)
            df_ml = df.iloc[MAX_RECORDS:]
            
            # 將 70 萬筆以後的資料匯出成新的 CSV
            ml_file = "spotify_data_ml.csv"
            df_ml.to_csv(ml_file, index=False)
            print(f"📦 已將剩餘的 {len(df_ml)} 筆資料另存為 {ml_file}，供後續機器學習訓練使用！")
        else:
            df_db = df
            print("資料總數未超過 70 萬筆，將全數寫入資料庫。")
            
        return df_db.to_dict('records')
    else:
        print("⚠️ 未找到 CSV 檔案，自動生成測試資料...")
        return [
            {"id": str(uuid.uuid4())[:16], "name": "天灰灰", "artists": "周杰倫", "lyrics": "天灰灰 會不會 讓我忘了你是誰", "energy": 0.3, "valence": 0.2, "tempo": 75.0, "danceability": 0.4},
            {"id": str(uuid.uuid4())[:16], "name": "Shape of You", "artists": "Ed Sheeran", "lyrics": "The club isn't the best place", "energy": 0.8, "valence": 0.9, "tempo": 95.5, "danceability": 0.8}
        ]

def import_to_db():
    data = get_sample_data()
    
    values = [
        (
            str(d.get('id', uuid.uuid4())), 
            str(d.get('name', 'Unknown')), 
            str(d.get('artists', 'Unknown')), 
            str(d.get('lyrics', '')) if pd.notna(d.get('lyrics')) else "", 
            float(d.get('energy', 0.0)) if pd.notna(d.get('energy')) else 0.0, 
            float(d.get('valence', 0.0)) if pd.notna(d.get('valence')) else 0.0, 
            float(d.get('tempo', 0.0)) if pd.notna(d.get('tempo')) else 0.0, 
            float(d.get('danceability', 0.0)) if pd.notna(d.get('danceability')) else 0.0, 
            "" 
        )
        for d in data
    ]
    
    insert_query = """
        INSERT INTO tracks (track_id, title, artist, lyrics, energy, valence, tempo, danceability, preview_url)
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING;
    """
    
    batch_size = 5000
    total = len(values)
    start_index = 0 
    
    print(f"總計 {total} 筆資料，開始分批寫入資料庫...")
    
    for i in range(start_index, total, batch_size):
        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            batch = values[i:i + batch_size]
            execute_values(cur, insert_query, batch)
            conn.commit()
            
            cur.close()
            conn.close()
            
            print(f"✅ 進度：{min(i + batch_size, total)} / {total} 筆已完成")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 第 {i} 批次匯入失敗，錯誤訊息：{e}")
            if conn is not None:
                conn.close()
            time.sleep(5)

    print("🎉 70 萬筆資料匯入大功告成！")

if __name__ == '__main__':
    import_to_db()
