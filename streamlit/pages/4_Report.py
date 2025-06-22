import streamlit as st

st.set_page_config(
    page_title="분석 보고서",
    page_icon="📄",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

st.title("📄 분석 보고서")
st.write("이 페이지에서는 탐사 데이터 분석 보고서를 생성하고 확인할 수 있습니다.")
