import streamlit as st
import hashlib
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from dynamodb_manager import dynamodb_manager
from aws_config import aws_config

# 페이지 설정
st.set_page_config(
    page_title="로봇 관제 시스템 (DynamoDB)",
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
if 'aws_configured' not in st.session_state:
    st.session_state.aws_configured = False

def hash_password(password):
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_aws_credentials():
    """AWS 자격 증명 설정"""
    st.subheader("AWS 설정")
    
    with st.form("aws_config_form"):
        access_key = st.text_input("AWS Access Key ID", type="password")
        secret_key = st.text_input("AWS Secret Access Key", type="password")
        region = st.selectbox("AWS Region", ["ap-northeast-2", "us-east-1", "us-west-2"], index=0)
        
        submit_button = st.form_submit_button("AWS 연결 설정")
        
        if submit_button:
            if access_key and secret_key:
                try:
                    aws_config.setup_credentials(access_key, secret_key, region)
                    if aws_config.test_connection():
                        st.session_state.aws_configured = True
                        st.success("AWS 연결이 성공적으로 설정되었습니다!")
                        st.rerun()
                    else:
                        st.error("AWS 연결에 실패했습니다. 자격 증명을 확인해주세요.")
                except Exception as e:
                    st.error(f"AWS 설정 중 오류 발생: {e}")
            else:
                st.warning("모든 필드를 입력해주세요.")

def login_user(email, password):
    """사용자 로그인 (DynamoDB)"""
    try:
        user = dynamodb_manager.get_user_by_email(email)
        if user and user.get('user_password') == hash_password(password):
            return user
        return None
    except Exception as e:
        st.error(f"로그인 중 오류 발생: {e}")
        return None

def register_user(first_name, last_name, email, password):
    """사용자 등록 (DynamoDB)"""
    try:
        # 이메일 중복 확인
        existing_user = dynamodb_manager.get_user_by_email(email)
        if existing_user:
            return False
        
        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'user_email': email,
            'user_password': hash_password(password),
            'user_role': 'User'
        }
        
        user_id = dynamodb_manager.create_user(user_data)
        return user_id
    except Exception as e:
        st.error(f"회원가입 중 오류 발생: {e}")
        return False

def main_splash():
    """스플래시 화면 - 로그인/회원가입"""
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1 style="font-size: 3rem; color: #1f77b4;">🤖 로봇 관제 시스템</h1>
        <p style="font-size: 1.2rem; color: #666;">Robot Monitoring & Control System (DynamoDB)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            submit_button = st.form_submit_button("로그인")
            
            if submit_button:
                if email and password:
                    user = login_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['user_id']
                        st.session_state.user_role = user['user_role']
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("이메일 또는 비밀번호가 잘못되었습니다.")
                else:
                    st.warning("모든 필드를 입력해주세요.")
    
    with tab2:
        st.subheader("회원가입")
        with st.form("register_form"):
            first_name = st.text_input("이름")
            last_name = st.text_input("성")
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            submit_register = st.form_submit_button("회원가입")
            
            if submit_register:
                if first_name and last_name and email and password and confirm_password:
                    if password == confirm_password:
                        if register_user(first_name, last_name, email, password):
                            st.success("회원가입이 완료되었습니다! 로그인해주세요.")
                        else:
                            st.error("이미 존재하는 이메일입니다.")
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("모든 필드를 입력해주세요.")

def main_dashboard():
    """메인 대시보드 (DynamoDB)"""
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
        if st.session_state.user_role == 'Admin':
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
    st.title("🏠 홈 - 전체 개요 (DynamoDB)")
    
    # 자동 새로고침 (5초마다)
    count = st_autorefresh(interval=5000, limit=None, key="fizzbuzzcounter")
    
    try:
        # DynamoDB에서 통계 데이터 가져오기
        stats = dynamodb_manager.get_dashboard_stats()
        
        # 상단 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="연결된 로봇 수",
                value=stats['robot_stats']['total_robots'],
                delta=f"{stats['robot_stats']['online_robots']} 온라인"
            )
        
        with col2:
            st.metric(
                label="전체 연결 상태",
                value="정상" if stats['robot_stats']['online_robots'] > 0 else "오프라인",
                delta="🟢" if stats['robot_stats']['online_robots'] > 0 else "🔴"
            )
        
        with col3:
            st.metric(
                label="평균 배터리",
                value=f"{stats['robot_stats']['avg_battery']:.1f}%",
                delta="정상" if stats['robot_stats']['avg_battery'] > 50 else "낮음"
            )
        
        with col4:
            st.metric(
                label="평균 온도",
                value=f"{stats['sensor_stats']['avg_temperature']:.1f}°C",
                delta="정상" if 20 <= stats['sensor_stats']['avg_temperature'] <= 30 else "주의"
            )
        
        # 차트 영역
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("로봇 상태 분포")
            robots = dynamodb_manager.get_robots()
            if robots:
                status_counts = {}
                for robot in robots:
                    status = robot.get('robot_status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                status_data = {
                    '상태': list(status_counts.keys()),
                    '개수': list(status_counts.values())
                }
                df_status = pd.DataFrame(status_data)
                fig = px.pie(df_status, values='개수', names='상태', title="로봇 상태 분포")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("로봇 데이터가 없습니다.")
        
        with col2:
            st.subheader("배터리 수준")
            if robots:
                battery_data = {
                    '로봇': [robot.get('robot_name', f"Robot-{robot.get('robot_id', 'Unknown')}") for robot in robots],
                    '배터리': [robot.get('robot_battery', 0) for robot in robots]
                }
                df_battery = pd.DataFrame(battery_data)
                fig = px.bar(df_battery, x='로봇', y='배터리', title="로봇별 배터리 수준")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("로봇 데이터가 없습니다.")
        
        # 최근 활동 로그
        st.subheader("최근 활동")
        try:
            # 최근 명령 히스토리 가져오기
            all_commands = []
            for robot in robots:
                commands = dynamodb_manager.get_command_history_by_robot(robot['robot_id'])
                all_commands.extend(commands)
            
            # 최신 5개 명령만 표시
            recent_commands = sorted(all_commands, key=lambda x: x.get('command_created_at', ''), reverse=True)[:5]
            
            if recent_commands:
                log_data = {
                    '시간': [cmd.get('command_created_at', '')[:16] for cmd in recent_commands],
                    '로봇': [cmd.get('robot_id', 'Unknown') for cmd in recent_commands],
                    '활동': [cmd.get('command_type', 'Unknown') for cmd in recent_commands]
                }
                df_log = pd.DataFrame(log_data)
                st.dataframe(df_log, use_container_width=True)
            else:
                st.info("최근 활동이 없습니다.")
        except Exception as e:
            st.error(f"활동 로그를 가져오는 중 오류 발생: {e}")
    
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류 발생: {e}")
        st.info("DynamoDB 연결을 확인해주세요.")

# 메인 실행
if __name__ == "__main__":
    # AWS 설정 확인
    if not st.session_state.aws_configured:
        setup_aws_credentials()
    else:
        # 인증 상태에 따라 페이지 표시
        if not st.session_state.authenticated:
            main_splash()
        else:
            main_dashboard()
