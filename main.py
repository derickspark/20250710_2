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

    # "2015년 01월" → datetime으로 변환
    df1['연월_날짜'] = pd.to_datetime(df1['연월'].str.replace("년 ", "-").str.replace("월", ""), format="%Y-%m")
    df2['연월_날짜'] = pd.to_datetime(df2['연월'].str.replace("년 ", "-").str.replace("월", ""), format="%Y-%m")

    # 지역 구분 필드 생성
    df1['지역'] = df1['구'] + " " + df1['동']
    df2['지역'] = df2['구'] + " " + df2['동']

    return df1, df2

data1, data2 = load_data()

st.set_page_config(page_title="서울 아파트 시세 분석", layout="wide")
st.title("서울 아파트 시세 분석 대시보드")

# ----------------------------
# 사이드바: 지역 선택
# ----------------------------
st.sidebar.markdown("## 📌 지역 선택")
gu_multi = st.sidebar.multiselect("자치구 선택", sorted(data1['구'].unique()))

dong_multi = []
if gu_multi:
    dong_multi = st.sidebar.multiselect(
        "법정동 선택", 
        sorted(data1[data1['구'].isin(gu_multi)]['동'].unique())
    )

# ----------------------------
# 선택된 지역 필터링
# ----------------------------
if gu_multi and dong_multi:
    selected_df = data1[
        (data1['구'].isin(gu_multi)) & 
        (data1['동'].isin(dong_multi))
    ].copy()

    if selected_df.empty:
        st.warning("선택한 지역에 해당하는 데이터가 없습니다.")
    else:
        st.subheader("① 선택 지역의 평균가격 및 평당가격 추이 비교")

        # 지역명 다시 지정
        selected_df['지역'] = selected_df['구'] + " " + selected_df['동']
        selected_df = selected_df.sort_values(['지역', '연월_날짜'])

        # 평균가격(p1) 그래프
        fig1 = px.line(
            selected_df,
            x='연월_날짜',
            y='p1',
            color='지역',
            title="📊 평균가격(만원) 추이 비교",
            labels={'p1': '평균가격(만원)', '연월_날짜': '연월'}
        )
        fig1.update_layout(font=dict(family="Noto Sans KR, sans-serif"), xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

        # 평당가격(p2) 그래프
        fig2 = px.line(
            selected_df,
            x='연월_날짜',
            y='p2',
            color='지역',
            title="📊 평당가격(만원) 추이 비교",
            labels={'p2': '평당가격(만원)', '연월_날짜': '연월'}
        )
        fig2.update_layout(font=dict(family="Noto Sans KR, sans-serif"), xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("왼쪽에서 자치구와 법정동을 모두 선택하세요.")
