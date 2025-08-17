import streamlit as st
import os
import sys
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="AI 지능형 정보 탐색 로봇 모니터링 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def main():
    """메인 애플리케이션"""
    
    # 사이드바 설정
    setup_sidebar()
    
    # 인증 확인
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # 메인 대시보드
    show_main_dashboard()

def setup_sidebar():
    """사이드바 설정"""
    with st.sidebar:
        st.title("🤖 로봇 모니터링")
        st.markdown("---")
        
        if st.session_state.authenticated:
            st.success(f"✅ 로그인됨: {st.session_state.user_role}")
            
            # 메뉴
            st.subheader("📋 메뉴")
            
            # 페이지 선택
            page = st.selectbox(
                "페이지 선택",
                [
                    "🏠 홈",
                    "🔧 로봇 관리", 
                    "🗺️ 지도",
                    "📊 분석 리포트",
                    "⚙️ 설정",
                    "👨‍💼 관리자 모드"
                ]
            )
            
            # 페이지 라우팅
            if page == "🏠 홈":
                st.switch_page("pages/1_홈.py")
            elif page == "🔧 로봇 관리":
                st.switch_page("pages/2_로봇관리.py")
            elif page == "🗺️ 지도":
                st.switch_page("pages/3_지도.py")
            elif page == "📊 분석 리포트":
                st.switch_page("pages/4_분석리포트.py")
            elif page == "⚙️ 설정":
                st.switch_page("pages/5_설정.py")
            elif page == "👨‍💼 관리자 모드":
                st.switch_page("pages/6_관리자모드.py")
            
            st.markdown("---")
            
            # 시스템 상태
            st.subheader("📊 시스템 상태")
            
            try:
                from services.robot_service import robot_service
                all_robots = robot_service.get_all_robots()
                online_robots = [r for r in all_robots if r.status == 'online']
                
                st.metric("전체 로봇", len(all_robots))
                st.metric("온라인 로봇", len(online_robots))
                
                # 배터리 상태
                low_battery_count = sum(1 for r in all_robots if r.battery_level < 20)
                if low_battery_count > 0:
                    st.warning(f"🔋 배터리 부족: {low_battery_count}개")
                
                # 알림 상태
                total_alerts = 0
                for robot in all_robots:
                    alerts = robot_service.get_robot_alerts(robot.robot_id, resolved=False)
                    total_alerts += len(alerts)
                
                if total_alerts > 0:
                    st.error(f"🚨 활성 알림: {total_alerts}개")
                else:
                    st.success("✅ 알림 없음")
                    
            except Exception as e:
                st.error(f"시스템 상태 로드 실패: {e}")
            
            st.markdown("---")
            
            # 로그아웃
            if st.button("🚪 로그아웃"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_role = None
                st.rerun()
        
        else:
            st.info("로그인이 필요합니다.")

def show_login_page():
    """로그인 페이지"""
    st.title("🔐 로그인")
    st.markdown("---")
    
    # 로그인 폼
    with st.form("login_form"):
        username = st.text_input("사용자명")
        password = st.text_input("비밀번호", type="password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("로그인", use_container_width=True)
        
        if submit_button:
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.user_id = username
                st.session_state.user_role = "관리자"  # 실제로는 DB에서 조회
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("로그인 실패. 사용자명과 비밀번호를 확인하세요.")
    
    # 데모 계정 정보
    st.markdown("---")
    st.subheader("💡 데모 계정(개발중에만 임시로 표시)")
    st.info("""
    **관리자 계정:**
    - 사용자명: admin
    - 비밀번호: admin123
    
    **운영자 계정:**
    - 사용자명: operator
    - 비밀번호: operator123
    """)

def show_main_dashboard():
    """메인 대시보드"""
    st.title("🤖 AI 지능형 정보 탐색 로봇 모니터링 시스템")
    st.markdown("---")
    
    # 환영 메시지
    st.success(f"환영합니다, {st.session_state.user_role}님!")
    
    # 시스템 개요
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 시스템 개요")
        st.write("""
        이 시스템은 AI 지능형 정보 탐색 로봇을 위한 종합 모니터링 플랫폼입니다.
        
        **주요 기능:**
        • 실시간 로봇 상태 모니터링
        • 위치 추적 및 지도 시각화
        • 센서 데이터 수집 및 분석
        • 카메라 스트림 관리
        • 알림 및 경고 시스템
        • 종합 분석 리포트
        """)
    
    with col2:
        st.subheader("🚀 빠른 시작")
        st.write("""
        **시작하기:**
        1. 사이드바에서 원하는 페이지 선택
        2. 로봇 관리에서 로봇 등록
        3. 지도에서 실시간 위치 확인
        4. 분석 리포트로 성능 모니터링
        """)
    
    # 최근 활동
    st.subheader("📈 최근 활동")
    
    try:
        from services.robot_service import robot_service
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 최근 로봇 활동
            recent_activities = []
            for robot in all_robots[:5]:  # 최근 5개 로봇
                recent_activities.append({
                    '로봇': robot.name,
                    '상태': robot.status,
                    '배터리': f"{robot.battery_level:.1f}%",
                    '마지막 업데이트': robot.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            import pandas as pd
            df_activities = pd.DataFrame(recent_activities)
            st.dataframe(df_activities, use_container_width=True, hide_index=True)
        else:
            st.info("등록된 로봇이 없습니다. 로봇 관리 페이지에서 로봇을 등록해주세요.")
            
    except Exception as e:
        st.error(f"최근 활동 로드 실패: {e}")
    
    # 시스템 정보
    st.subheader("ℹ️ 시스템 정보")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("시스템 버전", "1.0.0")
        st.metric("데이터베이스", "DynamoDB")
    
    with col2:
        st.metric("실행 시간", "24시간")
        st.metric("업데이트", "최신")
    
    with col3:
        st.metric("지원 브라우저", "Chrome, Firefox, Safari")
        st.metric("모바일 지원", "✅")

def authenticate_user(username, password):
    """사용자 인증"""
    # 데모 인증 (실제로는 DB에서 확인)
    valid_users = {
        'admin': 'admin123',
        'operator': 'operator123'
    }
    
    return username in valid_users and valid_users[username] == password

def check_system_health():
    """시스템 건강도 확인"""
    try:
        from services.robot_service import robot_service
        from database.dynamodb_client import db_client
        
        # DynamoDB 연결 확인
        db_client.get_all_robots()
        
        return True
    except Exception as e:
        st.error(f"시스템 연결 오류: {e}")
        return False

if __name__ == "__main__":
    main()