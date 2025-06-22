import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="분석 보고서", page_icon="📄", layout="wide")

# --- 사이드바 ---
with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

# --- 전역 상태 초기화 ---
if 'projects' not in st.session_state:
    st.session_state.projects = ["My Project 1", "temp proj 4", "temp proj", "wefwd", "yje"]
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = st.session_state.projects[0]

# --- 1. 상단: 제목 및 프로젝트 선택 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("분석 보고서")
    st.caption("탐사 데이터를 기반으로 상세 분석 보고서를 생성하고 확인합니다.")
with col2:
    st.selectbox("프로젝트 선택", options=st.session_state.projects, key='selected_project')
st.divider()

# --- 2. 보고서 생성 옵션 ---
with st.container(border=True):
    st.subheader("보고서 생성 옵션")
    col1, col2, col3 = st.columns(3)
    with col1:
        date_range = st.date_input(
            "기간 선택",
            (datetime.now() - timedelta(days=7), datetime.now()),
            format="YYYY-MM-DD"
        )
    with col2:
        robots = st.multiselect("로봇 선택", ["Robot 1", "Robot 2", "Leader Robot"], default=["Robot 1"])
    with col3:
        report_type = st.selectbox("보고서 유형", ["종합 보고서", "이상 감지 요약", "센서 데이터 상세"])
    
    if st.button("보고서 생성", type="primary"):
        st.session_state.report_generated = True
        st.session_state.report_data = {
            "date_range": date_range,
            "robots": robots,
            "report_type": report_type
        }

st.divider()

# --- 3. 보고서 표시 ---
if st.session_state.get("report_generated"):
    data = st.session_state.report_data
    with st.container(border=True):
        st.header(f"{data['report_type']} ({data['date_range'][0].strftime('%Y-%m-%d')} ~ {data['date_range'][1].strftime('%Y-%m-%d')})")
        st.subheader("개요")
        st.write(f"선택된 로봇: {', '.join(data['robots'])}")
        st.write("이 기간 동안 총 5건의 주요 이벤트가 감지되었으며, 평균 배터리 소모량은 35%입니다.")

        st.subheader("탐사 경로 및 주요 이벤트")
        st.image("https://i.imgur.com/uNf4T3a.png", caption="종합 탐사 경로")

        st.subheader("센서 데이터 분석 (온도)")
        chart_data = pd.DataFrame(
            np.random.randn(20, len(data['robots'])),
            columns=data['robots']
        )
        st.line_chart(chart_data)

        st.subheader("상세 데이터 로그")
        df = pd.DataFrame(
            np.random.randn(10, 5),
            columns=('col %d' % i for i in range(5))
        )
        st.dataframe(df)

        # 다운로드 버튼 (실제 파일 생성 로직 필요)
        st.download_button(
           "보고서 다운로드 (PDF)",
           data="This is a dummy PDF content.",
           file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
           mime="application/pdf",
        )
