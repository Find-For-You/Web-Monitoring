import streamlit as st
import sqlite3
import json
from datetime import datetime
import os

# 페이지 설정
st.set_page_config(
    page_title="설정",
    page_icon="⚙️",
    layout="wide"
)

def get_user_info(user_id):
    """사용자 정보 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT username, email, role, created_at
        FROM users 
        WHERE id = ?
    """, (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def update_user_info(user_id, email):
    """사용자 정보 업데이트"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users 
            SET email = ?, updated_at = ?
            WHERE id = ?
        """, (email, datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_bookmarks(user_id):
    """위치 북마크 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    # 북마크 테이블이 없으면 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            x_coord REAL,
            y_coord REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    cursor.execute("""
        SELECT id, name, x_coord, y_coord, description, created_at
        FROM bookmarks 
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    
    bookmarks = cursor.fetchall()
    conn.close()
    
    return bookmarks

def add_bookmark(user_id, name, x_coord, y_coord, description):
    """북마크 추가"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO bookmarks (user_id, name, x_coord, y_coord, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, x_coord, y_coord, description))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def delete_bookmark(bookmark_id):
    """북마크 삭제"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_notification_settings(user_id):
    """알림 설정 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    # 알림 설정 테이블이 없으면 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            email_notifications BOOLEAN DEFAULT TRUE,
            low_battery_alert BOOLEAN DEFAULT TRUE,
            connection_loss_alert BOOLEAN DEFAULT TRUE,
            detection_alert BOOLEAN DEFAULT TRUE,
            fault_alert BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    cursor.execute("""
        SELECT email_notifications, low_battery_alert, connection_loss_alert, 
               detection_alert, fault_alert
        FROM notification_settings 
        WHERE user_id = ?
    """, (user_id,))
    
    settings = cursor.fetchone()
    conn.close()
    
    if settings:
        return {
            'email_notifications': bool(settings[0]),
            'low_battery_alert': bool(settings[1]),
            'connection_loss_alert': bool(settings[2]),
            'detection_alert': bool(settings[3]),
            'fault_alert': bool(settings[4])
        }
    else:
        # 기본 설정 반환
        return {
            'email_notifications': True,
            'low_battery_alert': True,
            'connection_loss_alert': True,
            'detection_alert': True,
            'fault_alert': True
        }

def update_notification_settings(user_id, settings):
    """알림 설정 업데이트"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        # 기존 설정 삭제
        cursor.execute("DELETE FROM notification_settings WHERE user_id = ?", (user_id,))
        
        # 새 설정 추가
        cursor.execute("""
            INSERT INTO notification_settings 
            (user_id, email_notifications, low_battery_alert, connection_loss_alert, 
             detection_alert, fault_alert)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, settings['email_notifications'], settings['low_battery_alert'],
              settings['connection_loss_alert'], settings['detection_alert'], settings['fault_alert']))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def main():
    st.title("⚙️ 설정")
    
    # 사용자 정보 확인
    if not st.session_state.authenticated:
        st.error("로그인이 필요합니다.")
        return
    
    user_id = st.session_state.user_id
    user_info = get_user_info(user_id)
    
    if not user_info:
        st.error("사용자 정보를 불러올 수 없습니다.")
        return
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "위치 북마크", "알림 설정", "회원 정보", "데이터 저장", "앱 정보"
    ])
    
    with tab1:
        st.subheader("📍 위치 북마크")
        
        # 북마크 목록
        bookmarks = get_bookmarks(user_id)
        
        if bookmarks:
            st.write("**저장된 북마크:**")
            for bookmark in bookmarks:
                with st.expander(f"{bookmark[1]} - ({bookmark[2]}, {bookmark[3]})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**위치:** ({bookmark[2]}, {bookmark[3]})")
                        st.write(f"**설명:** {bookmark[4] or '설명 없음'}")
                        st.write(f"**생성일:** {bookmark[5]}")
                    
                    with col2:
                        if st.button("🗑️ 삭제", key=f"delete_{bookmark[0]}"):
                            if delete_bookmark(bookmark[0]):
                                st.success("북마크가 삭제되었습니다.")
                                st.rerun()
                            else:
                                st.error("삭제에 실패했습니다.")
        else:
            st.info("저장된 북마크가 없습니다.")
        
        # 새 북마크 추가
        st.subheader("➕ 새 북마크 추가")
        with st.form("add_bookmark"):
            bookmark_name = st.text_input("북마크 이름")
            col1, col2 = st.columns(2)
            
            with col1:
                x_coord = st.number_input("X 좌표", value=0.0, step=0.1)
            
            with col2:
                y_coord = st.number_input("Y 좌표", value=0.0, step=0.1)
            
            description = st.text_area("설명 (선택사항)")
            submit_bookmark = st.form_submit_button("북마크 추가")
            
            if submit_bookmark and bookmark_name:
                if add_bookmark(user_id, bookmark_name, x_coord, y_coord, description):
                    st.success("북마크가 추가되었습니다.")
                    st.rerun()
                else:
                    st.error("북마크 추가에 실패했습니다.")
    
    with tab2:
        st.subheader("🔔 알림 설정")
        
        # 현재 알림 설정 가져오기
        current_settings = get_notification_settings(user_id)
        
        with st.form("notification_settings"):
            st.write("**알림 유형 선택:**")
            
            email_notifications = st.checkbox(
                "이메일 알림", 
                value=current_settings['email_notifications']
            )
            
            low_battery_alert = st.checkbox(
                "배터리 부족 알림", 
                value=current_settings['low_battery_alert']
            )
            
            connection_loss_alert = st.checkbox(
                "연결 끊김 알림", 
                value=current_settings['connection_loss_alert']
            )
            
            detection_alert = st.checkbox(
                "객체 탐지 알림", 
                value=current_settings['detection_alert']
            )
            
            fault_alert = st.checkbox(
                "장애/경고 알림", 
                value=current_settings['fault_alert']
            )
            
            submit_settings = st.form_submit_button("설정 저장")
            
            if submit_settings:
                new_settings = {
                    'email_notifications': email_notifications,
                    'low_battery_alert': low_battery_alert,
                    'connection_loss_alert': connection_loss_alert,
                    'detection_alert': detection_alert,
                    'fault_alert': fault_alert
                }
                
                if update_notification_settings(user_id, new_settings):
                    st.success("알림 설정이 저장되었습니다.")
                else:
                    st.error("설정 저장에 실패했습니다.")
    
    with tab3:
        st.subheader("👤 회원 정보")
        
        st.write(f"**사용자명:** {user_info[0]}")
        st.write(f"**역할:** {user_info[2]}")
        st.write(f"**가입일:** {user_info[3]}")
        
        # 이메일 수정
        st.subheader("📧 이메일 수정")
        with st.form("update_email"):
            new_email = st.text_input("새 이메일 주소", value=user_info[1])
            submit_email = st.form_submit_button("이메일 수정")
            
            if submit_email and new_email:
                if update_user_info(user_id, new_email):
                    st.success("이메일이 수정되었습니다.")
                    st.rerun()
                else:
                    st.error("이메일 수정에 실패했습니다.")
    
    with tab4:
        st.subheader("💾 데이터 저장 경로 설정")
        
        # 현재 데이터베이스 정보
        st.write("**현재 데이터베이스:**")
        st.code("robot_monitoring.db")
        
        # 데이터베이스 크기 확인
        if os.path.exists('robot_monitoring.db'):
            size = os.path.getsize('robot_monitoring.db')
            st.write(f"**데이터베이스 크기:** {size / 1024 / 1024:.2f} MB")
        
        # 데이터 백업
        st.subheader("📦 데이터 백업")
        if st.button("백업 생성"):
            # 간단한 백업 로직 (실제로는 더 정교한 백업 필요)
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                import shutil
                shutil.copy2('robot_monitoring.db', backup_filename)
                st.success(f"백업이 생성되었습니다: {backup_filename}")
            except Exception as e:
                st.error(f"백업 생성에 실패했습니다: {e}")
        
        # 데이터 정리
        st.subheader("🧹 데이터 정리")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("오래된 센서 데이터 삭제"):
                conn = sqlite3.connect('robot_monitoring.db')
                cursor = conn.cursor()
                
                try:
                    cursor.execute("""
                        DELETE FROM sensor_data 
                        WHERE sensor_created_at < datetime('now', '-30 days')
                    """)
                    deleted_count = cursor.rowcount
                    conn.commit()
                    conn.close()
                    st.success(f"{deleted_count}개의 오래된 센서 데이터가 삭제되었습니다.")
                except Exception as e:
                    conn.close()
                    st.error(f"데이터 정리에 실패했습니다: {e}")
        
        with col2:
            if st.button("오래된 로그 삭제"):
                conn = sqlite3.connect('robot_monitoring.db')
                cursor = conn.cursor()
                
                try:
                    cursor.execute("""
                        DELETE FROM robot_status_history 
                        WHERE status_created_at < datetime('now', '-30 days')
                    """)
                    deleted_count = cursor.rowcount
                    conn.commit()
                    conn.close()
                    st.success(f"{deleted_count}개의 오래된 로그가 삭제되었습니다.")
                except Exception as e:
                    conn.close()
                    st.error(f"로그 정리에 실패했습니다: {e}")
    
    with tab5:
        st.subheader("ℹ️ 앱 정보")
        
        st.write("**로봇 관제 시스템**")
        st.write("버전: 1.0.0")
        st.write("개발자: 로봇 관제 시스템 팀")
        st.write("라이선스: MIT")
        
        st.write("**주요 기능:**")
        st.write("• 실시간 로봇 모니터링")
        st.write("• 센서 데이터 수집 및 분석")
        st.write("• YOLO 객체 탐지")
        st.write("• 지도 기반 위치 추적")
        st.write("• 알림 및 경고 시스템")
        
        st.write("**기술 스택:**")
        st.write("• Frontend: Streamlit")
        st.write("• Database: SQLite")
        st.write("• Visualization: Plotly")
        st.write("• Real-time: WebSocket")
        
        # 로그아웃 버튼
        st.markdown("---")
        if st.button("🚪 로그아웃"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_role = None
            st.success("로그아웃되었습니다.")
            st.rerun()

if __name__ == "__main__":
    main() 