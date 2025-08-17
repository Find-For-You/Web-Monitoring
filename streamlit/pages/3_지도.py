import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from services.robot_service import robot_service
from config import ROBOT_STATUS

# 페이지 설정
st.set_page_config(
    page_title="지도 - 로봇 위치 추적",
    page_icon="🗺️",
    layout="wide"
)

def main():
    st.title("🗺️ 로봇 위치 추적 지도")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📍 실시간 지도", "📊 위치 통계", "🛤️ 이동 경로"])
    
    with tab1:
        display_realtime_map()
    
    with tab2:
        display_location_statistics()
    
    with tab3:
        display_movement_paths()

def display_realtime_map():
    """실시간 지도 표시"""
    st.subheader("📍 실시간 로봇 위치")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 지도 중심점 계산 (모든 로봇의 평균 위치)
            robots_with_location = [r for r in all_robots if r.location]
            
            if robots_with_location:
                avg_lat = sum(r.location.latitude for r in robots_with_location) / len(robots_with_location)
                avg_lon = sum(r.location.longitude for r in robots_with_location) / len(robots_with_location)
                
                # Folium 지도 생성
                m = folium.Map(
                    location=[avg_lat, avg_lon],
                    zoom_start=12,
                    tiles='OpenStreetMap'
                )
                
                # 로봇별 마커 추가
                for robot in robots_with_location:
                    # 상태별 색상 설정
                    color_map = {
                        'online': 'green',
                        'offline': 'red',
                        'maintenance': 'orange',
                        'error': 'darkred',
                        'charging': 'yellow',
                        'moving': 'blue',
                        'idle': 'gray'
                    }
                    
                    color = color_map.get(robot.status, 'gray')
                    
                    # 팝업 정보 생성
                    popup_html = f"""
                    <div style="width: 200px;">
                        <h4>🤖 {robot.name}</h4>
                        <p><strong>ID:</strong> {robot.robot_id}</p>
                        <p><strong>상태:</strong> {robot.status}</p>
                        <p><strong>배터리:</strong> {robot.battery_level:.1f}%</p>
                        <p><strong>건강도:</strong> {robot.get_health_score():.1f}%</p>
                        <p><strong>위치:</strong> {robot.location.latitude:.6f}, {robot.location.longitude:.6f}</p>
                        <p><strong>업데이트:</strong> {robot.updated_at.strftime('%H:%M:%S')}</p>
                    </div>
                    """
                    
                    # 마커 추가
                    folium.Marker(
                        location=[robot.location.latitude, robot.location.longitude],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{robot.name} ({robot.status})",
                        icon=folium.Icon(color=color, icon='robot', prefix='fa')
                    ).add_to(m)
                
                # 지도 표시
                st_folium(m, width=800, height=600)
                
                # 로봇 목록 테이블
                st.subheader("📋 현재 위치 정보")
                location_data = []
                
                for robot in robots_with_location:
                    location_data.append({
                        '로봇 이름': robot.name,
                        '로봇 ID': robot.robot_id,
                        '상태': robot.status,
                        '위도': f"{robot.location.latitude:.6f}",
                        '경도': f"{robot.location.longitude:.6f}",
                        '고도': f"{robot.location.altitude:.1f}m" if robot.location.altitude else "N/A",
                        '배터리': f"{robot.battery_level:.1f}%",
                        '마지막 업데이트': robot.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                df = pd.DataFrame(location_data)
                
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
                st.warning("위치 정보가 있는 로봇이 없습니다.")
        else:
            st.info("등록된 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"지도 로드 실패: {e}")

def display_location_statistics():
    """위치 통계 표시"""
    st.subheader("📊 위치 통계")
    
    try:
        all_robots = robot_service.get_all_robots()
        robots_with_location = [r for r in all_robots if r.location]
        
        if robots_with_location:
            col1, col2 = st.columns(2)
            
            with col1:
                # 상태별 분포
                status_counts = {}
                for robot in robots_with_location:
                    status = robot.status
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                fig_status = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="위치 추적 중인 로봇 상태 분포"
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # 배터리 레벨 분포
                battery_levels = [robot.battery_level for robot in robots_with_location]
                robot_names = [robot.name for robot in robots_with_location]
                
                fig_battery = px.bar(
                    x=robot_names,
                    y=battery_levels,
                    title="로봇별 배터리 레벨",
                    labels={'x': '로봇 이름', 'y': '배터리 레벨 (%)'}
                )
                fig_battery.update_layout(yaxis=dict(range=[0, 100]))
                st.plotly_chart(fig_battery, use_container_width=True)
            
            # 위치 범위 통계
            st.subheader("📍 위치 범위 통계")
            
            if len(robots_with_location) > 1:
                latitudes = [r.location.latitude for r in robots_with_location]
                longitudes = [r.location.longitude for r in robots_with_location]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("최북단 위도", f"{max(latitudes):.6f}")
                
                with col2:
                    st.metric("최남단 위도", f"{min(latitudes):.6f}")
                
                with col3:
                    st.metric("최동단 경도", f"{max(longitudes):.6f}")
                
                with col4:
                    st.metric("최서단 경도", f"{min(longitudes):.6f}")
                
                # 위치 분포 히트맵 (간단한 버전)
                st.subheader("🔥 위치 분포 히트맵")
                
                # 위도/경도 범위를 그리드로 나누어 분포 계산
                lat_range = max(latitudes) - min(latitudes)
                lon_range = max(longitudes) - min(longitudes)
                
                if lat_range > 0 and lon_range > 0:
                    grid_size = 10
                    lat_step = lat_range / grid_size
                    lon_step = lon_range / grid_size
                    
                    heatmap_data = []
                    for i in range(grid_size):
                        for j in range(grid_size):
                            lat_min = min(latitudes) + i * lat_step
                            lat_max = lat_min + lat_step
                            lon_min = min(longitudes) + j * lon_step
                            lon_max = lon_min + lon_step
                            
                            count = sum(1 for r in robots_with_location 
                                      if lat_min <= r.location.latitude < lat_max 
                                      and lon_min <= r.location.longitude < lon_max)
                            
                            if count > 0:
                                heatmap_data.append({
                                    '위도': (lat_min + lat_max) / 2,
                                    '경도': (lon_min + lon_max) / 2,
                                    '로봇 수': count
                                })
                    
                    if heatmap_data:
                        df_heatmap = pd.DataFrame(heatmap_data)
                        fig_heatmap = px.scatter_mapbox(
                            df_heatmap,
                            lat='위도',
                            lon='경도',
                            size='로봇 수',
                            color='로봇 수',
                            title="로봇 위치 분포 히트맵",
                            mapbox_style="open-street-map"
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
            
        else:
            st.info("위치 정보가 있는 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"위치 통계 로드 실패: {e}")

def display_movement_paths():
    """이동 경로 표시"""
    st.subheader("🛤️ 로봇 이동 경로")
    
    try:
        all_robots = robot_service.get_all_robots()
        robots_with_location = [r for r in all_robots if r.location]
        
        if robots_with_location:
            # 로봇 선택
            selected_robot_id = st.selectbox(
                "이동 경로를 볼 로봇 선택",
                [robot.robot_id for robot in robots_with_location]
            )
            
            if selected_robot_id:
                robot = robot_service.get_robot(selected_robot_id)
                if robot and robot.location:
                    st.markdown(f"### 🤖 {robot.name} 이동 경로")
                    
                    # 현재 위치를 중심으로 지도 생성
                    m = folium.Map(
                        location=[robot.location.latitude, robot.location.longitude],
                        zoom_start=15,
                        tiles='OpenStreetMap'
                    )
                    
                    # 현재 위치 마커
                    folium.Marker(
                        location=[robot.location.latitude, robot.location.longitude],
                        popup=f"현재 위치: {robot.name}",
                        tooltip=f"{robot.name} (현재)",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
                    
                    # 이동 경로 시뮬레이션 (실제로는 히스토리 데이터가 필요)
                    st.info("📝 실제 이동 경로 데이터는 시간별 위치 히스토리가 필요합니다.")
                    
                    # 시뮬레이션된 경로 데이터 생성
                    if st.button("🎯 시뮬레이션 경로 생성"):
                        # 간단한 시뮬레이션 경로
                        path_points = []
                        base_lat, base_lon = robot.location.latitude, robot.location.longitude
                        
                        for i in range(10):
                            # 랜덤한 이동 시뮬레이션
                            import random
                            lat_offset = random.uniform(-0.001, 0.001)
                            lon_offset = random.uniform(-0.001, 0.001)
                            
                            path_points.append([
                                base_lat + lat_offset * i,
                                base_lon + lon_offset * i
                            ])
                        
                        # 경로 라인 그리기
                        folium.PolyLine(
                            locations=path_points,
                            color='blue',
                            weight=3,
                            opacity=0.7
                        ).add_to(m)
                        
                        # 경로 포인트 마커
                        for i, point in enumerate(path_points):
                            folium.CircleMarker(
                                location=point,
                                radius=3,
                                color='blue',
                                fill=True,
                                popup=f"경로 포인트 {i+1}"
                            ).add_to(m)
                        
                        st_folium(m, width=800, height=600)
                        
                        # 이동 통계
                        st.subheader("📊 이동 통계")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("총 이동 거리", "약 150m")
                        
                        with col2:
                            st.metric("평균 속도", "0.5 m/s")
                        
                        with col3:
                            st.metric("이동 시간", "5분")
                    else:
                        st_folium(m, width=800, height=600)
                
                # 이동 패턴 분석
                st.subheader("📈 이동 패턴 분석")
                st.info("이동 패턴 분석 기능은 추가 구현이 필요합니다.")
                
                # 시간대별 이동 빈도 차트 (시뮬레이션)
                time_data = {
                    '시간대': ['00-06', '06-12', '12-18', '18-24'],
                    '이동 빈도': [5, 15, 25, 10]
                }
                df_time = pd.DataFrame(time_data)
                
                fig_time = px.bar(
                    df_time,
                    x='시간대',
                    y='이동 빈도',
                    title="시간대별 이동 빈도"
                )
                st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("위치 정보가 있는 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"이동 경로 로드 실패: {e}")

def display_location_history():
    """위치 히스토리 표시 (추가 기능)"""
    st.subheader("📅 위치 히스토리")
    
    # 날짜 선택
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "시작 날짜",
            value=datetime.now().date() - timedelta(days=7)
        )
    
    with col2:
        end_date = st.date_input(
            "종료 날짜",
            value=datetime.now().date()
        )
    
    if st.button("📊 히스토리 조회"):
        st.info("위치 히스토리 기능은 추가 구현이 필요합니다.")
        
        # 히스토리 데이터 시뮬레이션
        st.subheader("📈 위치 변화 추이")
        
        # 시뮬레이션된 히스토리 데이터
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        history_data = []
        
        for date in dates:
            history_data.append({
                '날짜': date.strftime('%Y-%m-%d'),
                '평균 위도': 37.5665 + (date.day % 10) * 0.0001,
                '평균 경도': 126.9780 + (date.day % 10) * 0.0001,
                '활성 로봇 수': (date.day % 5) + 1
            })
        
        df_history = pd.DataFrame(history_data)
        
        fig_history = px.line(
            df_history,
            x='날짜',
            y=['평균 위도', '평균 경도'],
            title="위치 변화 추이"
        )
        st.plotly_chart(fig_history, use_container_width=True)

if __name__ == "__main__":
    main() 