import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# -----------------------------
# 페이지 & 폰트(웹폰트) 세팅
# -----------------------------
st.set_page_config(page_title="월별 매출 대시보드", page_icon="📈", layout="wide")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"]  {
  font-family: 'Noto Sans KR', system-ui, -apple-system, Segoe UI, Roboto, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.title("⚙️ 설정")
uploaded = st.sidebar.file_uploader("CSV 업로드 (열: 월, 매출액, 전년동월, 증감률)", type=["csv"])

theme_choice = st.sidebar.selectbox("테마", ["Dark", "Light"], index=0)
smooth_line = st.sidebar.checkbox("라인 부드럽게(line_shape='spline')", value=True)
bar_width_pct = st.sidebar.slider("증감률 막대 너비(%)", 20, 100, 60, step=5)

st.sidebar.markdown("---")
st.sidebar.caption("• 업로드가 없으면 샘플 데이터로 시연합니다.")

# -----------------------------
# 데이터 로드
# -----------------------------
if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    df = pd.DataFrame({
        "월": ["2024-01","2024-02","2024-03","2024-04","2024-05","2024-06",
               "2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"],
        "매출액":   [12000000,13500000,11000000,18000000,21000000,19500000,
                   20000000,20500000,18500000,17500000,19000000,22000000],
        "전년동월": [10500000,11200000,12800000,15200000,18500000,18000000,
                   17000000,16000000,17500000,16500000,17200000,19000000],
        "증감률":   [14.3,20.5,-14.1,18.4,13.5,8.3,17.6,28.1,5.7,6.1,10.5,15.8],
    })

# 타입 정리 & 결측치 제거
for col in ["매출액", "전년동월", "증감률"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["월", "매출액", "전년동월", "증감률"]).reset_index(drop=True)

# 시리즈 준비
months = df["월"].astype(str).tolist()
sales = df["매출액"].astype(int).tolist()
last_year = df["전년동월"].astype(int).tolist()
yoy = df["증감률"].astype(float).tolist()

# -----------------------------
# KPI 계산
# -----------------------------
def krw(n: float) -> str:
    try:
        return f"{int(n):,}원"
    except Exception:
        return "-"

def pct(x: float) -> str:
    try:
        return f"{x:.1f}%"
    except Exception:
        return "-"

total_sales = sum(sales) if sales else 0
avg_yoy = sum(yoy) / len(yoy) if yoy else 0.0
imax = sales.index(max(sales)) if sales else 0
imin = sales.index(min(sales)) if s
