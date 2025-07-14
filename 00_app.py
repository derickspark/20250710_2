import streamlit as st
import pandas as pd

# 데이터 업로드
@st.cache_data
def load_data():
    df = pd.read_csv("seoul_apartment.csv")  # CSV 파일명은 예시입니다.
    df['거래월'] = pd.to_datetime(df['계약일']).dt.to_period('M').astype(str)
    return df

df = load_data()

# 필수 컬럼 예시 (이름은 사용자 CSV에 맞게 수정)
# ['자치구', '법정동', '단지명', '전용면적', '거래금액', '계약일']

st.title("서울 아파트 매매 시세 분석 (2024.01~2025.06)")

# ----------------------------
# 1. 지역별 평균 가격 및 평당가
# ----------------------------
st.header("① 지역별 평균 가격 및 평당가격")

tab1, tab2 = st.tabs(["구별", "동별"])

with tab1:
    df_gu = df.copy()
    df_gu['거래금액'] = df_gu['거래금액'].str.replace(",", "").astype(int)
    df_gu['평당가'] = df_gu['거래금액'] / df_gu['전용면적']

    gu_group = df_gu.groupby('자치구').agg(
        평균_거래금액=('거래금액', 'mean'),
        평균_평당가격=('평당가', 'mean')
    ).reset_index()

    st.dataframe(gu_group.style.format({'평균_거래금액': '{:,.0f}만원', '평균_평당가격': '{:,.0f}만원'}))

with tab2:
    df_dong = df.copy()
    df_dong['거래금액'] = df_dong['거래금액'].str.replace(",", "").astype(int)
    df_dong['평당가'] = df_dong['거래금액'] / df_dong['전용면적']

    dong_group = df_dong.groupby(['자치구', '법정동']).agg(
        평균_거래금액=('거래금액', 'mean'),
        평균_평당가격=('평당가', 'mean')
    ).reset_index()

    st.dataframe(dong_group.style.format({'평균_거래금액': '{:,.0f}만원', '평균_평당가격': '{:,.0f}만원'}))

# ----------------------------
# 2. 선택한 구별 월별 최고가/최저가 단지
# ----------------------------
st.header("② 월별 최고가/최저가 아파트 단지 (선택한 구 기준)")

selected_gu = st.selectbox("자치구 선택", sorted(df['자치구'].unique()))

df_sel = df[df['자치구'] == selected_gu].copy()
df_sel['거래금액'] = df_sel['거래금액'].str.replace(",", "").astype(int)
df_sel['거래월'] = pd.to_datetime(df_sel['계약일']).dt.to_period('M').astype(str)

grouped = df_sel.groupby(['거래월'])

high_list = []
low_list = []

for name, group in grouped:
    idx_max = group['거래금액'].idxmax()
    idx_min = group['거래금액'].idxmin()
    high_list.append(group.loc[idx_max])
    low_list.append(group.loc[idx_min])

df_high = pd.DataFrame(high_list)[['거래월', '단지명', '전용면적', '거래금액', '법정동']]
df_low = pd.DataFrame(low_list)[['거래월', '단지명', '전용면적', '거래금액', '법정동']]

st.subheader("📈 월별 최고가 단지")
st.dataframe(df_high.sort_values('거래월'))

st.subheader("📉 월별 최저가 단지")
st.dataframe(df_low.sort_values('거래월'))
