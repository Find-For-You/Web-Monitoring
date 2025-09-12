import streamlit as st
import sqlite3
import hashlib
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(
    page_title="로봇 관제 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'user'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def hash_password(password):
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_table():
    """사용자 테이블 생성"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    # 기본 관리자 계정 생성
    try:
        admin_password = hash_password("admin123")
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        ''', ("admin", admin_password, "admin@robot.com", "admin"))
        conn.commit()
    except:
        pass
    
    conn.close()

def login_user(username, password):
    """사용자 로그인"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    
    cursor.execute('''
        SELECT user_id, user_email, user_role FROM users 
        WHERE user_email = ? AND user_password = ?
    ''', (username, hashed_password))
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def register_user(username, password, email):
    """사용자 등록"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (user_email, user_password, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (email, hashed_password, username, ''))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def main_splash():
    """스플래시 화면 - 로그인/회원가입"""
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1 style="font-size: 3rem; color: #1f77b4;">🤖 로봇 관제 시스템</h1>
        <p style="font-size: 1.2rem; color: #666;">Robot Monitoring & Control System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            username = st.text_input("사용자명")
            password = st.text_input("비밀번호", type="password")
            submit_button = st.form_submit_button("로그인")
            
            if submit_button:
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user[0]
                        st.session_state.user_role = user[2]
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("사용자명 또는 비밀번호가 잘못되었습니다.")
                else:
                    st.warning("모든 필드를 입력해주세요.")
    
    with tab2:
        st.subheader("회원가입")
        with st.form("register_form"):
            new_username = st.text_input("사용자명 (신규)")
            new_password = st.text_input("비밀번호 (신규)", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            email = st.text_input("이메일")
            submit_register = st.form_submit_button("회원가입")
            
            if submit_register:
                if new_username and new_password and confirm_password and email:
                    if new_password == confirm_password:
                        if register_user(new_username, new_password, email):
                            st.success("회원가입이 완료되었습니다! 로그인해주세요.")
                        else:
                            st.error("이미 존재하는 사용자명 또는 이메일입니다.")
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("모든 필드를 입력해주세요.")

def main_dashboard():
    """메인 대시보드"""
    # 사이드바 네비게이션
    with st.sidebar:
        st.title("🤖 로봇 관제 시스템")
        st.markdown("---")
        
        # 사용자 정보
        if st.session_state.authenticated:
            st.write(f"**사용자:** {st.session_state.user_role}")
            st.write(f"**역할:** {st.session_state.user_role}")
        
        st.markdown("---")
        
        # 네비게이션 메뉴
        st.subheader("📋 메뉴")
        
        # 일반 사용자 메뉴
        if st.button("🏠 홈", use_container_width=True):
            st.switch_page("pages/1_홈.py")
        
        if st.button("🤖 로봇 관리", use_container_width=True):
            st.switch_page("pages/2_로봇관리.py")
        
        if st.button("🗺️ 지도", use_container_width=True):
            st.switch_page("pages/3_지도.py")
        
        if st.button("📊 분석/리포트", use_container_width=True):
            st.switch_page("pages/4_분석리포트.py")
        
        if st.button("⚙️ 설정", use_container_width=True):
            st.switch_page("pages/5_설정.py")
        
        # 관리자 전용 메뉴
        if st.session_state.user_role == 'admin':
            st.markdown("---")
            st.subheader("🔧 관리자")
            
            if st.button("🔧 관리자 모드", use_container_width=True):
                st.switch_page("pages/6_관리자모드.py")
        
        st.markdown("---")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_role = None
            st.success("로그아웃되었습니다.")
            st.rerun()
    
    # 메인 콘텐츠
    st.title("🏠 홈 - 전체 개요")
    
    # 자동 새로고침 (5초마다)
    count = st_autorefresh(interval=5000, limit=None, key="fizzbuzzcounter")
    
    # 상단 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="연결된 로봇 수",
            value="5",
            delta="2"
        )
    
    with col2:
        st.metric(
            label="전체 연결 상태",
            value="정상",
            delta="🟢"
        )
    
    with col3:
        st.metric(
            label="평균 배터리",
            value="78%",
            delta="-2%"
        )
    
    with col4:
        st.metric(
            label="평균 온도",
            value="24°C",
            delta="1°C"
        )
    
    # 차트 영역
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("로봇 상태 분포")
        status_data = {
            '상태': ['정상', '경고', '오류', '충전중'],
            '개수': [3, 1, 0, 1]
        }
        df_status = pd.DataFrame(status_data)
        fig = px.pie(df_status, values='개수', names='상태', title="로봇 상태 분포")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("배터리 수준")
        battery_data = {
            '로봇': ['Robot-01', 'Robot-02', 'Robot-03', 'Robot-04', 'Robot-05'],
            '배터리': [85, 72, 90, 65, 78]
        }
        df_battery = pd.DataFrame(battery_data)
        fig = px.bar(df_battery, x='로봇', y='배터리', title="로봇별 배터리 수준")
        st.plotly_chart(fig, use_container_width=True)
    
    # 최근 활동 로그
    st.subheader("최근 활동")
    log_data = {
        '시간': ['14:30', '14:25', '14:20', '14:15', '14:10'],
        '로봇': ['Robot-01', 'Robot-02', 'Robot-03', 'Robot-01', 'Robot-04'],
        '활동': ['객체 탐지', '경로 이동', '센서 데이터 전송', '비상 정지', '충전 시작']
    }
    df_log = pd.DataFrame(log_data)
    st.dataframe(df_log, use_container_width=True)

# 메인 실행
if __name__ == "__main__":
    # 사용자 테이블 생성
    create_user_table()
    
    # 인증 상태에 따라 페이지 표시
    if not st.session_state.authenticated:
        main_splash()
    else:
        main_dashboard()