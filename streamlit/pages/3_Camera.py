import streamlit as st
import time

# --- 페이지 설정 ---
st.set_page_config(page_title="카메라 피드", page_icon="📷", layout="wide")

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
    st.title("실시간 카메라 피드")
    st.caption("선택한 프로젝트의 로봇 카메라 피드를 실시간으로 확인합니다.")
with col2:
    st.selectbox("프로젝트 선택", options=st.session_state.projects, key='selected_project')
st.divider()

# --- 2. 카메라 피드 그리드 ---
st.subheader(f"'{st.session_state.selected_project}'의 카메라 피드")

# 로봇 목록 (임시 데이터)
robot_feeds = {
    "Robot 1": "https://i.imgur.com/g2g5n4m.png",
    "Robot 2": "https://i.imgur.com/uNf4T3a.png",
    "Leader Robot": "https://i.imgur.com/Ttcj3QV.png",
    "Robot Alpha": "https://i.imgur.com/g2g5n4m.png",
}

# 그리드 레이아웃 선택
grid_size = st.radio("레이아웃 선택", [1, 2, 4], index=1, horizontal=True)

if grid_size == 1:
    selected_robot = st.selectbox("표시할 로봇 선택", list(robot_feeds.keys()))
    st.image(robot_feeds[selected_robot], caption=f"{selected_robot} - 실시간 피드", use_column_width=True)

elif grid_size == 2:
    cols = st.columns(2)
    robot_list = list(robot_feeds.keys())
    for i, col in enumerate(cols):
        if i < len(robot_list):
            robot_name = robot_list[i]
            with col:
                st.image(robot_feeds[robot_name], caption=f"{robot_name} - 실시간 피드", use_column_width=True)

elif grid_size == 4:
    cols = st.columns(2)
    robot_list = list(robot_feeds.keys())
    for i in range(0, 4, 2):
        with cols[0]:
            if i < len(robot_list):
                robot_name = robot_list[i]
                st.image(robot_feeds[robot_name], caption=f"{robot_name} - 실시간 피드", use_column_width=True)
        with cols[1]:
            if i + 1 < len(robot_list):
                robot_name = robot_list[i+1]
                st.image(robot_feeds[robot_name], caption=f"{robot_name} - 실시간 피드", use_column_width=True)
