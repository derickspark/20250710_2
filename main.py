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

    df1['연월_날짜'] = pd.to_datetime(df1['연월'].str.replace("\ub144 ", "-").str.replace("\uc6d4", ""), format="%Y-%m")
    df2['연월_날짜'] = pd.to_datetime(df2['연월'].str.replace("\ub144 ", "-").str.replace("\uc6d4", ""), format="%Y-%m")

    df1['연도'] = df1['연월_날짜'].dt.year
    df1['월'] = df1['연월_날짜'].dt.month
    df2['연도'] = df2['연월_날짜'].dt.year
    df2['월'] = df2['연월_날짜'].dt.month

    df1['지역'] = df1['구'] + " " + df1['동']
    df2['지역'] = df2['구'] + " " + df2['동']

    return df1, df2

# ----------------------------
# 데이터 로드
# ----------------------------
data1, data2 = load_data()

st.set_page_config(page_title="서울 아파트 시세 데이스보드", layout="wide")
st.title(":cityscape: 서울 아파트 시세 데이스보드")

# ----------------------------
# 사이드바: 지역1, 지역2 및 연도 범위
# ----------------------------
st.sidebar.header(":round_pushpin: 비교 지역 선택")

gu_list = sorted(data1['구'].unique())

gu1 = st.sidebar.selectbox("자치구 (지역 1)", gu_list, key="gu1")
dong1_list = sorted(data1[data1['구'] == gu1]['동'].unique())
dong1 = st.sidebar.selectbox("법정동 (지역 1)", dong1_list, key="dong1")

st.sidebar.markdown("---")
gu2 = st.sidebar.selectbox("자치구 (지역 2)", gu_list, index=1 if gu1 == gu_list[0] else 0, key="gu2")
dong2_list = sorted(data1[data1['구'] == gu2]['동'].unique())
dong2 = st.sidebar.selectbox("법정동 (지역 2)", dong2_list, key="dong2")

st.sidebar.markdown("---")
min_year = int(data1['연도'].min())
max_year = int(data1['연도'].max())
year_range = st.sidebar.slider("\ud3c9가 범위 (연도)", min_value=min_year, max_value=max_year, value=(2018, 2024))
year_min, year_max = year_range

# ----------------------------
# 선택 결과 필터링
# ----------------------------
df1 = data1[(data1['구'] == gu1) & (data1['동'] == dong1) & (data1['연도'].between(year_min, year_max))].copy()
df1['지역'] = f"{gu1} {dong1}"

df2 = data1[(data1['구'] == gu2) & (data1['동'] == dong2) & (data1['연도'].between(year_min, year_max))].copy()
df2['지역'] = f"{gu2} {dong2}"

selected_df = pd.concat([df1, df2], ignore_index=True).sort_values(['지역', '연월_날짜'])

# ----------------------------
# 1. 선택 지역 가격 후유 선그랙
# ----------------------------
st.subheader("1. \uc120\ud0dd \uc9c0\uc5ed \ud3c9\uade0\uac00\uaca9 / \ud3c9\ub2f9\uac00\uaca9 \ucd94이")

fig1 = px.line(
    selected_df,
    x='연월_날짜',
    y='p1',
    color='지역',
    title="\ud3c9\uade0\uac00\uaca9(\ub9cc\uc6d0) \ucd94\uc774",
    labels={'p1': '평균가격(만원)', '연월_날짜': '연월'}
)
fig2 = px.line(
    selected_df,
    x='연월_날짜',
    y='p2',
    color='지역',
    title="\ud3c9\ub2f9\uac00\uaca9(\ub9cc\uc6d0) \ucd94\uc774",
    labels={'p2': '평당가격(만원)', '연월_날짜': '연월'}
)
fig1.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)
fig2.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# 2. 자치구별 평당가격 막대그래프 (내림차순 정렬)
# ----------------------------
st.subheader("2. \uc11c\uc6b8 \uc804\uccb4 \uc790\uce58\uad6c \ud3c9\ub2f9\uac00\uaca9 \ub9c8\uae08\uadf8\ub798\ud504")

avg_by_gu = data1[data1['연도'].between(year_min, year_max)].groupby('구')['p2'].mean().reset_index()
avg_by_gu['구분'] = avg_by_gu['구'].apply(lambda x: '선택' if x in [gu1, gu2] else '기타')
avg_by_gu = avg_by_gu.sort_values('p2', ascending=False)

fig_bar = px.bar(
    avg_by_gu,
    x='구',
    y='p2',
    color='구분',
    title=f"\uc790\uce58\uad6c\ubcc4 \ud3c9\ub2f9\uac00\uaca9 (\uc5f0\ub3c4: {year_min} ~ {year_max})",
    labels={'p2': '평당가격(만원)', '구': '자치구'},
    color_discrete_map={'선택': 'crimson', '기타': 'lightgray'}
)
fig_bar.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# 3. 서울 전체 단지 산점도 (x: 평당가격, y: 평균가격)
# ----------------------------
st.subheader("3. \uc804 \ub2e8\uc9c0 \ud3c9\ub2f9\uac00\uaca9 \ubc0f \ud3c9\uade0\uac00\uaca9 \uc0b0\uc810\ub3c4")

scatter_df = data2[data2['연도'].between(year_min, year_max)].copy()
scatter_df['강조'] = scatter_df['동'].apply(lambda x: '선택지역' if x in [dong1, dong2] else '기타')

fig_scatter = px.scatter(
    scatter_df,
    x='p2',
    y='p1',
    color='강조',
    hover_data=['단지명', '구', '동', '연월'],
    title="\ub2e8\uc9c0\ubcc4 \ud3c9\ub2f9\uac00\uaca9 vs \ud3c9\uade0\uac00\uaca9 \uc0b0\uc810\ub3c4",
    labels={'p2': '평당가격(만원)', 'p1': '평균가격(만원)'},
    color_discrete_map={'선택지역': 'firebrick', '기타': 'lightgray'}
)
fig_scatter.update_layout(font=dict(family="Noto Sans KR"))
st.plotly_chart(fig_scatter, use_container_width=True)
