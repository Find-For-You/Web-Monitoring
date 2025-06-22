import streamlit as st

st.set_page_config(
    page_title="설정",
    page_icon="⚙️",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

st.title("⚙️ 시스템 설정")
st.write("이 페이지에서는 시스템 설정을 변경할 수 있습니다.")
