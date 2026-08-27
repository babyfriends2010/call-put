import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="옵션 플로우 대시보드", layout="wide")

st.title("📈 미국주식 옵션 플로우 (무료 데이터)")
ticker = st.text_input("종목 티커 입력 (예: AMD, NVDA, TSLA)", "AMD").upper()

if st.button("조회하기"):
    try:
        stock = yf.Ticker(ticker)
        expiries = stock.options
        
        if not expiries:
            st.error("옵션 데이터를 찾을 수 없습니다.")
        else:
            selected_expiry = expiries[0]
            chain = stock.option_chain(selected_expiry)
            
            calls = chain.calls
            puts = chain.puts
            
            call_vol = calls['volume'].sum()
            put_vol = puts['volume'].sum()
            
            sentiment = "Bullish (상승 우세 🟢)" if call_vol > put_vol else "Bearish (하락 우세 🔴)"
            
            st.subheader(f"[{ticker}] 만기일: {selected_expiry} 기준")
            st.metric("종합 판정", sentiment)
            
            df = pd.DataFrame({
                "유형": ["콜 옵션 (상승 베팅)", "풋 옵션 (하락 베팅)"],
                "거래량": [call_vol, put_vol]
            })
            fig = px.bar(df, x="유형", y="거래량", color="유형", 
                         color_discrete_map={"콜 옵션 (상승 베팅)": "green", "풋 옵션 (하락 베팅)": "red"})
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
