import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from services.robot_service import robot_service
from utils.stream_utils import StreamUtils
from config import ROBOT_STATUS, ALERT_LEVELS

# 페이지 설정
st.set_page_config(
    page_title="로봇 모니터링 대시보드",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

def main():
    st.title("🤖 AI 지능형 정보 탐색 로봇 모니터링 대시보드")
    st.markdown("---")
    
    # 실시간 데이터 새로고침
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 실시간 데이터 새로고침", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    st.markdown(f"**마지막 업데이트:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 전체 통계 카드
    display_overview_cards()
    
    # 로봇 상태별 분포 차트
    display_robot_status_chart()
    
    # 최근 알림 목록
    display_recent_alerts()
    
    # 실시간 로봇 목록
    display_robot_list()
    
    # 건강도 점수 차트
    display_health_scores()

def display_overview_cards():
    """전체 통계 카드 표시"""
    st.subheader("📊 전체 통계")
    
    try:
        all_robots = robot_service.get_all_robots()
        online_robots = robot_service.get_online_robots()
        
        total_robots = len(all_robots)
        online_count = len(online_robots)
        offline_count = total_robots - online_count
        
        # 배터리 레벨이 낮은 로봇 수
        low_battery_count = sum(1 for robot in all_robots if robot.battery_level < 20)
        
        # 정비가 필요한 로봇 수
        maintenance_needed = sum(1 for robot in all_robots if robot.needs_maintenance())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="전체 로봇",
                value=total_robots,
                delta=None
            )
        
        with col2:
            st.metric(
                label="온라인 로봇",
                value=online_count,
                delta=f"{online_count - (total_robots - online_count)}" if total_robots > 0 else "0"
            )
        
        with col3:
            st.metric(
                label="배터리 부족",
                value=low_battery_count,
                delta=None
            )
        
        with col4:
            st.metric(
                label="정비 필요",
                value=maintenance_needed,
                delta=None
            )
            
    except Exception as e:
        st.error(f"통계 데이터 로드 실패: {e}")

def display_robot_status_chart():
    """로봇 상태별 분포 차트"""
    st.subheader("📈 로봇 상태 분포")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            status_counts = {}
            for robot in all_robots:
                status = robot.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # 상태별 색상 매핑
            colors = {
                'online': '#00FF00',
                'offline': '#FF0000',
                'maintenance': '#FFA500',
                'error': '#FF0000',
                'charging': '#FFFF00',
                'moving': '#0000FF',
                'idle': '#808080'
            }
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="로봇 상태별 분포",
                color_discrete_map=colors
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("등록된 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"상태 차트 로드 실패: {e}")

def display_recent_alerts():
    """최근 알림 목록 표시"""
    st.subheader("🚨 최근 알림")
    
    try:
        all_robots = robot_service.get_all_robots()
        recent_alerts = []
        
        for robot in all_robots[:5]:  # 최근 5개 로봇만 확인
            alerts = robot_service.get_robot_alerts(robot.robot_id, resolved=False)
            recent_alerts.extend(alerts[:3])  # 각 로봇당 최근 3개 알림
        
        # 시간순 정렬
        recent_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        if recent_alerts:
            alert_data = []
            for alert in recent_alerts[:10]:  # 최근 10개 알림만 표시
                alert_data.append({
                    '로봇 ID': alert.robot_id,
                    '레벨': alert.level,
                    '메시지': alert.message,
                    '시간': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            df = pd.DataFrame(alert_data)
            
            # 레벨별 색상 적용
            def color_alert_level(val):
                if val == 'critical':
                    return 'background-color: #ffcccc'
                elif val == 'error':
                    return 'background-color: #ffdddd'
                elif val == 'warning':
                    return 'background-color: #fff2cc'
                else:
                    return 'background-color: #ccffcc'
            
            st.dataframe(
                df.style.applymap(color_alert_level, subset=['레벨']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("현재 활성 알림이 없습니다.")
            
    except Exception as e:
        st.error(f"알림 데이터 로드 실패: {e}")

def display_robot_list():
    """실시간 로봇 목록 표시"""
    st.subheader("🤖 실시간 로봇 목록")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            robot_data = []
            for robot in all_robots:
                health_score = robot.get_health_score()
                
                robot_data.append({
                    '로봇 ID': robot.robot_id,
                    '이름': robot.name,
                    '모델': robot.model,
                    '상태': robot.status,
                    '배터리': f"{robot.battery_level:.1f}%",
                    '건강도': f"{health_score:.1f}%",
                    '위치': f"{robot.location.latitude:.4f}, {robot.location.longitude:.4f}" if robot.location else "N/A",
                    '마지막 업데이트': robot.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            df = pd.DataFrame(robot_data)
            
            # 상태별 색상 적용
            def color_status(val):
                if val == 'online':
                    return 'background-color: #ccffcc'
                elif val == 'offline':
                    return 'background-color: #ffcccc'
                elif val == 'maintenance':
                    return 'background-color: #fff2cc'
                elif val == 'error':
                    return 'background-color: #ffdddd'
                else:
                    return 'background-color: #f0f0f0'
            
            st.dataframe(
                df.style.applymap(color_status, subset=['상태']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("등록된 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"로봇 목록 로드 실패: {e}")

def display_health_scores():
    """건강도 점수 차트"""
    st.subheader("💚 로봇 건강도 점수")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            robot_names = [robot.name for robot in all_robots]
            health_scores = [robot.get_health_score() for robot in all_robots]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=robot_names,
                    y=health_scores,
                    marker_color=['red' if score < 50 else 'orange' if score < 80 else 'green' for score in health_scores]
                )
            ])
            
            fig.update_layout(
                title="로봇별 건강도 점수",
                xaxis_title="로봇 이름",
                yaxis_title="건강도 점수 (%)",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("건강도 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"건강도 차트 로드 실패: {e}")

if __name__ == "__main__":
    main() 