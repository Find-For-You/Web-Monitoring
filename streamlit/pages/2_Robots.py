import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(
    page_title="로봇 상태",
    page_icon="🤖",
    layout="wide"
)

# --- 사이드바 ---
with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

# --- 전역 상태 초기화 (Overview 페이지와 동기화) ---
if 'projects' not in st.session_state:
    st.session_state.projects = ["My Project 1", "temp proj 4", "temp proj", "wefwd", "yje"]
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = st.session_state.projects[0]

# --- 1. 상단: 제목 및 프로젝트 선택 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Robots")
    st.caption("프로젝트에 사용되는 로봇들을 한 눈에 확인하세요.")
with col2:
    st.selectbox(
        "프로젝트 선택",
        options=st.session_state.projects,
        key='selected_project'
    )
st.divider()

# --- 2. 로봇 리스트 ---
st.subheader(f"'{st.session_state.selected_project}'의 로봇 현황")
cols = st.columns(6)
robot_names = ["Robot 1", "Leader Robot", "You can", "change name", "like this"]
robot_values = ["24", "14", "87", "72", "43"]

# 첫 번째 메트릭 카드 (녹색 배경)
with cols[0]:
    st.markdown("""
    <div style="background-color: #2E7D32; border-radius: 10px; padding: 1rem; color: white; height: 135px;">
        <p style="font-size: 0.9rem; color: white;">Robot 1 ✏️</p>
        <p style="font-size: 2.5rem; font-weight: bold;">24 <span style="font-size: 1.5rem;">%</span></p>
    </div>
    """, unsafe_allow_html=True)

# 나머지 메트릭 카드
for i, col in enumerate(cols[1:-1]):
    with col:
        st.metric(f"{robot_names[i+1]} ✏️", f"{robot_values[i+1]} %")

# 로봇 추가 버튼
with cols[-1]:
    st.button("➕", use_container_width=True, help="새 로봇 추가")

st.divider()

# --- 3. 메인 콘텐츠: 지도 및 상세 정보 ---
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    with st.container(border=True):
        st.subheader("Maps")
        st.image("https://i.imgur.com/Ttcj3QV.png", use_column_width=True)

with col2:
    # 수동 조작
    with st.container(border=True):
        st.subheader("수동 조작")
        st.button("⬆️", use_container_width=True, key="joy_up")
        st.button("⬇️", use_container_width=True, key="joy_down")
        l, c, r = st.columns(3)
        l.button("⬅️", use_container_width=True, key="joy_left")
        c.button("⏹️", use_container_width=True, key="joy_stop")
        r.button("➡️", use_container_width=True, key="joy_right")

    # 센서 정보
    with st.container(border=True):
        st.subheader("Sensor")
        st.metric("🌡️ Temperature", "23 °C")
        st.metric("💧 Humidity", "53 %")

    # 배터리 & 속도
    with st.container(border=True):
        st.subheader("Battery & Velocity")
        st.metric("Battery", "24 %")
        st.metric("Velocity", "8 cm/s")

    # 연결 상태
    with st.container(border=True):
        st.subheader("Connection")
        st.metric("Mbps", "17")
        st.metric("ms", "153")
