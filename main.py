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

except Exception as e:
    st.error("인구 데이터를 불러오지 못했습니다.")
    st.info(
        "인터넷 연결과 데이터 주소를 확인한 후 다시 실행해 주세요."
    )
    st.caption(f"오류 내용: {e}")
    st.stop()


# ------------------------------------------
# 3. 나이 열 순서 만들기
# ------------------------------------------
# 나이 라벨을 0세부터 100세 이상까지 직접 만듭니다.
# 이 순서를 그래프의 세로축에 그대로 적용합니다.
ages = [f"{i}세" for i in range(101)] + ["100세 이상"]

# 데이터 열 이름과 화면에 표시할 나이 라벨을 연결합니다.
# 0~99세는 해당 나이의 열을 사용하고,
# 100세 이상은 '100세 이상' 열을 사용합니다.
male_cols = []
female_cols = []

for age in range(100):
    male_cols.append(f"남_{age}세")
    female_cols.append(f"여_{age}세")

male_cols.append("남_100세 이상")
female_cols.append("여_100세 이상")

# 실제 데이터에 필요한 나이 열이 있는지 확인합니다.
missing_cols = [
    col for col in male_cols + female_cols
    if col not in df.columns
]

if missing_cols:
    st.error("데이터에서 일부 나이별 인구 열을 찾지 못했습니다.")
    st.write("찾지 못한 열:", missing_cols)
    st.stop()


# ------------------------------------------
# 4. 지역 선택 드롭다운 3개
# ------------------------------------------
st.subheader("📍 지역 선택")

col1, col2, col3 = st.columns(3)

with col1:
    sido_list = sorted(df["시도"].unique().tolist())

    selected_sido = st.selectbox(
        "① 시도 선택",
        sido_list
    )

# 선택한 시도에 속하는 시군구만 표시합니다.
df_sido = df[df["시도"] == selected_sido]

with col2:
    sigungu_list = sorted(df_sido["시군구"].unique().tolist())

    selected_sigungu = st.selectbox(
        "② 시군구 선택",
        sigungu_list
    )

# 선택한 시도와 시군구에 속하는 동만 표시합니다.
df_sigungu = df_sido[
    df_sido["시군구"] == selected_sigungu
]

with col3:
    dong_list = sorted(df_sigungu["동"].unique().tolist())

    selected_dong = st.selectbox(
        "③ 동 선택",
        dong_list
    )


# ------------------------------------------
# 5. 선택한 동네의 데이터 가져오기
# ------------------------------------------
selected_data = df_sigungu[
    df_sigungu["동"] == selected_dong
]

if selected_data.empty:
    st.warning("선택한 지역의 인구 데이터가 없습니다.")
    st.stop()

# 같은 동네의 행이 여러 개라면 나이별 인구를 합산합니다.
# 일반적으로 동네 하나의 행만 존재하더라도 안전하게 처리합니다.
selected_data = selected_data.iloc[0]

male_population = np.array([
    selected_data[col] for col in male_cols
], dtype=float)

female_population = np.array([
    selected_data[col] for col in female_cols
], dtype=float)

# 남성은 왼쪽에 표시하기 위해 음수로 변환합니다.
male_left = -male_population

# 총인구를 계산합니다.
total_male = int(male_population.sum())
total_female = int(female_population.sum())
total_population = total_male + total_female


# ------------------------------------------
# 6. 인구 요약 정보
# ------------------------------------------
st.divider()

st.subheader(
    f"📊 {selected_sido} {selected_sigungu} {selected_dong}"
)

st.caption(f"기준 연도: {latest_year}년")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("전체 인구", f"{total_population:,}명")

with metric2:
    st.metric("남성 인구", f"{total_male:,}명")

with metric3:
    st.metric("여성 인구", f"{total_female:,}명")


# ------------------------------------------
# 7. 인구 피라미드 가로 막대그래프
# ------------------------------------------
fig = go.Figure()

# 남성 인구는 음수로 설정하여 왼쪽에 그립니다.
fig.add_trace(
    go.Bar(
        y=ages,
        x=male_left,
        name="남성",
        orientation="h",
        marker_color="#D98268",
        hovertemplate=(
            "나이: %{y}<br>"
            "남성 인구: %{customdata:,}명"
            "<extra></extra>"
        ),
        customdata=male_population
    )
)

# 여성 인구는 양수로 설정하여 오른쪽에 그립니다.
fig.add_trace(
    go.Bar(
        y=ages,
        x=female_population,
        name="여성",
        orientation="h",
        marker_color="#E8B86D",
        hovertemplate=(
            "나이: %{y}<br>"
            "여성 인구: %{x:,}명"
            "<extra></extra>"
        )
    )
)

# 가로축 눈금은 음수인 남성 인구도 양수처럼 보이게 표시합니다.
# 실제 데이터는 음수이므로 남성 막대가 왼쪽으로 뻗습니다.
max_population = max(
    float(male_population.max()),
    float(female_population.max()),
    1
)

axis_limit = int(np.ceil(max_population / 100) * 100)

tick_step = max(1, axis_limit // 5)

tick_values = list(
    range(-axis_limit, axis_limit + 1, tick_step)
)

tick_text = [f"{abs(value):,}" for value in tick_values]

fig.update_layout(
    title={
        "text": f"{selected_dong} 연령별 인구 피라미드",
        "x": 0.5,
        "xanchor": "center"
    },
    barmode="overlay",
    bargap=0.12,
    height=1000,
    paper_bgcolor="#FFF9F2",
    plot_bgcolor="#FFF9F2",
    font=dict(
        family="Arial, sans-serif",
        size=12,
        color="#5C4638"
    ),
    legend=dict(
        title="성별",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=80, r=40, t=100, b=70),
    xaxis=dict(
        title="인구수 (명)",
        range=[-axis_limit, axis_limit],
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_text,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="#BCA18A",
        gridcolor="#EADFD4"
    ),
    yaxis=dict(
        title="나이",
        type="category",

        # 중요: 나이 순서를 직접 지정합니다.
        # categoryorder='array'는 아래 목록의 순서를 따릅니다.
        # 가로 막대그래프의 세로축은 목록을 아래에서 위로 표시하므로
        # 0세가 맨 아래, 100세 이상이 맨 위에 놓입니다.
        categoryorder="array",
        categoryarray=ages,

        # 축을 통째로 뒤집는 옵션은 사용하지 않습니다.
        # 나이별 인구수로 정렬하지도 않습니다.
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        tickfont=dict(size=10),
        gridcolor="#F1E6DC"
    )
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "※ 남성 인구는 왼쪽에 표시하기 위해 그래프에서 음수로 변환했습니다. "
    "실제 인구수와 요약 정보는 양수 기준입니다."
)


# ------------------------------------------
# 8. 나이별 인구 데이터 표
# ------------------------------------------
with st.expander("📋 나이별 남녀 인구 표 보기"):
    population_table = pd.DataFrame({
        "나이": ages,
        "남성 인구": male_population.astype(int),
        "여성 인구": female_population.astype(int),
        "전체 인구": (
            male_population + female_population
        ).astype(int)
    })

    st.dataframe(
        population_table,
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption("자료: 제공된 읍·면·동 연도별 성별 인구 데이터")
