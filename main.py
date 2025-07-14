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

    df1['연월_날짜'] = pd.to_datetime(df1['연월'].str.replace("년 ", "-").str.replace("월", ""), format="%Y-%m")
    df2['연월_날짜'] = pd.to_datetime(df2['연월'].str.replace("년 ", "-").str.replace("월", ""), format="%Y-%m")

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

st.set_page_config(page_title="서울 아파트 시세 대시보드", layout="wide")
st.title(":cityscape: 서울 아파트 시세 대시보드")

# ----------------------------
# 사이드바: 지역1, 지역2 및 연도 범위 선택
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
year_range = st.sidebar.slider("평가 범위 (연도)", min_value=min_year, max_value=max_year, value=(2018, 2024))
year_min, year_max = year_range

# ----------------------------
# 선택 결과 필터링
# ----------------------------
df1 = data1[(data1['구'] == gu1) & (data1['동'] == dong1) & (data1['연도'].between(year_min, year_max))].copy()
df1['지역'] = f"{gu1} {dong1}"

df2 = data1[(data1['구'] == gu2) & (data1['동'] == dong2) & (data1['연도'].between(year_min, year_max))].copy()
df2['지역'] = f"{gu2} {dong2}"

selected_df = pd.concat([df1, df2], ignore_index=True)

# 서울 전체 평균
seoul_avg = data1[data1['연도'].between(year_min, year_max)].groupby('연월_날짜')[['p1', 'p2']].mean().reset_index()
seoul_avg['지역'] = '서울 전체'

# 병합 및 정렬
plot_df = pd.concat([selected_df, seoul_avg], ignore_index=True).sort_values(['지역', '연월_날짜'])

# ----------------------------
# 1. 선택 지역 및 서울 전체 평균가격/평당가격 추이
# ----------------------------
st.subheader("1. 선택 지역 및 서울 전체 평균가격 / 평당가격 추이")

fig1 = px.line(
    plot_df,
    x='연월_날짜',
    y='p1',
    color='지역',
    title="평균가격(만원) 추이",
    labels={'p1': '평균가격(만원)', '연월_날짜': '연월'}
)
fig2 = px.line(
    plot_df,
    x='연월_날짜',
    y='p2',
    color='지역',
    title="평당가격(만원) 추이",
    labels={'p2': '평당가격(만원)', '연월_날짜': '연월'}
)
fig1.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)
fig2.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# 2. 자치구별 평당가격 막대그래프 (내림차순 정렬)
# ----------------------------
st.subheader("2. 서울 전체 자치구 평당가격 막대그래프")

avg_by_gu = data1[data1['연도'].between(year_min, year_max)].groupby('구')['p2'].mean().reset_index()
avg_by_gu['구분'] = avg_by_gu['구'].apply(lambda x: '선택' if x in [gu1, gu2] else '기타')
avg_by_gu = avg_by_gu.sort_values('p2', ascending=False)

fig_bar = px.bar(
    avg_by_gu,
    x='구',
    y='p2',
    color='구분',
    title=f"자치구별 평균 평당가격 (연도: {year_min} ~ {year_max})",
    labels={'p2': '평당가격(만원)', '구': '자치구'},
    color_discrete_map={'선택': 'crimson', '기타': 'lightgray'}
)
fig_bar.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# 3. 서울 전체 단지 산점도 (x: 평당가격, y: 평균가격)
# ----------------------------
st.subheader("3. 전 단지 평당가격 및 평균가격 산점도")

scatter_df = data2[data2['연도'].between(year_min, year_max)].copy()
scatter_df['지역'] = scatter_df['구'] + " " + scatter_df['동']

highlight_regions = [f"{gu1} {dong1}", f"{gu2} {dong2}"]
scatter_df['강조'] = scatter_df['지역'].apply(lambda x: '선택지역' if x in highlight_regions else '기타')

fig_scatter = px.scatter(
    scatter_df,
    x='p2',
    y='p1',
    color='강조',
    hover_data=['단지명', '구', '동', '연월'],
    title="단지별 평당가격 vs 평균가격 산점도",
    labels={'p2': '평당가격(만원)', 'p1': '평균가격(만원)'},
    color_discrete_map={'선택지역': 'firebrick', '기타': 'lightgray'}
)
fig_scatter.update_layout(font=dict(family="Noto Sans KR"))
st.plotly_chart(fig_scatter, use_container_width=True)
