import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ------------------------------------------
# 1. 페이지 설정
# ------------------------------------------
st.set_page_config(
    page_title="동네별 인구 피라미드",
    page_icon="🏘️",
    layout="wide"
)

# 따뜻한 색감의 화면 디자인
st.markdown("""
<style>
    .stApp {
        background-color: #FFF9F2;
    }
    h1, h2, h3 {
        color: #754C35;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #F0D9C5;
        padding: 16px;
        border-radius: 12px;
    }
    .warning-note {
        background-color: #FFF0D8;
        border: 1px solid #E6A23C;
        color: #8A4B08;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 4px 0 12px 0;
        font-weight: 600;
    }
    .summary-note {
        background-color: #FFFFFF;
        border-left: 5px solid #D98268;
        border-radius: 8px;
        padding: 14px 16px;
        margin-top: 10px;
        color: #5C4638;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏘️ 동네별 인구 피라미드")
st.write("우리 동네의 연령별 남녀 인구를 한눈에 확인해 보세요.")
st.divider()


# ------------------------------------------
# 2. 데이터 불러오기
# ------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/first2022-cyber/"
    "contents/main/population_ts_yearly_gender.zip"
)


@st.cache_data
def load_data():
    # ZIP 파일 주소를 pandas에 전달하면 압축 파일을 읽을 수 있습니다.
    df = pd.read_csv(DATA_URL, compression="zip")

    # 열 이름에 불필요한 공백이 있으면 제거합니다.
    df.columns = df.columns.astype(str).str.strip()

    # 연도는 숫자로 변환합니다.
    df["연도"] = pd.to_numeric(df["연도"], errors="coerce")

    # 최신 연도 데이터만 남깁니다.
    latest_year = int(df["연도"].max())
    df = df[df["연도"] == latest_year].copy()

    # 시도, 시군구, 동 이름을 문자열로 통일합니다.
    for col in ["시도", "시군구", "동"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # 인구 데이터 열을 숫자로 변환합니다.
    age_cols = [
        col for col in df.columns
        if col.startswith("남_") or col.startswith("여_")
    ]

    for col in age_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df, latest_year


try:
    df, latest_year = load_data()
