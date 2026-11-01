from fastapi import FastAPI, HTTPException, Query
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 初始化 FastAPI 應用程式
app = FastAPI(title="Spotify 推薦系統 API", description="提供音樂搜尋與推薦功能")

# 建立資料庫連線的輔助函式
def get_db_connection():
    # 使用 RealDictCursor 讓查詢結果自動變成像 JSON 格式的字典
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# 1. 根目錄測試 API
@app.get("/")
def read_root():
    return {"message": "歡迎來到 Spotify 音樂推薦系統 API！"}

# 2. 關鍵字搜尋 API (搜尋歌名或歌手)
@app.get("/api/search")
def search_tracks(
    keyword: str = Query(..., description="請輸入歌名或歌手關鍵字"),
    limit: int = Query(10, description="回傳的資料筆數限制")
):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 使用 ILIKE 進行不分大小寫的模糊搜尋
        query = """
            SELECT track_id, title, artist, energy, valence, tempo 
            FROM tracks 
            WHERE title ILIKE %s OR artist ILIKE %s
            LIMIT %s;
        """
        search_term = f"%{keyword}%"
        cur.execute(query, (search_term, search_term, limit))
        
        results = cur.fetchall()
        return {
            "keyword": keyword,
            "count": len(results),
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料庫查詢錯誤: {str(e)}")
    finally:
        if conn:
            cur.close()
            conn.close()

# 3. 聲學特徵推薦 API (Vibe Match 氛圍推薦)
@app.get("/api/recommend")
def recommend_by_vibe(
    energy: float = Query(0.5, description="能量 (0.0 柔和 ~ 1.0 動感)"),
    valence: float = Query(0.5, description="愉悅度 (0.0 悲傷 ~ 1.0 快樂)"),
    tempo: float = Query(120.0, description="BPM 節奏 (如 80 慢歌, 120 輕快)"),
    limit: int = Query(10, description="回傳筆數")
):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 設定檢索範圍 (Tolerance)，讓 B-Tree 索引發揮最大效能
        e_min, e_max = energy - 0.2, energy + 0.2
        v_min, v_max = valence - 0.2, valence + 0.2
        t_min, t_max = tempo - 20.0, tempo + 20.0
        
        # 結合範圍過濾 (WHERE BETWEEN) 與 絕對值距離排序 (ORDER BY ABS)
        query = """
            SELECT track_id, title, artist, energy, valence, tempo 
            FROM tracks 
            WHERE energy BETWEEN %s AND %s
              AND valence BETWEEN %s AND %s
              AND tempo BETWEEN %s AND %s
            ORDER BY (ABS(energy - %s) + ABS(valence - %s) + ABS(tempo - %s)/100.0) ASC
            LIMIT %s;
        """
        
        cur.execute(query, (
            e_min, e_max, v_min, v_max, t_min, t_max, 
            energy, valence, tempo, limit
        ))
        
        results = cur.fetchall()
        return {
            "target_vibe": {"energy": energy, "valence": valence, "tempo": tempo},
            "count": len(results),
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推薦引擎查詢錯誤: {str(e)}")
    finally:
        if conn:
            cur.close()
            conn.close()
