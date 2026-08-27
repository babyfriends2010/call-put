import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pykrx import stock as krx_stock
from datetime import datetime, timedelta

st.set_page_config(page_title="한국 주식 종합 대시보드", layout="wide")

st.title("🇰🇷 한국 주식 & 시장 종합 분석 대시보드")

# Tap 구성
tab1, tab2, tab3, tab4 = st.tabs(["📊 차트 & 기술적 지표", "🏦 외국인/기관 수급", "📑 재무 & 투자지표", "📈 코스피200 옵션 비율"])

# 공통 입력 항목 (sidebar)
st.sidebar.header("종목 설정")
ticker_input = st.sidebar.text_input("종목코드 (6자리)", "005930") # 예: 005930
today_str = datetime.today().strftime("%Y%m%d")
start_str = (datetime.today() - timedelta(days=180)).strftime("%Y%m%d")

yf_ticker = f"{ticker_input}.KS" # 기본 코스피 설정

# --- TAB 1: 차트 & 기술적 지표 (RSI, 이동평균선) ---
with tab1:
    st.subheader(f"📌 {ticker_input} 기술적 분석")
    try:
        df = yf.Ticker(yf_ticker).history(period="6mo")
        if not df.empty:
            # 이동평균선
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # RSI 계산
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # 주가 차트
            st.line_chart(df[['Close', 'MA20', 'MA60']])
            
            # RSI 차트
            st.subheader("📉 RSI (상대강도지수 - 70이상 과매수 / 30이하 과매도)")
            st.line_chart(df['RSI'])
        else:
            st.error("주가 데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

# --- TAB 2: 외국인 / 기관 매매동향 ---
with tab2:
    st.subheader(f"🏦 최근 외국인 / 기관 순매수 동향 (KRX)")
    try:
        net_df = krx_stock.get_market_trading_value_by_date(start_str, today_str, ticker_input)
        if not net_df.empty:
            recent_df = net_df[['기관합계', '외국인합계', '개인']].tail(20)
            st.bar_chart(recent_df)
            st.dataframe(recent_df.tail(10))
        else:
            st.warning("수급 데이터를 가져올 수 없습니다. (종목코드를 확인하세요)")
    except Exception as e:
        st.error(f"수급 데이터 조회 오류: {e}")

# --- TAB 3: 주요 재무제표 & 투자지표 ---
with tab3:
    st.subheader(f"📑 {ticker_input} 기업 밸류에이션 지표")
    try:
        info = yf.Ticker(yf_ticker).info
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("PER (배)", info.get('trailingPE', 'N/A'))
        col2.metric("PBR (배)", info.get('priceToBook', 'N/A'))
        col3.metric("ROE (%)", f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else 'N/A')
        col4.metric("배당수익률 (%)", f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A')
    except Exception as e:
        st.error(f"재무 정보 조회 오류: {e}")

# --- TAB 4: 국내 코스피200 옵션 시장 콜/풋 비율 ---
with tab4:
    st.subheader("📈 코스피200 옵션 거래비율 (풋/콜 Ratio)")
    try:
        # 코스피200 옵션 전체 거래실적
        opt_df = krx_stock.get_market_trading_value_by_investor_group(today_str, today_str, "OPT")
        if not opt_df.empty:
            st.dataframe(opt_df)
        else:
            st.info("오늘 옵션 시장 거래 데이터가 아직 집계되지 않았거나 장 시작 전입니다.")
    except Exception as e:
        st.info("장 시작 전이거나 옵션 거래 데이터를 불러오는 중입니다.")
