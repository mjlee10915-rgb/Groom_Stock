import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="KOSPI 마켓 브레스 히스토리", layout="wide")

st.title("📈 KOSPI 50일선 하회 비율 (1년 추이)")
st.write("시가총액 상위 종목들이 지난 1년간 50일선 아래에 머문 비율의 변화를 분석합니다.")

if st.button('1년 데이터 분석 시작'):
    with st.spinner('지난 1년치 데이터를 정밀 분석 중입니다...'):
        # 1. 시총 상위 100개 종목 리스트 (부하를 줄이기 위해 100개 권장)
        df_krx = fdr.StockListing('KOSPI').head(100)
        tickers = df_krx['Code'].tolist()
        
        # 모든 종목의 하회 여부를 저장할 데이터프레임
        history_df = pd.DataFrame()
        
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(tickers):
            try:
                # 종목별로 1.5년치 데이터를 한꺼번에 가져옴 (50일 MA 계산을 위해 넉넉히)
                df = fdr.DataReader(ticker)
                if len(df) > 60:
                    # 50일 이동평균선 계산
                    ma50 = df['Close'].rolling(window=50).mean()
                    # 하회 여부 체크 (하회하면 1, 아니면 0)
                    is_below = (df['Close'] < ma50).astype(int)
                    history_df[ticker] = is_below
            except:
                continue
            progress_bar.progress((i + 1) / len(tickers))

        # 2. 날짜별로 하회 종목 비율 계산
        # 전체 종목 중 1의 개수(하회 종목) 비중 계산
        ratio_series = history_df.mean(axis=1) * 100
        ratio_series = ratio_series.tail(252) # 최근 1년(약 252 거래일)만 추출

        # 3. 그래프 그리기 (Plotly 사용)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ratio_series.index, 
            y=ratio_series.values,
            mode='lines',
            name='50일선 하회 비율(%)',
            line=dict(color='red', width=2)
        ))

        fig.update_layout(
            title="KOSPI 상위 100종목 중 50일선 하회 비율 추이",
            xaxis_title="날짜",
            yaxis_title="하회 비율 (%)",
            yaxis=dict(range=[0, 100]),
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # 4. 요약 정보
        current_ratio = ratio_series.iloc[-1]
        st.subheader(f"현재 하회 비율: {current_ratio:.1f}%")
        st.write("- 비율이 **80% 이상**이면 시장이 극도로 위축된 **바닥권**일 가능성이 높습니다.")
        st.write("- 비율이 **20% 이하**이면 대부분의 종목이 달리는 **강세장**입니다.")
