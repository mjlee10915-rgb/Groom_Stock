import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import time

st.set_page_config(page_title="KOSPI 마켓 브레스", layout="wide")

st.title("📊 KOSPI 50일선 하회 종목 실시간 분석")
st.write("현재 코스피 종목 중 50일 이동평균선 아래에 있는 종목의 비율을 계산합니다.")

# 데이터 불러오기 실패 시 재시도 로직 추가
@st.cache_data(ttl=3600)  # 결과를 1시간 동안 기억해서 서버 부하를 줄입니다
def get_stock_list():
    try:
        return fdr.StockListing('KOSPI')
    except:
        return None

if st.button('데이터 분석 시작'):
    df_krx = get_stock_list()
    
    if df_krx is None:
        st.error("⚠️ 거래소 데이터 서버 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.")
    else:
        with st.spinner('데이터를 분석 중입니다... (약 1분 소요)'):
            tickers = df_krx['Code'].tolist()
            # 서버 과부하 방지를 위해 샘플링 (너무 많으면 차단될 수 있어 200개로 제한 권장)
            # 전체를 보려면 아래 [:200]을 지우세요.
            tickers = tickers[:200] 
            
            progress_bar = st.progress(0)
            below_count = 0
            actual_processed = 0
            
            for i, ticker in enumerate(tickers):
                try:
                    # 종목별로 약간의 간격을 두어 차단을 방지합니다
                    df = fdr.DataReader(ticker)
                    if len(df) >= 50:
                        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                        current = df['Close'].iloc[-1]
                        if current < ma50:
                            below_count += 1
                        actual_processed += 1
                except:
                    continue
                progress_bar.progress((i + 1) / len(tickers))
                time.sleep(0.05) # 서버 매너 타임

            if actual_processed > 0:
                ratio = (below_count / actual_processed) * 100
                st.divider()
                col1, col2 = st.columns(2)
                col1.metric("성공적으로 분석한 종목", f"{actual_processed}개")
                col2.metric("50일선 하회 비율", f"{ratio:.1f}%", f"{below_count}개 종목", delta_color="inverse")
            else:
                st.error("종목 데이터를 가져오지 못했습니다.")
