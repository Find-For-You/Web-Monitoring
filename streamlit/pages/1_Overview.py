import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="시스템 개요",
    page_icon="📊",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

# --- 전역 상태 초기화 ---
# 프로젝트 목록
if 'projects' not in st.session_state:
    st.session_state.projects = ["My Project 1", "temp proj 4", "temp proj", "wefwd", "yje"]
# 선택된 프로젝트
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = st.session_state.projects[0]

# 팀원 목록
if 'team_members' not in st.session_state:
    st.session_state.team_members = [
        {"name": "Nekeworld", "email": "chrisabc94@gmail.com"},
        {"name": "example1", "email": "ex1@gmail.com"},
        {"name": "example2", "email": "ex2@gmail.com"},
    ]


# --- 1. 상단: 제목 및 프로젝트 선택 ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Overview")
    st.caption("프로젝트를 관리하고, 필요한 정보에 빠르게 접근하세요.")

with col2:
    st.selectbox(
        "프로젝트 선택",
        options=st.session_state.projects,
        key='selected_project' # selectbox의 상태를 session_state와 연결
    )

st.divider()

# --- 2. 중단: 그래프, 로봇, 알림 ---
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    with st.container(border=True):
        st.subheader("탐사 면적")
        chart_data = pd.DataFrame(
            np.random.rand(10, 1) * 20 + 20,
            columns=['면적(m²)']
        )
        st.line_chart(chart_data)

with col2:
    with st.container(border=True):
        st.subheader("Robots")
        st.text("🤖 Robot 1: 65% | 32 Mbps | 17 ms")
        st.text("🤖 Robot 2: 27% | 15 Mbps | 250 ms")
        st.text("🤖 Robot 3: 13% | 42 Mbps | 2 ms")

    with st.container(border=True):
        st.subheader("Notifications")
        st.warning("로봇 1의 배터리가 낮습니다. (2025.05.13)")
        st.error("로봇 2의 핑이 매우 높습니다. (2025.05.13)")

st.divider()

# --- 3. 하단: 팀, 지도, 배터리, 연결 ---
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("Team")
        
        # 스크롤 가능한 팀원 목록 컨테이너
        team_list_container = st.container(height=150)
        for member in st.session_state.team_members:
            team_list_container.text(f"👤 {member['name']} ({member['email']})")

        # 팀원 추가 Popover
        with st.popover("팀원 추가"):
            with st.form("add_member_form", clear_on_submit=True):
                new_name = st.text_input("이름")
                new_email = st.text_input("이메일")
                
                submitted = st.form_submit_button("추가")
                if submitted:
                    if new_name and new_email:
                        st.session_state.team_members.append({"name": new_name, "email": new_email})
                        st.rerun()
                    else:
                        st.warning("이름과 이메일을 모두 입력해주세요.")


with col2:
    with st.container(border=True):
        st.subheader("Maps")
        st.image("https://i.imgur.com/Ttcj3QV.png")

with col3:
    with st.container(border=True):
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.subheader("Average Battery")
            st.metric(label="", value="43 %")
        with sub_col2:
            st.subheader("Average Connection")
            st.metric(label="Mbps", value="17")
            st.metric(label="ms", value="153")