import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import sqlite3
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="홈 - 전체 개요",
    page_icon="🏠",
    layout="wide"
)

# 자동 새로고침 (5초마다)
count = st_autorefresh(interval=5000, limit=None, key="home_autorefresh")

def get_robot_stats():
    """로봇 통계 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    # 연결된 로봇 수
    cursor.execute("SELECT COUNT(*) FROM robots WHERE robot_status = 'Online'")
    connected_robots = cursor.fetchone()[0]
    
    # 전체 로봇 수
    cursor.execute("SELECT COUNT(*) FROM robots")
    total_robots = cursor.fetchone()[0]
    
    # 평균 배터리
    cursor.execute("SELECT AVG(robot_battery) FROM robots WHERE robot_battery IS NOT NULL")
    avg_battery = cursor.fetchone()[0] or 0
    
    # 평균 온도
    cursor.execute("SELECT AVG(sensor_temp) FROM sensor_data WHERE sensor_temp IS NOT NULL")
    avg_temp = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'connected_robots': connected_robots,
        'total_robots': total_robots,
        'avg_battery': round(avg_battery, 1),
        'avg_temp': round(avg_temp, 1)
    }

def get_recent_locations():
    """최근 위치 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT robot_name, robot_location_x, robot_location_y, robot_status
        FROM robots 
        WHERE robot_location_x IS NOT NULL AND robot_location_y IS NOT NULL
        ORDER BY robot_update_at DESC
        LIMIT 10
    """)
    
    locations = cursor.fetchall()
    conn.close()
    
    return locations

def main():
    st.title("🏠 홈 - 전체 개요")
    
    # 상단 메트릭
    stats = get_robot_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="연결된 로봇 수",
            value=f"{stats['connected_robots']}",
            delta=f"{stats['total_robots'] - stats['connected_robots']} 대 오프라인"
        )
    
    with col2:
        connection_status = "정상" if stats['connected_robots'] > 0 else "연결 없음"
        st.metric(
            label="전체 연결 상태",
            value=connection_status,
            delta="🟢" if stats['connected_robots'] > 0 else "🔴"
        )
    
    with col3:
        st.metric(
            label="평균 배터리",
            value=f"{stats['avg_battery']}%",
            delta="-2%" if stats['avg_battery'] < 80 else "+1%"
        )
    
    with col4:
        st.metric(
            label="평균 온도",
            value=f"{stats['avg_temp']}°C",
            delta="1°C" if stats['avg_temp'] > 20 else "-1°C"
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
    
    # 최근 위치 정보
    st.subheader("📍 최근 위치")
    locations = get_recent_locations()
    
    if locations:
        location_df = pd.DataFrame(locations, columns=['로봇명', 'X좌표', 'Y좌표', '상태'])
        st.dataframe(location_df, use_container_width=True)
    else:
        st.info("위치 데이터가 없습니다.")
    
    # 최근 활동 로그
    st.subheader("📋 최근 활동")
    log_data = {
        '시간': ['14:30', '14:25', '14:20', '14:15', '14:10'],
        '로봇': ['Robot-01', 'Robot-02', 'Robot-03', 'Robot-01', 'Robot-04'],
        '활동': ['객체 탐지', '경로 이동', '센서 데이터 전송', '비상 정지', '충전 시작']
    }
    df_log = pd.DataFrame(log_data)
    st.dataframe(df_log, use_container_width=True)

if __name__ == "__main__":
    main() 