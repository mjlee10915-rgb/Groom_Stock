import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="국내시장 마켓 브레스", layout="wide")

st.title("📊 국내시장 마켓 브레스 & 지수 비교 분석")
st.write("50일선 하회 비율과 실제 지수 주가를 비교하여 시장의 위치를 파악합니다.")

# 사이드바 설정
market_type = st.sidebar.selectbox("분석할 시장을 선택하세요", ["KOSPI", "KOSDAQ"])
num_stocks = st.sidebar.slider("분석 종목 수 (상위순)", 50, 300, 300)

if st.button(f'{market_type} 데이터 분석 및 지수 비교 시작'):
    with st.spinner('데이터 분석 및 지수 데이터를 가져오는 중...'):
        try:
            # 1. 지수 데이터 가져오기
            market_code = 'KS11' if market_type == 'KOSPI' else 'KQ11'
            df_index = fdr.DataReader(market_code).tail(252)

            # 2. 개별 종목 분석
            df_list = fdr.StockListing(market_type).head(num_stocks)
            tickers = df_list['Code'].tolist()
            names = df_list['Name'].tolist()
            
            history_df = pd.DataFrame()
            progress_bar = st.progress(0)
            
            for i, (ticker, name) in enumerate(zip(tickers, names)):
                try:
                    df = fdr.DataReader(ticker).tail(300)
                    if len(df) > 50:
                        ma50 = df['Close'].rolling(window=50).mean()
                        is_below = (df['Close'] < ma50).astype(int)
                        history_df[name] = is_below
                except:
                    continue
                progress_bar.progress((i + 1) / len(tickers))

            if not history_df.empty:
                # 3. 비율 계산
                ratio_series = history_df.mean(axis=1) * 100
                ratio_series = ratio_series.tail(252)

                # 4. 이중 축 그래프 생성
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # 하회 비율 차트 - 왼쪽 축
                fig.add_trace(
                    go.Scatter(x=ratio_series.index, y=ratio_series.values, 
                               name="50일선 하회 비율(%)", line=dict(color='rgba(255, 0, 0, 0.6)', width=2)),
                    secondary_y=False,
                )

                # 실제 지수 차트 - 오른쪽 축
                fig.add_trace(
                    go.Scatter(x=df_index.index, y=df_index['Close'], 
                               name=f"{market_type} 지수", line=dict(color='royalblue', width=2)),
                    secondary_y=True,
                )

                # 기준선 추가
                fig.add_hline(y=80, line_dash="dash", line_color="orange", secondary_y=False)
                fig.add_hline(y=20, line_dash="dash", line_color="green", secondary_y=False)

                fig.update_layout(
                    title=f"<b>{market_type}</b> 하회 비율 vs 지수 주가 비교 (1년)",
                    xaxis_title="날짜",
                    template="plotly_white",
                    hovermode="x unified"
                )

                fig.update_yaxes(title_text="하회 비율 (%)", range=[0, 100], secondary_y=False)
                fig.update_yaxes(title_text=f"{market_type} 지수 (Point)", secondary_y=True)

                st.plotly_chart(fig, use_container_width=True)
                
                st.info(f"💡 현재 {market_type} 지수: {df_index['Close'].iloc[-1]:,.2f}pt / 하회 비율: {ratio_series.iloc[-1]:.1f}%")
            else:
                st.error("분석 데이터를 가져오지 못했습니다.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
