import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

st.set_page_config(
    page_title="월별 매출 대시보드",
    page_icon="📈",
    layout="wide",
)

# -------------------------------------
# 사이드바: 데이터 업로드 & 옵션
# -------------------------------------
st.sidebar.title("⚙️ 설정")
uploaded = st.sidebar.file_uploader("CSV 업로드 (열: 월, 매출액, 전년동월, 증감률)", type=["csv"])

theme_choice = st.sidebar.selectbox("테마", ["Dark", "Light"], index=0)
bar_width = st.sidebar.slider("증감률 막대 너비(%)", 20, 100, 60, step=5)
smooth_line = st.sidebar.checkbox("라인 부드럽게(smooth)", value=True)

st.sidebar.markdown("---")
st.sidebar.caption("• 업로드가 없으면 샘플 데이터로 시연합니다.")

# -------------------------------------
# 데이터 로드
# -------------------------------------
if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    # 샘플 데이터 (원하시면 여기만 교체하면 됨)
    df = pd.DataFrame({
        "월": ["2024-01","2024-02","2024-03","2024-04","2024-05","2024-06",
               "2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"],
        "매출액": [12000000,13500000,11000000,18000000,21000000,19500000,
                 20000000,20500000,18500000,17500000,19000000,22000000],
        "전년동월": [10500000,11200000,12800000,15200000,18500000,18000000,
                  17000000,16000000,17500000,16500000,17200000,19000000],
        "증감률": [14.3,20.5,-14.1,18.4,13.5,8.3,17.6,28.1,5.7,6.1,10.5,15.8],
    })

# 타입 정리
for col in ["매출액", "전년동월", "증감률"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 결측치 제거
df = df.dropna(subset=["월", "매출액", "전년동월", "증감률"]).reset_index(drop=True)

# -------------------------------------
# KPI 계산
# -------------------------------------
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

months = df["월"].astype(str).tolist()
sales = df["매출액"].astype(int).tolist()
last_year = df["전년동월"].astype(int).tolist()
yoy = df["증감률"].astype(float).tolist()

total_sales = sum(sales) if sales else 0
avg_yoy = sum(yoy) / len(yoy) if yoy else 0.0

imax = sales.index(max(sales)) if sales else 0
imin = sales.index(min(sales)) if sales else 0
max_month, max_value = (months[imax], sales[imax]) if sales else ("-", 0)
min_month, min_value = (months[imin], sales[imin]) if sales else ("-", 0)

# -------------------------------------
# 헤더
# -------------------------------------
st.title("월별 매출 대시보드")
st.caption("최근 12개월 매출 추이와 전년동월 대비 변화를 한눈에 확인하세요.")

# -------------------------------------
# KPI 카드
# -------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("총매출", krw(total_sales), help="표시된 기간의 합계")
k2.metric("평균 증감률(YoY)", pct(avg_yoy), delta=f"{'상승' if avg_yoy>=0 else '하락'} 추세")
k3.metric("최고 매출 월", f"{max_month} · {krw(max_value)}")
k4.metric("최저 매출 월", f"{min_month} · {krw(min_value)}")

# -------------------------------------
# ECharts 색상/테마 프리셋
# -------------------------------------
dark = theme_choice == "Dark"
axis_text = "#cfd6ff" if dark else "#334155"
grid_line = "rgba(255,255,255,0.1)" if dark else "rgba(0,0,0,0.08)"
accent = "#7aa2ff"
accent2 = "#74e0c0"
accent3 = "#ffd166"

# -------------------------------------
# 라인 차트 (매출액 vs 전년동월)
# -------------------------------------
st.subheader("매출액 vs 전년동월")
line_options = {
    "backgroundColor": "transparent",
    "tooltip": {
        "trigger": "axis",
        "valueFormatter": "function (v) { return v.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',') + '원'; }",
    },
    "legend": {
        "data": ["매출액", "전년동월"],
        "top": 8,
        "textStyle": {"color": axis_text},
    },
    "grid": {"left": 48, "right": 24, "top": 48, "bottom": 32},
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "data": months,
        "axisLine": {"lineStyle": {"color": "#405085" if dark else "#CBD5E1"}},
        "axisLabel": {"color": axis_text},
    },
    "yAxis": {
        "type": "value",
        "axisLabel": {
            "color": axis_text,
            "formatter": "function (v) { return (v/1000000) + '백만원'; }",
        },
        "splitLine": {"lineStyle": {"color": grid_line}},
    },
    "dataZoom": [
        {"type": "slider", "height": 16, "bottom": 0, "borderColor": "#2a3560" if dark else "#CBD5E1",
         "handleIcon": "M0,0 L1,0 L1,1 L0,1 z"}
    ],
    "series": [
        {
            "name": "매출액",
            "type": "line",
            "smooth": smooth_line,
            "symbol": "circle",
            "symbolSize": 8,
            "itemStyle": {"color": accent},
            "lineStyle": {"width": 3, "color": accent},
            "areaStyle": {"color": "rgba(122,162,255,0.15)" if dark else "rgba(122,162,255,0.10)"},
            "data": sales,
        },
        {
            "name": "전년동월",
            "type": "line",
            "smooth": smooth_line,
            "symbol": "circle",
            "symbolSize": 8,
            "itemStyle": {"color": accent2},
            "lineStyle": {"width": 3, "color": accent2, "type": "dashed"},
            "data": last_year,
        },
    ],
}
st_echarts(options=line_options, height="420px", theme="dark" if dark else "light")

# -------------------------------------
# 증감률 바 차트
# -------------------------------------
st.subheader("전년동월 대비 증감률(%)")
bar_options = {
    "backgroundColor": "transparent",
    "tooltip": {"trigger": "axis", "valueFormatter": "function (v) { return v.toFixed(1) + '%'; }"},
    "legend": {"data": ["증감률"], "top": 8, "textStyle": {"color": axis_text}},
    "grid": {"left": 48, "right": 24, "top": 48, "bottom": 32},
    "xAxis": {
        "type": "category",
        "data": months,
        "axisLine": {"lineStyle": {"color": "#405085" if dark else "#CBD5E1"}},
        "axisLabel": {"color": axis_text},
    },
    "yAxis": {
        "type": "value",
        "axisLabel": {"color": axis_text, "formatter": "function (v) { return v + '%'; }"},
        "splitLine": {"lineStyle": {"color": grid_line}},
    },
    "series": [
        {
            "name": "증감률",
            "type": "bar",
            "barWidth": f"{bar_width}%",
            "itemStyle": {
                "color": {
                    "type": "function",
                    "function": """
                        function (params) {
                          const val = params.data;
                          return val >= 0 ? '#74e0c0' : '#ff6689';
                        }
                    """,
                }
            },
            "data": yoy,
        }
    ],
}
st_echarts(options=bar_options, height="380px", theme="dark" if dark else "light")

# -------------------------------------
# 데이터 테이블
# -------------------------------------
st.subheader("원본 데이터")
show_index = st.checkbox("인덱스 표시", value=False)
st.dataframe(df, use_container_width=True, hide_index=not show_index)

# -------------------------------------
# 다운로드 (CSV)
# -------------------------------------
csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 현재 데이터 CSV 다운로드",
    data=csv_bytes,
    file_name="월별_매출_데이터.csv",
    mime="text/csv",
)
