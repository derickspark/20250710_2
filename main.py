import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    data1 = pd.read_csv("data1.csv", dtype={'계약년월': str})
    data2 = pd.read_csv("data2.csv", dtype={'계약년월': str})
    return data1, data2

data1, data2 = load_data()

st.set_page_config(page_title="서울 아파트 시세 분석", layout="wide")
st.title("서울 아파트 시세 분석 대시보드 (2024~2025)")

# ----------------------------
# 사용자 입력
# ----------------------------
gu_options = ["선택하세요"] + sorted(data1['구'].unique())
selected_gu = st.selectbox("자치구를 선택하세요", gu_options)

dong_options = ["선택하세요"]
if selected_gu != "선택하세요":
    dong_options += sorted(data1[data1['구'] == selected_gu]['동'].unique())
selected_dong = st.selectbox("법정동을 선택하세요", dong_options)

if selected_gu == "선택하세요" or selected_dong == "선택하세요":
    st.info("자치구와 법정동을 모두 선택하세요.")
    st.stop()

# ----------------------------
# ① 선택 지역의 월별 평균 가격
# ----------------------------
st.subheader("① 월별 평균가격 및 평당가격 (data1 기준)")
subset1 = data1[(data1['구'] == selected_gu) & (data1['동'] == selected_dong)].copy()
subset1 = subset1.sort_values('계약년월')

st.dataframe(
    subset1[['계약년월', 'p1', 'p2']]
    .rename(columns={'p1': '평균가격(만원)', 'p2': '평당가격(만원)'})
    .style.format({'평균가격(만원)': '{:,.0f}', '평당가격(만원)': '{:,.0f}'})
)

# ----------------------------
# ② 월별 최고/최저 단지 (data2 기준)
# ----------------------------
st.subheader("② 월별 최고/최저 단지 (data2 기준)")

subset2 = data2[(data2['구'] == selected_gu) & (data2['동'] == selected_dong)].copy()
if subset2.empty:
    st.warning("해당 지역에 대한 단지별 정보가 data2.csv에 없습니다.")
else:
    by_month = subset2.groupby('계약년월')

    max_p1_list = []
    min_p1_list = []
    max_p2_list = []
    min_p2_list = []

    for name, group in by_month:
        max_p1_list.append(group.loc[group['p1'].idxmax()])
        min_p1_list.append(group.loc[group['p1'].idxmin()])
        max_p2_list.append(group.loc[group['p2'].idxmax()])
        min_p2_list.append(group.loc[group['p2'].idxmin()])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("📈 **계약년월별 평균가격 최고/최저 단지**")
        st.dataframe(
            pd.DataFrame(max_p1_list + min_p1_list)
            .sort_values('계약년월')[['계약년월', '단지명', 'p1']]
            .rename(columns={'p1': '평균가격(만원)'})
        )
    with col2:
        st.markdown("🏢 **계약년월별 평당가격 최고/최저 단지**")
        st.dataframe(
            pd.DataFrame(max_p2_list + min_p2_list)
            .sort_values('계약년월')[['계약년월', '단지명', 'p2']]
            .rename(columns={'p2': '평당가격(만원)'})
        )

# ----------------------------
# ③ 선택지역 vs 기타지역 추이 (plotly)
# ----------------------------
st.subheader("③ 평당가격 추이 비교 (선택지역 vs 기타지역)")

data1['지역구분'] = data1.apply(
    lambda row: '선택지역' if (row['구'] == selected_gu and row['동'] == selected_dong) else '기타지역',
    axis=1
)

trend = data1.groupby(['계약년월', '지역구분'])['p2'].mean().reset_index()

fig = px.line(
    trend,
    x='계약년월',
    y='p2',
    color='지역구분',
    title=f"{selected_gu} {selected_dong} vs 기타 지역 평당가격 추이",
    labels={'p2': '평당가격(만원)', '계약년월': '계약년월'},
)

fig.update_layout(
    font=dict(family="Noto Sans KR, sans-serif", size=14),
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)
