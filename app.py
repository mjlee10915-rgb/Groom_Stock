import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

st.set_page_config(page_title="KOSPI 마켓 브레스", layout="wide")

st.title("📊 KOSPI 50일선 하회 종목 분석")
st.write("현재 코스피 종목들의 위치를 분석합니다.")

# 데이터를 안전하게 가져오는 함수
def get_data():
    try:
        # 종목 리스트를 먼저 가져옵니다
        df_krx = fdr.StockListing('KOSPI')
        return df_krx
    except:
        return None

if st.button('데이터 분석 시작'):
    df_krx = get_data()
    
    if df_krx is None:
        st.error("⚠️ 현재 거래소 데이터에 접근할 수 없습니다. 잠시 후 다시 시도해주세요.")
    else:
        with st.spinner('시장의 숨겨진 수치를 계산 중...'):
            # 분석 속도를 위해 시가총액 상위 200개 종목만 우선 분석 (차단 방지)
            tickers = df_krx.head(200)
            
            progress_bar = st.progress(0)
            below_count = 0
            success_count = 0
            
            for i, row in tickers.iterrows():
                try:
                    # 각 종목의 최근 주가 데이터 100일치만 가져오기 (부하 감소)
                    df = fdr.DataReader(row['Code'])
                    if len(df) >= 50:
                        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
                        current_price = df['Close'].iloc[-1]
                        
                        if current_price < ma50:
                            below_count += 1
                        success_count += 1
                except:
                    continue
                progress_bar.progress((i + 1) / len(tickers))

            if success_count > 0:
                ratio = (below_count / success_count) * 100
                st.divider()
                c1, c2, c3 = st.columns(3)
                c1.metric("분석 종목 (상위)", f"{success_count}개")
                c2.metric("50일선 하회", f"{below_count}개")
                c3.metric("하회 비율", f"{ratio:.1f}%", delta_color="inverse")
                
                st.info(f"현재 시총 상위 200대 종목 중 {ratio:.1f}%가 50일 이동평균선 아래에 있습니다.")
            else:
                st.error("데이터를 분석하는 과정에서 오류가 발생했습니다.")
