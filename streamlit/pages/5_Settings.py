import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(page_title="설정", page_icon="⚙️", layout="wide")

# --- 사이드바 ---
with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

# --- 1. 상단: 제목 ---
st.title("시스템 설정")
st.caption("시스템의 동작 및 계정 정보를 설정합니다.")
st.divider()

# --- 2. 설정 탭 ---
tab1, tab2, tab3 = st.tabs(["일반 설정", "로봇 설정", "계정 설정"])

with tab1:
    st.header("일반 설정")
    with st.container(border=True):
        st.subheader("테마 및 언어")
        st.radio("테마 선택", ["시스템 기본값", "라이트 모드", "다크 모드"], horizontal=True)
        st.selectbox("언어 선택", ["한국어", "English"])
    
    with st.container(border=True):
        st.subheader("알림 설정")
        st.write("주요 이벤트 발생 시 알림을 받을 방법을 선택하세요.")
        st.checkbox("이메일 알림 받기")
        st.checkbox("앱 내 푸시 알림 받기")

with tab2:
    st.header("로봇 설정")
    with st.container(border=True):
        st.subheader("기본 임무 파라미터")
        st.slider("안전 복귀 배터리 임계값 (%)", 20, 50, 30)
        st.selectbox("연결 두절 시 동작", ["가장 가까운 기지로 복귀", "현재 위치에서 대기", "탐사 중단 및 경고"])
        st.number_input("최대 탐사 시간 (분)", min_value=30, max_value=300, value=120, step=10)

with tab3:
    st.header("계정 설정")
    with st.container(border=True):
        st.subheader("내 정보")
        st.text_input("이름", "Nekeworld")
        st.text_input("이메일", "chrisabc94@gmail.com", disabled=True)
        if st.button("프로필 업데이트"):
            st.toast("프로필 정보가 업데이트되었습니다.")

    with st.container(border=True):
        st.subheader("비밀번호 변경")
        st.password_input("현재 비밀번호")
        st.password_input("새 비밀번호")
        st.password_input("새 비밀번호 확인")
        if st.button("비밀번호 변경"):
            st.toast("비밀번호가 성공적으로 변경되었습니다.", icon="🎉")

st.divider()
if st.button("모든 설정 저장", type="primary"):
    st.toast("모든 설정이 저장되었습니다.", icon="✅")
