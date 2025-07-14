import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# 데이터 불러오기 및 전처리
# ----------------------------
@st.cache_data
def load_data():
    df1 = pd.read_csv("data1.csv", dtype={'연월': str})
    df2 = pd.read_csv("data2.csv", dtype={'연월': str})

    # "2015년 01월" → datetime
    df1['연월_날짜'] = pd.to_datetime(df1['연월'].str.replace("년 ", "-").str.replace("월", ""), format="%Y-%m")
    df2['연월_날짜'] = pd.to_datetime(df2['연월'].str.replace("년 ", "-").str.replace("월", ""), format="%Y-%m")

    # 연도/월 파생 변수 생성
    df1['연도'] = df1['연월_날짜'].dt.year
    df1['월'] = df1['연월_날짜'].dt.month
    df2['연도'] = df2['연월_날짜'].dt.year
    df2['월'] = df2['연월_날짜'].dt.month

    # 지역 컬럼 생성
    df1['지역'] = df1['구'] + " " + df1['동']
    df2['지역'] = df2['구'] + " " + df2['동']

    return df1, df2

data1, data2 = load_data()

st.set_page_config(page_title="서울 아파트 시세 분석", layout="wide")
st.title("🏙️ 서울 아파트 시세 분석 대시보드")

# ----------------------------
# 사이드바 필터링
# ----------------------------
st.sidebar.header("📌 분석 조건 선택")

gu_multi = st.sidebar.multiselect("자치구 선택", sorted(data1['구'].unique()))
dong_multi = st.sidebar.multiselect("법정동 선택", sorted(data1['동'].unique()))
year_multi = st.sidebar.multiselect("연도 선택", sorted(data1['연도'].unique()))

if not gu_multi or not dong_multi or not year_multi:
    st.info("왼쪽에서 자치구, 법정동, 연도를 모두 선택하세요.")
    st.stop()

# ----------------------------
# 데이터 필터링
# ----------------------------
filtered1 = data1[
    data1['구'].isin(gu_multi) &
    data1['동'].isin(dong_multi) &
    data1['연도'].isin(year_multi)
].copy()

filtered2 = data2[
    data2['구'].isin(gu_multi) &
    data2['동'].isin(dong_multi) &
    data2['연도'].isin(year_multi)
].copy()

# ----------------------------
# ① 평균가격 / 평당가격 추이
# ----------------------------
st.subheader("① 선택 지역의 월별 평균가격 및 평당가격 추이")

filtered1 = filtered1.sort_values(['지역', '연월_날짜'])

fig1 = px.line(
    filtered1,
    x='연월_날짜',
    y='p1',
    color='지역',
    title="📊 평균가격(만원) 추이",
    labels={'p1': '평균가격(만원)', '연월_날짜': '연월'}
)
fig1.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)

fig2 = px.line(
    filtered1,
    x='연월_날짜',
    y='p2',
    color='지역',
    title="📊 평당가격(만원) 추이",
    labels={'p2': '평당가격(만원)', '연월_날짜': '연월'}
)
fig2.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# ② 서울 전체 자치구 평당가격 막대그래프
# ----------------------------
st.subheader("② 서울 전체 자치구 평당가격 비교 (선택 연도 기준)")

avg_by_gu = data1[data1['연도'].isin(year_multi)].groupby('구')['p2'].mean().reset_index()
avg_by_gu['구분'] = avg_by_gu['구'].apply(lambda x: '선택' if x in gu_multi else '기타')

fig_bar = px.bar(
    avg_by_gu,
    x='구',
    y='p2',
    color='구분',
    title=f"📊 자치구별 평균 평당가격 (연도: {', '.join(map(str, year_multi))})",
    labels={'p2': '평당가격(만원)', '구': '자치구'},
    color_discrete_map={'선택': 'crimson', '기타': 'lightgray'}
)
fig_bar.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)

st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# ③ 서울 전체 단지 평당가격 산점도
# ----------------------------
st.subheader("③ 서울 전체 단지의 평당가격 산점도")

scatter_df = data2[data2['연도'].isin(year_multi)].copy()
scatter_df['강조'] = scatter_df['동'].apply(lambda x: '선택지역' if x in dong_multi else '기타')

fig_scatter = px.scatter(
    scatter_df,
    x='연월_날짜',
    y='p2',
    color='강조',
    hover_data=['단지명', '구', '동'],
    title="📌 단지별 평당가격 산점도",
    labels={'p2': '평당가격(만원)', '연월_날짜': '연월'}
)
fig_scatter.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)

st.plotly_chart(fig_scatter, use_container_width=True)
