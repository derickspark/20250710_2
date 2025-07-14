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

gu_list = ["선택하세요"] + sorted(data1['구'].unique())

gu1 = st.sidebar.selectbox("자치구 (지역 1)", gu_list, key="gu1")
if gu1 != "선택하세요":
    dong1_list = ["선택하세요"] + sorted(data1[data1['구'] == gu1]['동'].unique())
    dong1 = st.sidebar.selectbox("법정동 (지역 1)", dong1_list, key="dong1")
else:
    dong1 = "선택하세요"

st.sidebar.markdown("---")

gu2 = st.sidebar.selectbox("자치구 (지역 2)", gu_list, key="gu2")
if gu2 != "선택하세요":
    dong2_list = ["선택하세요"] + sorted(data1[data1['구'] == gu2]['동'].unique())
    dong2 = st.sidebar.selectbox("법정동 (지역 2)", dong2_list, key="dong2")
else:
    dong2 = "선택하세요"

st.sidebar.markdown("---")
min_year = int(data1['연도'].min())
max_year = int(data1['연도'].max())
year_range = st.sidebar.slider("평가 범위 (연도)", min_value=min_year, max_value=max_year, value=(2018, 2024))
year_min, year_max = year_range

# ----------------------------
# 선택 결과 필터링
# ----------------------------
selected_df = pd.DataFrame()
gu1_label = f"{gu1} {dong1}" if gu1 != "선택하세요" and dong1 != "선택하세요" else None
gu2_label = f"{gu2} {dong2}" if gu2 != "선택하세요" and dong2 != "선택하세요" else None

if gu1_label:
    df1 = data1[(data1['구'] == gu1) & (data1['동'] == dong1) & (data1['연도'].between(year_min, year_max))].copy()
    df1['지역'] = gu1_label
    df1['구분'] = gu1_label
    selected_df = pd.concat([selected_df, df1], ignore_index=True)

if gu2_label:
    df2 = data1[(data1['구'] == gu2) & (data1['동'] == dong2) & (data1['연도'].between(year_min, year_max))].copy()
    df2['지역'] = gu2_label
    df2['구분'] = gu2_label
    selected_df = pd.concat([selected_df, df2], ignore_index=True)

# 서울 전체 평균
seoul_avg = data1[data1['연도'].between(year_min, year_max)].groupby('연월_날짜')[['p1', 'p2']].mean().reset_index()
seoul_avg['지역'] = '서울 전체'
seoul_avg['구분'] = '서울 전체'

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
    color='구분',
    title="평균가격(만원) 추이",
    labels={'p1': '평균가격(만원)', '연월_날짜': '연월'}
)
fig2 = px.line(
    plot_df,
    x='연월_날짜',
    y='p2',
    color='구분',
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
avg_by_gu = avg_by_gu.sort_values('p2', ascending=False)

avg_by_gu['구'] = pd.Categorical(avg_by_gu['구'], categories=avg_by_gu['구'], ordered=True)

def assign_color_label(row):
    if row['구'] == gu1:
        return gu1_label
    elif row['구'] == gu2:
        return gu2_label
    else:
        return '기타'

avg_by_gu['구분'] = avg_by_gu.apply(assign_color_label, axis=1)

color_map = {
    '기타': '#d3d3d3',
    gu1_label: '#1f77b4',  # 짙은 파랑
    gu2_label: '#aec7e8'   # 옅은 하늘색
}

fig_bar = px.bar(
    avg_by_gu,
    x='구',
    y='p2',
    color='구분',
    color_discrete_map=color_map,
    title=f"자치구별 평균 평당가격 (연도: {year_min} ~ {year_max})",
    labels={'p2': '평당가격(만원)', '구': '자치구'}
)
fig_bar.update_layout(font=dict(family="Noto Sans KR"), xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# 3. 서울 전체 단지 산점도 (x: 평당가격, y: 평균가격)
# ----------------------------
st.subheader("3. 전 단지 평당가격 및 평균가격 산점도")

scatter_df = data2[data2['연도'].between(year_min, year_max)].copy()
scatter_df['지역'] = scatter_df['구'] + " " + scatter_df['동']

highlight_regions = {}
if gu1_label:
    highlight_regions[gu1_label] = gu1_label
if gu2_label:
    highlight_regions[gu2_label] = gu2_label

scatter_df['구분'] = scatter_df['지역'].apply(lambda x: highlight_regions[x] if x in highlight_regions else '기타')

fig_scatter = px.scatter(
    scatter_df,
    x='p2',
    y='p1',
    color='구분',
    color_discrete_map=color_map,
    hover_data=['단지명', '구', '동', '연월'],
    title="단지별 평당가격 vs 평균가격 산점도",
    labels={'p2': '평당가격(만원)', 'p1': '평균가격(만원)'}
)
fig_scatter.update_layout(font=dict(family="Noto Sans KR"))
st.plotly_chart(fig_scatter, use_container_width=True)
