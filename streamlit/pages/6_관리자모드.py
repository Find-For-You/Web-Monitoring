import streamlit as st
import sqlite3
import json
from datetime import datetime
import psutil
import os
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="관리자 모드",
    page_icon="🔧",
    layout="wide"
)

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

def main():
    st.title("🔧 관리자 모드")
    
    # 관리자 권한 확인
    if not check_admin_permission():
        st.error("관리자 권한이 필요합니다.")
        st.info("관리자 계정으로 로그인해주세요.")
        return
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs([
        "PID 파라미터 조정", "사용자 관리", "시스템 상태"
    ])
    
    with tab1:
        st.subheader("🎛️ PID 파라미터 조정")
        
        robots = get_robots_for_pid()
        
        if robots:
            # 로봇 선택
            robot_options = {f"{robot[1]} ({robot[2]})": robot[0] for robot in robots}
            selected_robot_name = st.selectbox("로봇 선택", list(robot_options.keys()))
            selected_robot_id = robot_options[selected_robot_name]
            
            # 현재 PID 파라미터 가져오기
            current_params = get_pid_parameters()
            current_param = next((p for p in current_params if p[0] == selected_robot_id), None)
            
            # PID 파라미터 조정 폼
            with st.form("pid_adjustment"):
                st.write("**PID 파라미터 설정:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    kp = st.number_input(
                        "Kp (비례 게인)", 
                        min_value=0.0, 
                        max_value=10.0, 
                        value=current_param[1] if current_param else 1.0,
                        step=0.1
                    )
                
                with col2:
                    ki = st.number_input(
                        "Ki (적분 게인)", 
                        min_value=0.0, 
                        max_value=5.0, 
                        value=current_param[2] if current_param else 0.1,
                        step=0.01
                    )
                
                with col3:
                    kd = st.number_input(
                        "Kd (미분 게인)", 
                        min_value=0.0, 
                        max_value=2.0, 
                        value=current_param[3] if current_param else 0.05,
                        step=0.01
                    )
                
                submit_pid = st.form_submit_button("PID 파라미터 적용")
                
                if submit_pid:
                    if update_pid_parameters(selected_robot_id, kp, ki, kd):
                        st.success("PID 파라미터가 적용되었습니다.")
                    else:
                        st.error("PID 파라미터 적용에 실패했습니다.")
            
            # PID 파라미터 히스토리
            st.subheader("📊 PID 파라미터 히스토리")
            if current_params:
                param_data = []
                for param in current_params:
                    robot_name = next((r[1] for r in robots if r[0] == param[0]), "Unknown")
                    param_data.append({
                        '로봇': robot_name,
                        'Kp': param[1],
                        'Ki': param[2],
                        'Kd': param[3],
                        '업데이트': param[4]
                    })
                
                df_params = pd.DataFrame(param_data)
                st.dataframe(df_params, use_container_width=True)
            else:
                st.info("PID 파라미터 히스토리가 없습니다.")
        
        else:
            st.info("PID 조정 가능한 로봇이 없습니다.")
    
    with tab2:
        st.subheader("👥 사용자 관리")
        
        users = get_all_users()
        
        if users:
            # 사용자 목록
            st.write("**사용자 목록:**")
            for user in users:
                with st.expander(f"{user[1]} ({user[3]}) - {user[2]}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**사용자 ID:** {user[0]}")
                        st.write(f"**이메일:** {user[2]}")
                        st.write(f"**역할:** {user[3]}")
                        st.write(f"**가입일:** {user[4]}")
                        st.write(f"**마지막 로그인:** {user[5] or '없음'}")
                    
                    with col2:
                        # 역할 변경
                        new_role = st.selectbox(
                            "역할 변경",
                            ["user", "admin"],
                            index=0 if user[3] == "user" else 1,
                            key=f"role_{user[0]}"
                        )
                        
                        if st.button("역할 변경", key=f"change_role_{user[0]}"):
                            if update_user_role(user[0], new_role):
                                st.success("역할이 변경되었습니다.")
                                st.rerun()
                            else:
                                st.error("역할 변경에 실패했습니다.")
                        
                        # 사용자 차단
                        if st.button("사용자 차단", key=f"block_{user[0]}"):
                            if block_user(user[0]):
                                st.success("사용자가 차단되었습니다.")
                                st.rerun()
                            else:
                                st.error("사용자 차단에 실패했습니다.")
            
            # 사용자 통계
            st.subheader("📈 사용자 통계")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_users = len(users)
                st.metric("총 사용자", total_users)
            
            with col2:
                admin_users = len([u for u in users if u[3] == "admin"])
                st.metric("관리자", admin_users)
            
            with col3:
                regular_users = len([u for u in users if u[3] == "user"])
                st.metric("일반 사용자", regular_users)
        
        else:
            st.info("등록된 사용자가 없습니다.")
    
    with tab3:
        st.subheader("🖥️ 시스템 상태")
        
        # 시스템 상태 정보 가져오기
        system_status = get_system_status()
        
        # 상태 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            db_color = "green" if system_status['db_status'] == "정상" else "red"
            st.markdown(f"**DB 상태:** <span style='color:{db_color}'>{system_status['db_status']}</span>", unsafe_allow_html=True)
            st.metric("사용자 수", system_status['user_count'])
        
        with col2:
            st.metric("서버 응답 시간", f"{system_status['server_response_time']}ms")
        
        with col3:
            st.metric("CPU 사용률", f"{system_status['cpu_usage']:.1f}%")
        
        with col4:
            st.metric("메모리 사용률", f"{system_status['memory_usage']:.1f}%")
        
        # 시스템 리소스 차트
        st.subheader("📊 시스템 리소스")
        
        # CPU 및 메모리 사용률 차트
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=system_status['cpu_usage'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CPU 사용률 (%)"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터베이스 정보
        st.subheader("🗄️ 데이터베이스 정보")
        
        if os.path.exists('robot_monitoring.db'):
            db_size = os.path.getsize('robot_monitoring.db')
            st.write(f"**데이터베이스 크기:** {db_size / 1024 / 1024:.2f} MB")
        
        # 시스템 로그 (가상 데이터)
        st.subheader("📋 시스템 로그")
        log_data = {
            '시간': ['14:30:15', '14:30:10', '14:30:05', '14:30:00', '14:29:55'],
            '레벨': ['INFO', 'WARNING', 'INFO', 'ERROR', 'INFO'],
            '메시지': [
                '사용자 로그인: admin',
                '로봇 연결 끊김: Robot-02',
                '센서 데이터 수집 완료',
                '데이터베이스 연결 오류',
                '시스템 시작'
            ]
        }
        
        df_log = pd.DataFrame(log_data)
        st.dataframe(df_log, use_container_width=True)
        
        # 시스템 관리 액션
        st.subheader("🔧 시스템 관리")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("시스템 재시작"):
                st.warning("시스템 재시작 기능은 실제 구현에서 추가해야 합니다.")
        
        with col2:
            if st.button("로그 정리"):
                st.info("로그 정리 기능은 실제 구현에서 추가해야 합니다.")

if __name__ == "__main__":
    main() 