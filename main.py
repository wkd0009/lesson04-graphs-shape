import io
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # raw.githubusercontent.com이 기본 User-Agent 요청을 막는 경우가 있어
    # requests로 헤더를 지정해 받아온 뒤 pandas에 넘긴다.
    headers = {"User-Agent": "Mozilla/5.0 (Streamlit App)"}
    response = requests.get(DATA_URL, headers=headers, timeout=10)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))

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
# 구역 2. 장르 안에 영화 - 총 관객 트리맵
# =========================================================
st.header("2. 장르별 영화 트리맵 (칸 크기 = 총 관객)")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체"), "genre_main", "movieNm"],
    values="total_audi",
)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>"
)
fig2.update_layout(margin=dict(t=20, b=20, l=20, r=20))

st.plotly_chart(fig2, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 3. 총 관객 히스토그램
# =========================================================
st.header("3. 총 관객(total_audi) 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
)
fig3.update_traces(
    hovertemplate="구간: %{x}<br>편수: %{y}편<extra></extra>"
)
fig3.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수",
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 많은 영화가 몰린 구간, 총 관객 1위 영화 계산
counts = pd.cut(df["total_audi"], bins=30, include_lowest=True).value_counts(sort=False)
top_bin = counts.idxmax()
top_bin_count = counts.max()

top_movie = df.loc[df["total_audi"].idxmax()]

st.info(
    f"💡 이 그래프로 알 수 있는 것: 대부분의 영화는 총 관객 **{int(top_bin.left):,}명 ~ {int(top_bin.right):,}명** "
    f"구간에 몰려 있으며({top_bin_count}편), 이 기간 총 관객이 가장 많은 영화는 "
    f"**'{top_movie['movieNm']}'**({int(top_movie['total_audi']):,}명)입니다."
)

st.divider()

# =========================================================
# 구역 4. 개봉일 스크린수 vs 총 관객 산점도
# =========================================================
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객", "genre_main": "장르"},
)
fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}<br>총 관객: %{y:,}명<extra></extra>"
)
fig4.update_layout(margin=dict(t=20, b=20, l=20, r=20))

st.plotly_chart(fig4, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 5. 장르별 총 관객 상자 그림 (10편 이상 장르만)
# =========================================================
st.header("5. 장르별 총 관객 분포 (10편 이상인 장르만)")

genre_movie_counts = df["genre_main"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major = df[df["genre_main"].isin(major_genres)]

fig5 = px.box(
    df_major,
    x="genre_main",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    labels={"genre_main": "장르", "total_audi": "총 관객"},
)
fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객: %{y:,}명<extra></extra>"
)
fig5.update_layout(margin=dict(t=20, b=20, l=20, r=20))

st.plotly_chart(fig5, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 6. 스크린수 vs 총 관객 버블 그래프 (점 크기 = 첫 주 관객)
# =========================================================
st.header("6. 개봉일 스크린수와 총 관객 (버블 크기 = 첫 주 관객)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_main",
    hover_name="movieNm",
    size_max=40,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre_main": "장르",
        "first_week_audi": "첫 주 관객",
    },
)
fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}<br>"
        "총 관객: %{y:,}명<br>첫 주 관객: %{marker.size:,}명<extra></extra>"
    )
)
fig6.update_layout(margin=dict(t=20, b=20, l=20, r=20))

st.plotly_chart(fig6, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 7. 제작 국가 → 장르 선버스트 (칸 크기 = 영화 편수)
# =========================================================
st.header("7. 제작 국가별 장르 구성")

fig7 = px.sunburst(
    df,
    path=["nation", "genre_main"],
    labels={"nation": "제작 국가", "genre_main": "장르"},
)
fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<extra></extra>"
)
fig7.update_layout(margin=dict(t=20, b=20, l=20, r=20))

st.plotly_chart(fig7, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 8. 10위권에 오래 머문 영화는 총 관객도 많은가
# =========================================================
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")

fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={"days_in_top10": "10위권에 머문 날수", "total_audi": "총 관객"},
)
fig8.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>10위권 머문 날수: %{x}일<br>총 관객: %{y:,}명<extra></extra>"
)
fig8.update_layout(margin=dict(t=20, b=20, l=20, r=20))

st.plotly_chart(fig8, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# =========================================================
# 구역 9. (다음 그래프 자리)
# =========================================================
st.header("9. (다음 그래프 준비 중)")
st.caption("이 자리에 다음 그래프가 추가될 예정입니다.")

st.divider()
