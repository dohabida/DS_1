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
imin = sales.index(min(sales)) if sales else 0
max_month, max_value = (months[imax], sales[imax]) if sales else ("-", 0)
min_month, min_value = (months[imin], sales[imin]) if sales else ("-", 0)

# -----------------------------
# 헤더 & KPI
# -----------------------------
st.title("월별 매출 대시보드 (Plotly/Streamlit)")
st.caption("최근 12개월 매출 추이와 전년동월 대비 변화를 한눈에 확인하세요.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("총매출", krw(total_sales), help="표시된 기간 합계")
k2.metric("평균 증감률(YoY)", pct(avg_yoy), delta=f"{'상승' if avg_yoy>=0 else '하락'} 추세")
k3.metric("최고 매출 월", f"{max_month} · {krw(max_value)}")
k4.metric("최저 매출 월", f"{min_month} · {krw(min_value)}")

# -----------------------------
# Plotly 테마/색상
# -----------------------------
is_dark = (theme_choice == "Dark")
template = "plotly_dark" if is_dark else "plotly_white"
axis_color = "#cfd6ff" if is_dark else "#334155"
accent = "#7aa2ff"
accent2 = "#74e0c0"

# -----------------------------
# 1) 라인 차트 (매출액 vs 전년동월)
# -----------------------------
st.subheader("매출액 vs 전년동월")
line_shape = "spline" if smooth_line else "linear"

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=months, y=sales, mode="lines+markers", name="매출액",
    line=dict(width=3, color=accent, shape=line_shape),
    marker=dict(size=8)
))
fig_line.add_trace(go.Scatter(
    x=months, y=last_year, mode="lines+markers", name="전년동월",
    line=dict(width=3, color=accent2, dash="dash", shape=line_shape),
    marker=dict(size=8)
))
fig_line.update_layout(
    template=template,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis_title="금액 (원)",
    xaxis_title="월",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    font=dict(family="Noto Sans KR"),
    hovermode="x unified",
)
# y축 라벨을 '백만원' 단위 안내 텍스트로 대체하고, 호버에는 원 단위 표시
fig_line.update_yaxes(tickformat=",", title="금액 (원) · 호버로 확인")
st.plotly_chart(fig_line, use_container_width=True, height=420)

# -----------------------------
# 2) 증감률 바 차트
# -----------------------------
st.subheader("전년동월 대비 증감률(%)")
colors = ["#74e0c0" if v >= 0 else "#ff6689" for v in yoy]
# bar_width_pct는 trace에 직접 퍼센트로 주지 못하므로 layout의 bargap으로 조정(0=가득, 0.5=얇음)
# 막대가 넓을수록 bargap을 줄인다.
bargap = max(0.0, min(0.5, (100 - bar_width_pct) / 200))  # 0~0.5

fig_bar = go.Figure(data=[go.Bar(
    x=months, y=yoy, name="증감률", marker_color=colors, hovertemplate="%{y:.1f}%<extra></extra>"
)])
fig_bar.update_layout(
    template=template,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis_title="증감률 (%)",
    xaxis_title="월",
    bargap=bargap,
    font=dict(family="Noto Sans KR"),
)
st.plotly_chart(fig_bar, use_container_width=True, height=380)

# -----------------------------
# 데이터 테이블 & 다운로드
# -----------------------------
st.subheader("원본 데이터")
show_index = st.checkbox("인덱스 표시", value=False)
st.dataframe(df, use_container_width=True, hide_index=not show_index)

csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 현재 데이터 CSV 다운로드",
    data=csv_bytes,
    file_name="월별_매출_데이터.csv",
    mime="text/csv",
)
