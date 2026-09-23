import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 8자리 숫자 -> datetime
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    # 장르: 세로막대(|) 기호로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre_main"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    return df


df = load_data()

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 든 영화 중, 해당 기간에 개봉한 216편의 요약 데이터")

st.divider()

# =========================================================
# 구역 1. 장르별 영화 편수 분포
# =========================================================
st.header("1. 장르별 영화 편수")

genre_counts = df["genre_main"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = go.Figure(
    data=[
        go.Pie(
            labels=genre_counts["genre"],
            values=genre_counts["count"],
            hole=0.5,
            hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
        )
    ]
)
fig1.update_layout(
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig1, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 2. (다음 그래프 자리)
# =========================================================
st.header("2. (다음 그래프 준비 중)")
st.caption("이 자리에 다음 그래프가 추가될 예정입니다.")

st.divider()
