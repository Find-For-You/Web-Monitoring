import streamlit as st

st.set_page_config(
    page_title="카메라 피드",
    page_icon="📷",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

st.title("📷 실시간 카메라 피드")
st.write("이 페이지에서는 로봇의 실시간 카메라 피드를 확인할 수 있습니다.")
