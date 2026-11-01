import streamlit as st
import requests
import pandas as pd

# 設定你的 FastAPI 伺服器網址
API_URL = "http://127.0.0.1:8000"

# 網頁基本設定
st.set_page_config(page_title="Spotify 推薦系統 Demo", page_icon="🎵", layout="wide")
st.title("🎵 Spotify 音樂推薦系統 (期中展示版)")
st.markdown("這個介面將直接呼叫背後的 FastAPI，並從 PostgreSQL 的 70 萬筆資料中即時檢索。")

# 建立兩個分頁
tab1, tab2 = st.tabs(["🔍 關鍵字搜尋", "🎛️ 聲學氛圍推薦 (Vibe Match)"])

# --- 分頁 1：關鍵字搜尋 ---
with tab1:
    st.subheader("透過歌名或歌手進行模糊搜尋")
    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("輸入關鍵字 (如：love, 周杰倫, taylor)", "love")
    with col2:
        st.write("") # 排版用空白
        st.write("")
        search_btn = st.button("搜尋歌曲", use_container_width=True)
    
    if search_btn:
        with st.spinner('搜尋中...'):
            response = requests.get(f"{API_URL}/api/search", params={"keyword": keyword, "limit": 15})
            if response.status_code == 200:
                data = response.json()["data"]
                if data:
                    st.success(f"找到 {len(data)} 筆結果！")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("找不到相符的歌曲。")
            else:
                st.error("API 連線失敗，請確認 FastAPI 是否有啟動。")

# --- 分頁 2：聲學特徵推薦 ---
with tab2:
    st.subheader("滑動數值，尋找完美氛圍的音樂")
    st.markdown("利用資料庫 **B-Tree 複合索引** 進行多維度相近值檢索：")
    
    col_e, col_v, col_t = st.columns(3)
    with col_e:
        energy = st.slider("⚡ 能量 (Energy) - 越右邊越動感", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
    with col_v:
        valence = st.slider("😊 愉悅度 (Valence) - 越右邊越快樂", min_value=0.0, max_value=1.0, value=0.8, step=0.01)
    with col_t:
        tempo = st.slider("🥁 節奏 (Tempo BPM) - 越右邊越快", min_value=40.0, max_value=200.0, value=120.0, step=1.0)
        
    recommend_btn = st.button("🚀 產生推薦", use_container_width=True, type="primary")
    
    if recommend_btn:
        with st.spinner('演算法計算中...'):
            response = requests.get(
                f"{API_URL}/api/recommend", 
                params={"energy": energy, "valence": valence, "tempo": tempo, "limit": 15}
            )
            if response.status_code == 200:
                data = response.json()["data"]
                if data:
                    st.success("推薦清單產生完畢！")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("在這個範圍內沒有找到合適的歌曲，請稍微調整數值。")
            else:
                st.error("API 連線失敗，請確認 FastAPI 是否有啟動。")

