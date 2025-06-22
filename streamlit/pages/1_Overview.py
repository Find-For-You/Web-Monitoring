import streamlit as st

st.set_page_config(
    page_title="시스템 개요",
    page_icon="📊",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

st.title("📊 시스템 개요")
st.write("이 페이지에서는 시스템의 전반적인 상태와 주요 지표를 확인할 수 있습니다.")
