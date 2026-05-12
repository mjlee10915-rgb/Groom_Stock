import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

st.set_page_config(page_title="KOSPI 마켓 브레스", layout="wide")

st.title("📊 KOSPI 50일선 하회 종목 실시간 분석")
st.write("현재 코스피 종목 중 50일 이동평균선 아래에 있는 종목의 비율을 계산합니다.")

if st.button('데이터 분석 시작'):
    with st.spinner('데이터를 분석 중입니다... (약 1분 소요)'):
        # 1. KOSPI 종목 리스트 확보
        df_krx = fdr.StockListing('KOSPI')
        tickers = df_krx['Code'].tolist()
        
        progress_bar = st.progress(0)
        below_count = 0
        total = len(tickers)
        
        # 2. 분석 진행
        for i, ticker in enumerate(tickers):
            try:
                df = fdr.DataReader(ticker)
                if len(df) >= 50:
                    ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                    current = df['Close'].iloc[-1]
                    if current < ma50:
                        below_count += 1
            except:
                pass
            progress_bar.progress((i + 1) / total)

        # 3. 결과 화면 표시
        ratio = (below_count / total) * 100
        
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("전체 분석 종목 수", f"{total}개")
        col2.metric("50일선 하회 비율", f"{ratio:.1f}%", f"{below_count}개 종목", delta_color="inverse")
        
        if ratio > 70:
            st.warning("⚠️ 시장 하락세가 강해 과매도 구간(바닥권) 가능성이 있습니다.")
        elif ratio < 30:
            st.success("✅ 대부분의 종목이 정배열 상태인 강세장입니다.")
