import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="한국 주식 차트 대시보드", layout="wide")

st.title("🇰🇷 한국 주식 차트 & 분석 대시보드")
st.caption("코스피: 종목코드.KS (예: 005930.KS) / 코스닥: 종목코드.KQ (예: 247540.KQ)")

code = st.text_input("종목코드 입력", "005930.KS").upper()
period = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

if st.button("주가 조회하기"):
    try:
        stock = yf.Ticker(code)
        df = stock.history(period=period)
        
        if df.empty:
            st.error("주가 데이터를 가져올 수 없습니다. 종목코드를 확인해 주세요.")
        else:
            st.subheader(f"📊 {code} 주가 추이")
            
            # 이동평균선 계산
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # 주가 및 이동평균선 차트
            st.line_chart(df[['Close', 'MA20', 'MA60']])
            
            # 거래량 차트
            st.subheader("📈 거래량 추이")
            st.bar_chart(df['Volume'])

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
