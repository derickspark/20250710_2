import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기
@st.cache_data
def load_data():
    data1 = pd.read_csv("data1.csv", dtype={'계약년월': str})
    data2 = pd.read_csv("data2.csv", dtype={'계약년월': str})
    return data1, data2

data1, data2 = load_data()

st.title("서울 아파트 시세 분석 대시보드")

# 사용자 입력 받기
gu_list = sorted(data1['구'].unique())
selected_gu = st.selectbox("자치구 선택", gu_list)

dong_list = sorted(data1[data1['구'] == selected_gu]['동'].unique())
selected_dong = st.selectbox("법정동 선택", dong_list)

# ① 해당 동의 평균가격 / 평당가격 (data1)
st.subheader("① 월별 평균가격 및 평당가격 (data1 기준)")
subset1 = data1[(data1['구'] == selected_gu) & (data1['동'] == selected_dong)].copy()
subset1 = subset1.sort_values('계약년월')
subset1['계약년월'] = subset1['계약년월'].astype(str)

st.dataframe(
    subset1[['계약년월', 'p1', 'p2']]
    .rename(columns={'p1': '평균가격(만원)', 'p2': '평당가격(만원)'})
    .style.format({'평균가격(만원)': '{:,.0f}', '평당가격(만원)': '{:,.0f}'})
)

# ② 최고/최저 단지 분석 (data2)
st.subheader("② 최고/최저 가격 단지 (data2 기준)")

subset2 = data2[(data2['구'] == selected_gu) & (data2['동'] == selected_dong)].copy()

if subset2.empty:
    st.warning("해당 지역에 대한 단지별 정보가 data2.csv에 없습니다.")
else:
    # 단지별 평균 계산
    grouped = subset2.groupby('단지명').agg(
        평균가격=('p1', 'mean'),
        평당가격=('p2', 'mean')
    ).reset_index()

    # 최고/최저 단지 찾기
    max_p1 = grouped.loc[grouped['평균가격'].idxmax()]
    min_p1 = grouped.loc[grouped['평균가격'].idxmin()]
    max_p2 = grouped.loc[grouped['평당가격'].idxmax()]
    min_p2 = grouped.loc[grouped['평당가격'].idxmin()]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("📈 **평균가격 최고/최저 단지**")
        st.write(f"최고가: {max_p1['단지명']} - {max_p1['평균가격']:.0f} 만원")
        st.write(f"최저가: {min_p1['단지명']} - {min_p1['평균가격']:.0f} 만원")

    with col2:
        st.markdown("🏢 **평당가격 최고/최저 단지**")
        st.write(f"최고가: {max_p2['단지명']} - {max_p2['평당가격']:.0f} 만원/평")
        st.write(f"최저가: {min_p2['단지명']} - {min_p2['평당가격']:.0f} 만원/평")

# ③ 평당가격 추이 비교 (그래프)
st.subheader("③ 선택 지역 vs 기타 지역 평당가격 추이")

# 지역 구분
data1['지역구분'] = data1.apply(
    lambda row: '선택지역' if (row['구'] == selected_gu and row['동'] == selected_dong) else '기타지역',
    axis=1
)

# 월별 평균 평당가격
trend = data1.groupby(['계약년월', '지역구분'])['p2'].mean().reset_index()

# 그래프
fig, ax = plt.subplots(figsize=(10, 5))
for name, group in trend.groupby('지역구분'):
    ax.plot(group['계약년월'], group['p2'], label=name)

ax.set_title(f"계약년월별 평당가격 추이: {selected_gu} {selected_dong} vs 기타지역")
ax.set_xlabel("계약년월")
ax.set_ylabel("평당 평균가격 (만원)")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)
