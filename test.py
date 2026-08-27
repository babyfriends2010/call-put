import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="국내주식 분석 대시보드", layout="wide")

st.title("🇰🇷 한국 주식 차트 & 분석 대시보드")
st.caption("코스피는 종목코드.KS (예: 005930.KS), 코스닥은 종목코드.KQ (예: 247540.KQ) 입력")

# 사용자 입력
code = st.text_input("종목코드 입력", "005930.KS").upper()
period = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

if st.button("주가 조회하기"):
    try:
        stock = yf.Ticker(code)
        df = stock.history(period=period)
        info = stock.info
        
        if df.empty:
            st.error("주가 데이터를 가져올 수 없습니다. 종목코드를 확인해 주세요.")
        else:
            # 기업 기본 정보 표시
            company_name = info.get('longName', code)
            st.subheader(f"📊 {company_name} ({code})")
            
            # 이동평균선 계산
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # 캔들스틱 차트 생성
            fig = go.Figure()
            
            # 주가 캔들 차트
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="주가"
            ))
            
            # 이동평균선 추가
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='20일 이동평균선', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], mode='lines', name='60일 이동평균선', line=dict(color='blue')))
            
            fig.update_layout(title="주가 추이 및 이동평균선", xaxis_title="날짜", yaxis_title="주가 (KRW)", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            # 거래량 차트
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], name="거래량", marker_color='gray'))
            fig_vol.update_layout(title="거래량 추이", xaxis_title="날짜", yaxis_title="거래량")
            st.plotly_chart(fig_vol, use_container_width=True)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
            fig = px.bar(df, x="유형", y="거래량", color="유형", 
                         color_discrete_map={"콜 옵션 (상승 베팅)": "green", "풋 옵션 (하락 베팅)": "red"})
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
