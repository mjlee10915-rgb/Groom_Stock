import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="국내시장 마켓 브레스", layout="wide")

st.title("📊 국내시장 50일선 하회 비율 분석 (1년 추이)")
st.write("시가총액 상위 종목들을 기준으로 시장의 과열 및 공포 구간을 분석합니다.")

# 사이드바 설정
market_type = st.sidebar.selectbox("분석할 시장을 선택하세요", ["KOSPI", "KOSDAQ"])
num_stocks = st.sidebar.slider("분석 종목 수 (상위순)", 50, 300, 300)

if st.button(f'{market_type} 상위 {num_stocks}개 데이터 분석 시작'):
    with st.spinner(f'{market_type} 데이터를 정밀 분석 중입니다... (약 1~2분 소요)'):
        # 1. 종목 리스트 확보
        try:
            df_list = fdr.StockListing(market_type).head(num_stocks)
            tickers = df_list['Code'].tolist()
            names = df_list['Name'].tolist()
            
            history_df = pd.DataFrame()
            progress_bar = st.progress(0)
            
            # 2. 데이터 수집 및 계산
            for i, (ticker, name) in enumerate(zip(tickers, names)):
                try:
                    df = fdr.DataReader(ticker)
                    if len(df) > 60:
                        ma50 = df['Close'].rolling(window=50).mean()
                        is_below = (df['Close'] < ma50).astype(int)
                        history_df[name] = is_below
                except:
                    continue
                progress_bar.progress((i + 1) / len(tickers))

            if not history_df.empty:
                # 3. 날짜별 하회 비율 계산
                ratio_series = history_df.mean(axis=1) * 100
                ratio_series = ratio_series.tail(252) # 최근 1년치

                # 4. 그래프 시각화
                fig = go.Figure()
                fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="공포 (바닥권)")
                fig.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="환희 (고점주의)")

                fig.add_trace(go.Scatter(
                    x=ratio_series.index, 
                    y=ratio_series.values,
                    mode='lines',
                    name=f'{market_type} 50일선 하회 비율',
                    line=dict(color='royalblue', width=2)
                ))

                fig.update_layout(
                    title=f"{market_type} 상위 {num_stocks}종목 50일선 하회 비율 추이 (1년)",
                    xaxis_title="날짜", yaxis_title="하회 비율 (%)",
                    yaxis=dict(range=[0, 100]),
                    template="plotly_white", hovermode="x unified"
                )

                st.plotly_chart(fig, use_container_width=True)
                
                # 5. 현재 상태 요약
                curr_val = ratio_series.iloc[-1]
                st.subheader(f"📍 현재 {market_type} 하회 비율: {curr_val:.1f}%")
                
                c1, c2, c3 = st.columns(3)
                c1.info("**20% 이하 (강세)**\n대부분 상승세입니다.")
                c2.info("**50% 내외 (중립)**\n방향 탐색 구간입니다.")
                c3.info("**80% 이상 (약세
