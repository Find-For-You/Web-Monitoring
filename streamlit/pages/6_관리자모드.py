import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from services.robot_service import robot_service
from config import ROBOT_STATUS, ALERT_LEVELS, SENSOR_TYPES

# 페이지 설정
st.set_page_config(
    page_title="관리자 모드",
    page_icon="👨‍💼",
    layout="wide"
)

<<<<<<< HEAD
def check_admin_permission():
    """관리자 권한 확인"""
    if not st.session_state.authenticated:
        return False
    
    if st.session_state.user_role != 'admin':
        return False
    
    return True

def get_all_users():
    """모든 사용자 목록 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, user_email, user_email, user_role, created_at, last_login_date
        FROM users
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    conn.close()
    
    return users

def update_user_role(user_id, new_role):
    """사용자 역할 업데이트"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users 
            SET user_role = ?, updated_at = ?
            WHERE user_id = ?
        """, (new_role, datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def block_user(user_id):
    """사용자 차단"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users 
            SET isdeleted = 1, updated_at = ?
            WHERE user_id = ?
        """, (datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_system_status():
    """시스템 상태 정보 가져오기"""
    # 데이터베이스 상태
    db_status = "정상"
    try:
        conn = sqlite3.connect('robot_monitoring.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        db_status = "오류"
        user_count = 0
    
    # 서버 응답 시간 (가상 데이터)
    server_response_time = 150  # ms
    
    # 서버 부하
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    
    return {
        'db_status': db_status,
        'user_count': user_count,
        'server_response_time': server_response_time,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage
    }

def get_pid_parameters():
    """PID 파라미터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    # PID 파라미터 테이블이 없으면 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pid_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id INTEGER,
            kp REAL DEFAULT 1.0,
            ki REAL DEFAULT 0.1,
            kd REAL DEFAULT 0.05,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (robot_id) REFERENCES robots (id)
        )
    """)
    
    cursor.execute("""
        SELECT robot_id, kp, ki, kd, updated_at
        FROM pid_parameters
        ORDER BY robot_id
    """)
    
    parameters = cursor.fetchall()
    conn.close()
    
    return parameters

def update_pid_parameters(robot_id, kp, ki, kd):
    """PID 파라미터 업데이트"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        # 기존 파라미터 삭제
        cursor.execute("DELETE FROM pid_parameters WHERE robot_id = ?", (robot_id,))
        
        # 새 파라미터 추가
        cursor.execute("""
            INSERT INTO pid_parameters (robot_id, kp, ki, kd, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (robot_id, kp, ki, kd, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_robots_for_pid():
    """PID 조정 가능한 로봇 목록"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT robot_id, robot_name, robot_status
        FROM robots
        ORDER BY robot_name
    """)
    
    robots = cursor.fetchall()
    conn.close()
    
    return robots

=======
>>>>>>> 6e105827c182f77b8467adb8e75db507e3c04462
def main():
    st.title("👨‍💼 관리자 모드")
    st.markdown("---")
    
    # 관리자 권한 확인
    if not check_admin_permission():
        st.error("관리자 권한이 필요합니다.")
        return
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 시스템 모니터링", "👥 사용자 관리", "🗄️ 데이터 관리", "🔧 시스템 설정"])
    
    with tab1:
        display_system_monitoring()
    
    with tab2:
        display_user_management()
    
    with tab3:
        display_data_management()
    
    with tab4:
        display_system_configuration()

def check_admin_permission():
    """관리자 권한 확인"""
    # 실제로는 세션에서 사용자 역할 확인
    return st.session_state.get('user_role') == '관리자' or st.session_state.get('user_id') == 'admin'

def display_system_monitoring():
    """시스템 모니터링"""
    st.subheader("📊 시스템 모니터링")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        # 시스템 상태 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_robots = len(all_robots)
            st.metric("전체 로봇", total_robots)
        
        with col2:
            online_robots = len([r for r in all_robots if r.status == 'online'])
            st.metric("온라인 로봇", online_robots)
        
        with col3:
            avg_battery = sum(r.battery_level for r in all_robots) / len(all_robots) if all_robots else 0
            st.metric("평균 배터리", f"{avg_battery:.1f}%")
        
        with col4:
            system_health = "양호" if online_robots > total_robots * 0.8 else "주의" if online_robots > total_robots * 0.5 else "위험"
            st.metric("시스템 상태", system_health)
        
        # 시스템 성능 차트
        col1, col2 = st.columns(2)
        
        with col1:
            # 로봇 상태 분포
            status_counts = {}
            for robot in all_robots:
                status = robot.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig_status = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="로봇 상태 분포"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # 배터리 분포
            battery_levels = [robot.battery_level for robot in all_robots]
            fig_battery = px.histogram(
                x=battery_levels,
                title="배터리 레벨 분포",
                labels={'x': '배터리 레벨 (%)', 'y': '로봇 수'}
            )
            st.plotly_chart(fig_battery, use_container_width=True)
        
        # 시스템 로그
        st.subheader("📝 시스템 로그")
        system_logs = generate_system_logs()
        
        if system_logs:
            df_logs = pd.DataFrame(system_logs)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.info("시스템 로그가 없습니다.")
            
    except Exception as e:
        st.error(f"시스템 모니터링 로드 실패: {e}")

def display_user_management():
    """사용자 관리"""
    st.subheader("👥 사용자 관리")
    
    # 사용자 목록 (시뮬레이션)
    users_data = [
        {'사용자 ID': 'admin', '이름': '관리자', '이메일': 'admin@example.com', '역할': '관리자', '상태': '활성', '마지막 로그인': '2024-01-15 14:30:00'},
        {'사용자 ID': 'operator1', '이름': '운영자1', '이메일': 'operator1@example.com', '역할': '운영자', '상태': '활성', '마지막 로그인': '2024-01-15 13:45:00'},
        {'사용자 ID': 'operator2', '이름': '운영자2', '이메일': 'operator2@example.com', '역할': '운영자', '상태': '비활성', '마지막 로그인': '2024-01-14 18:20:00'},
        {'사용자 ID': 'viewer1', '이름': '조회자1', '이메일': 'viewer1@example.com', '역할': '조회자', '상태': '활성', '마지막 로그인': '2024-01-15 12:15:00'}
    ]
    
    df_users = pd.DataFrame(users_data)
    st.dataframe(df_users, use_container_width=True, hide_index=True)
    
    # 사용자 추가
    st.subheader("➕ 사용자 추가")
    
    with st.form("add_user"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_user_id = st.text_input("사용자 ID")
            new_name = st.text_input("이름")
            new_email = st.text_input("이메일")
        
        with col2:
            new_role = st.selectbox("역할", ["관리자", "운영자", "조회자"])
            new_status = st.selectbox("상태", ["활성", "비활성"])
        
        submitted = st.form_submit_button("사용자 추가")
        
        if submitted:
            if new_user_id and new_name and new_email:
                st.success(f"사용자 '{new_name}'이 추가되었습니다!")
                st.rerun()
            else:
                st.error("필수 필드를 입력해주세요.")
    
    # 사용자 권한 관리
    st.subheader("🔐 권한 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**역할별 권한**")
        permissions = {
            '관리자': ['모든 기능 접근', '사용자 관리', '시스템 설정', '데이터 관리'],
            '운영자': ['로봇 관리', '모니터링', '알림 관리', '리포트 생성'],
            '조회자': ['데이터 조회', '리포트 보기']
        }
        
        for role, perms in permissions.items():
            with st.expander(f"📋 {role}"):
                for perm in perms:
                    st.write(f"• {perm}")
    
    with col2:
        st.write("**권한 수정**")
        selected_user = st.selectbox("사용자 선택", [user['사용자 ID'] for user in users_data])
        new_role = st.selectbox("새 역할", ["관리자", "운영자", "조회자"])
        
        if st.button("권한 변경"):
            st.success(f"사용자 '{selected_user}'의 권한이 '{new_role}'로 변경되었습니다!")

def display_data_management():
    """데이터 관리"""
    st.subheader("🗄️ 데이터 관리")
    
    # 데이터베이스 상태
    st.write("**📊 데이터베이스 상태**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 로봇 수", "15")
        st.metric("총 센서 데이터", "1,234,567")
    
    with col2:
        st.metric("총 알림 수", "89")
        st.metric("총 사용자", "8")
    
    with col3:
        st.metric("데이터베이스 크기", "2.3 GB")
        st.metric("백업 크기", "1.8 GB")
    
    with col4:
        st.metric("마지막 백업", "2024-01-15 02:00")
        st.metric("백업 상태", "✅ 성공")
    
    # 데이터 백업
    st.subheader("💾 데이터 백업")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**자동 백업 설정**")
        backup_enabled = st.checkbox("자동 백업 활성화", value=True)
        backup_frequency = st.selectbox("백업 빈도", ["매일", "매주", "매월"])
        backup_time = st.time_input("백업 시간", value=datetime.strptime("02:00", "%H:%M").time())
        
        if st.button("백업 설정 저장"):
            st.success("백업 설정이 저장되었습니다!")
    
    with col2:
        st.write("**수동 백업**")
        if st.button("📦 지금 백업 생성"):
            with st.spinner("백업 생성 중..."):
                # 백업 시뮬레이션
                import time
                time.sleep(2)
                st.success("백업이 성공적으로 생성되었습니다!")
        
        if st.button("📋 백업 목록 보기"):
            backup_list = [
                {'파일명': 'backup_20240115_020000.zip', '크기': '1.8 GB', '상태': '완료', '생성일': '2024-01-15 02:00'},
                {'파일명': 'backup_20240114_020000.zip', '크기': '1.7 GB', '상태': '완료', '생성일': '2024-01-14 02:00'},
                {'파일명': 'backup_20240113_020000.zip', '크기': '1.6 GB', '상태': '완료', '생성일': '2024-01-13 02:00'}
            ]
            df_backup = pd.DataFrame(backup_list)
            st.dataframe(df_backup, use_container_width=True, hide_index=True)
    
    # 데이터 정리
    st.subheader("🧹 데이터 정리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**오래된 데이터 정리**")
        days_to_keep = st.slider("보관 기간 (일)", 30, 365, 90)
        
        if st.button("오래된 센서 데이터 삭제"):
            with st.spinner("데이터 정리 중..."):
                # 정리 시뮬레이션
                import time
                time.sleep(1)
                st.success("123,456개의 오래된 센서 데이터가 삭제되었습니다!")
        
        if st.button("오래된 로그 삭제"):
            with st.spinner("로그 정리 중..."):
                # 정리 시뮬레이션
                import time
                time.sleep(1)
                st.success("45,678개의 오래된 로그가 삭제되었습니다!")
    
    with col2:
        st.write("**데이터 압축**")
        if st.button("데이터베이스 압축"):
            with st.spinner("압축 중..."):
                # 압축 시뮬레이션
                import time
                time.sleep(2)
                st.success("데이터베이스가 성공적으로 압축되었습니다! (크기: 2.1 GB)")
        
        if st.button("인덱스 재구성"):
            with st.spinner("인덱스 재구성 중..."):
                # 재구성 시뮬레이션
                import time
                time.sleep(1)
                st.success("인덱스가 성공적으로 재구성되었습니다!")

def display_system_configuration():
    """시스템 설정"""
    st.subheader("🔧 시스템 설정")
    
    # 시스템 정보
    st.write("**ℹ️ 시스템 정보**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        system_info = {
            '시스템 이름': 'AI 지능형 정보 탐색 로봇 모니터링 시스템',
            '버전': '1.0.0',
            '빌드 날짜': '2024-01-15',
            'Python 버전': '3.9.0',
            'Streamlit 버전': '1.28.1'
        }
        
        for key, value in system_info.items():
            st.write(f"**{key}:** {value}")
    
    with col2:
        runtime_info = {
            '시작 시간': '2024-01-15 00:00:00',
            '실행 시간': '14시간 30분',
            '메모리 사용량': '512 MB',
            'CPU 사용률': '15%',
            '디스크 사용률': '45%'
        }
        
        for key, value in runtime_info.items():
            st.write(f"**{key}:** {value}")
    
    # 시스템 설정
    st.subheader("⚙️ 시스템 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**일반 설정**")
        debug_mode = st.checkbox("디버그 모드", value=False)
        log_level = st.selectbox("로그 레벨", ["DEBUG", "INFO", "WARNING", "ERROR"])
        max_log_size = st.number_input("최대 로그 크기 (MB)", min_value=10, max_value=1000, value=100)
    
    with col2:
        st.write("**성능 설정**")
        cache_enabled = st.checkbox("캐시 활성화", value=True)
        cache_size = st.slider("캐시 크기 (MB)", 50, 500, 200)
        auto_refresh = st.checkbox("자동 새로고침", value=True)
        refresh_interval = st.slider("새로고침 간격 (초)", 5, 60, 10)
    
    if st.button("💾 시스템 설정 저장"):
        st.success("시스템 설정이 저장되었습니다!")
    
    # 시스템 유지보수
    st.subheader("🔧 시스템 유지보수")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**시스템 재시작**")
        if st.button("🔄 시스템 재시작"):
            st.warning("시스템을 재시작하시겠습니까?")
            if st.button("✅ 확인"):
                with st.spinner("시스템 재시작 중..."):
                    # 재시작 시뮬레이션
                    import time
                    time.sleep(3)
                    st.success("시스템이 성공적으로 재시작되었습니다!")
    
    with col2:
        st.write("**서비스 관리**")
        services = ['웹 서버', '데이터베이스', '모니터링 서비스', '알림 서비스']
        
        for service in services:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(service)
            with col_b:
                if st.button(f"재시작", key=f"restart_{service}"):
                    st.success(f"{service}가 재시작되었습니다!")

def generate_system_logs():
    """시스템 로그 생성 (시뮬레이션)"""
    logs = [
        {'시간': '2024-01-15 14:30:00', '레벨': 'INFO', '메시지': '시스템 시작됨'},
        {'시간': '2024-01-15 14:29:00', '레벨': 'WARNING', '메시지': '로봇 Robot-03 배터리 부족 (15%)'},
        {'시간': '2024-01-15 14:28:00', '레벨': 'INFO', '메시지': '새로운 로봇 등록: Robot-05'},
        {'시간': '2024-01-15 14:27:00', '레벨': 'ERROR', '메시지': '로봇 Robot-02 연결 끊김'},
        {'시간': '2024-01-15 14:26:00', '레벨': 'INFO', '메시지': '데이터베이스 백업 완료'},
        {'시간': '2024-01-15 14:25:00', '레벨': 'INFO', '메시지': '사용자 admin 로그인'},
        {'시간': '2024-01-15 14:24:00', '레벨': 'WARNING', '메시지': '센서 데이터 수집 지연'},
        {'시간': '2024-01-15 14:23:00', '레벨': 'INFO', '메시지': '알림 설정 업데이트'},
    ]
    
    return logs

if __name__ == "__main__":
    main() 