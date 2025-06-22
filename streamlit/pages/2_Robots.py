import streamlit as st

st.set_page_config(
    page_title="로봇 상태",
    page_icon="🤖",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

st.title("🤖 로봇 상태")
st.write("이 페이지에서는 각 로봇의 현재 상태와 임무 데이터를 확인할 수 있습니다.")
