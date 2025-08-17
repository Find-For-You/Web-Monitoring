import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from services.robot_service import robot_service
from utils.stream_utils import StreamUtils
from config import ROBOT_STATUS, SENSOR_TYPES, ALERT_LEVELS

# 페이지 설정
st.set_page_config(
    page_title="로봇 관리",
    page_icon="🔧",
    layout="wide"
)

def main():
    st.title("🔧 로봇 관리")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📋 로봇 목록", "➕ 로봇 등록", "📊 상세 모니터링", "⚙️ 설정 관리"])
    
    with tab1:
        display_robot_list()
    
    with tab2:
        display_robot_registration()
    
    with tab3:
        display_detailed_monitoring()
    
    with tab4:
        display_settings_management()

def display_robot_list():
    """로봇 목록 표시"""
    st.subheader("📋 로봇 목록")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 검색 및 필터링
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("🔍 로봇 검색", placeholder="로봇 이름 또는 ID")
            
            with col2:
                status_filter = st.selectbox(
                    "📊 상태 필터",
                    ["전체"] + list(ROBOT_STATUS.values())
                )
            
            with col3:
                battery_filter = st.selectbox(
                    "🔋 배터리 필터",
                    ["전체", "낮음 (<20%)", "보통 (20-80%)", "높음 (>80%)"]
                )
            
            # 필터링 적용
            filtered_robots = all_robots
            
            if search_term:
                filtered_robots = [r for r in filtered_robots 
                                 if search_term.lower() in r.name.lower() 
                                 or search_term.lower() in r.robot_id.lower()]
            
            if status_filter != "전체":
                filtered_robots = [r for r in filtered_robots if r.status == status_filter]
            
            if battery_filter != "전체":
                if battery_filter == "낮음 (<20%)":
                    filtered_robots = [r for r in filtered_robots if r.battery_level < 20]
                elif battery_filter == "보통 (20-80%)":
                    filtered_robots = [r for r in filtered_robots if 20 <= r.battery_level <= 80]
                elif battery_filter == "높음 (>80%)":
                    filtered_robots = [r for r in filtered_robots if r.battery_level > 80]
            
            # 로봇 데이터 테이블 생성
            robot_data = []
            for robot in filtered_robots:
                health_score = robot.get_health_score()
                
                robot_data.append({
                    '로봇 ID': robot.robot_id,
                    '이름': robot.name,
                    '모델': robot.model,
                    '상태': robot.status,
                    '배터리': f"{robot.battery_level:.1f}%",
                    '건강도': f"{health_score:.1f}%",
                    '위치': f"{robot.location.latitude:.4f}, {robot.location.longitude:.4f}" if robot.location else "N/A",
                    '마지막 업데이트': robot.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    '정비 필요': "예" if robot.needs_maintenance() else "아니오"
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
            
            # 선택된 로봇 상세 정보
            if st.button("📊 선택된 로봇 상세 정보 보기"):
                selected_robot_id = st.selectbox(
                    "로봇 선택",
                    [robot.robot_id for robot in filtered_robots]
                )
                
                if selected_robot_id:
                    display_robot_details(selected_robot_id)
        else:
            st.info("등록된 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"로봇 목록 로드 실패: {e}")

def display_robot_registration():
    """로봇 등록 폼"""
    st.subheader("➕ 로봇 등록")
    
    with st.form("robot_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            robot_name = st.text_input("로봇 이름 *", placeholder="예: 탐색로봇-01")
            robot_model = st.text_input("모델명 *", placeholder="예: Explorer-X1")
            manufacturer = st.text_input("제조사", placeholder="예: RobotCorp")
            serial_number = st.text_input("시리얼 번호", placeholder="예: SN2024001")
        
        with col2:
            description = st.text_area("설명", placeholder="로봇에 대한 설명을 입력하세요")
            firmware_version = st.text_input("펌웨어 버전", placeholder="예: v2.1.0")
            initial_status = st.selectbox("초기 상태", list(ROBOT_STATUS.values()))
            initial_battery = st.slider("초기 배터리 레벨 (%)", 0, 100, 100)
        
        # 위치 정보
        st.subheader("📍 초기 위치 설정")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latitude = st.number_input("위도", min_value=-90.0, max_value=90.0, value=37.5665, format="%.6f")
        
        with col2:
            longitude = st.number_input("경도", min_value=-180.0, max_value=180.0, value=126.9780, format="%.6f")
        
        with col3:
            altitude = st.number_input("고도 (m)", min_value=0.0, value=0.0, format="%.1f")
        
        # 센서 설정
        st.subheader("📡 센서 설정")
        sensor_types = st.multiselect(
            "장착된 센서",
            list(SENSOR_TYPES.values()),
            default=[SENSOR_TYPES['BATTERY'], SENSOR_TYPES['GPS']]
        )
        
        # 카메라 스트림 설정
        st.subheader("📹 카메라 스트림 설정")
        col1, col2 = st.columns(2)
        
        with col1:
            stream_url = st.text_input("스트림 URL", placeholder="https://example.com/stream/robot1")
            stream_type = st.selectbox("스트림 타입", ["http", "rtsp", "webrtc"])
        
        with col2:
            stream_quality = st.selectbox("스트림 품질", ["low", "medium", "high"])
            enable_stream = st.checkbox("스트림 활성화", value=True)
        
        submitted = st.form_submit_button("🚀 로봇 등록")
        
        if submitted:
            if robot_name and robot_model:
                try:
                    # 로봇 생성
                    robot = robot_service.create_robot(
                        name=robot_name,
                        model=robot_model,
                        status=initial_status,
                        battery_level=initial_battery,
                        description=description,
                        manufacturer=manufacturer,
                        serial_number=serial_number,
                        firmware_version=firmware_version,
                        sensors=sensor_types
                    )
                    
                    # 위치 설정
                    if latitude and longitude:
                        robot_service.update_robot_location(
                            robot.robot_id, 
                            latitude, 
                            longitude, 
                            altitude if altitude > 0 else None
                        )
                    
                    # 카메라 스트림 추가
                    if enable_stream and stream_url:
                        if StreamUtils.validate_stream_url(stream_url):
                            robot_service.add_camera_stream(
                                robot.robot_id,
                                stream_url,
                                stream_type,
                                stream_quality
                            )
                        else:
                            st.warning("유효하지 않은 스트림 URL입니다.")
                    
                    st.success(f"✅ 로봇 '{robot_name}'이 성공적으로 등록되었습니다!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"로봇 등록 실패: {e}")
            else:
                st.error("필수 필드를 입력해주세요.")

def display_detailed_monitoring():
    """상세 모니터링"""
    st.subheader("📊 상세 모니터링")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            selected_robot_id = st.selectbox(
                "모니터링할 로봇 선택",
                [robot.robot_id for robot in all_robots]
            )
            
            if selected_robot_id:
                robot = robot_service.get_robot(selected_robot_id)
                if robot:
                    display_robot_monitoring(robot)
        else:
            st.info("모니터링할 로봇이 없습니다.")
            
    except Exception as e:
        st.error(f"모니터링 데이터 로드 실패: {e}")

def display_robot_monitoring(robot):
    """개별 로봇 모니터링"""
    st.markdown(f"### 🤖 {robot.name} ({robot.robot_id})")
    
    # 상태 정보 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "🟢" if robot.status == "online" else "🔴"
        st.metric("상태", f"{status_color} {robot.status}")
    
    with col2:
        battery_color = "🔴" if robot.battery_level < 20 else "🟡" if robot.battery_level < 50 else "🟢"
        st.metric("배터리", f"{battery_color} {robot.battery_level:.1f}%")
    
    with col3:
        health_score = robot.get_health_score()
        health_color = "🔴" if health_score < 50 else "🟡" if health_score < 80 else "🟢"
        st.metric("건강도", f"{health_color} {health_score:.1f}%")
    
    with col4:
        maintenance_status = "🔧 필요" if robot.needs_maintenance() else "✅ 정상"
        st.metric("정비 상태", maintenance_status)
    
    # 탭으로 세부 정보 분리
    tab1, tab2, tab3, tab4 = st.tabs(["📍 위치", "📡 센서", "📹 카메라", "🚨 알림"])
    
    with tab1:
        display_location_info(robot)
    
    with tab2:
        display_sensor_info(robot)
    
    with tab3:
        display_camera_info(robot)
    
    with tab4:
        display_alert_info(robot)

def display_location_info(robot):
    """위치 정보 표시"""
    if robot.location:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**현재 위치:**")
            st.write(f"위도: {robot.location.latitude:.6f}")
            st.write(f"경도: {robot.location.longitude:.6f}")
            if robot.location.altitude:
                st.write(f"고도: {robot.location.altitude:.1f}m")
            if robot.location.timestamp:
                st.write(f"업데이트: {robot.location.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            # 간단한 지도 표시 (실제로는 folium 등을 사용)
            st.write("**위치 지도**")
            st.info("지도 표시 기능은 추가 구현이 필요합니다.")
    else:
        st.warning("위치 정보가 없습니다.")

def display_sensor_info(robot):
    """센서 정보 표시"""
    st.write("**장착된 센서:**")
    
    if robot.sensors:
        for sensor in robot.sensors:
            st.write(f"• {sensor}")
    else:
        st.info("등록된 센서가 없습니다.")
    
    # 센서 데이터 차트 (실제 데이터가 있을 때)
    st.subheader("📈 센서 데이터 추이")
    st.info("실시간 센서 데이터 차트는 추가 구현이 필요합니다.")

def display_camera_info(robot):
    """카메라 정보 표시"""
    streams = robot_service.get_robot_camera_streams(robot.robot_id)
    
    if streams:
        for stream in streams:
            with st.expander(f"📹 스트림: {stream.stream_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**URL:** {stream.stream_url}")
                    st.write(f"**타입:** {stream.stream_type}")
                    st.write(f"**품질:** {stream.quality}")
                    st.write(f"**상태:** {'🟢 활성' if stream.is_active else '🔴 비활성'}")
                
                with col2:
                    if st.button(f"🔗 스트림 테스트", key=f"test_{stream.stream_id}"):
                        if StreamUtils.test_stream_connection(stream.stream_url):
                            st.success("✅ 스트림 연결 성공!")
                        else:
                            st.error("❌ 스트림 연결 실패!")
                    
                    if st.button(f"📸 스냅샷 캡처", key=f"capture_{stream.stream_id}"):
                        frame = StreamUtils.capture_frame(stream.stream_url)
                        if frame is not None:
                            st.image(frame, caption="캡처된 이미지", use_column_width=True)
                        else:
                            st.error("이미지 캡처 실패!")
    else:
        st.info("등록된 카메라 스트림이 없습니다.")

def display_alert_info(robot):
    """알림 정보 표시"""
    alerts = robot_service.get_robot_alerts(robot.robot_id)
    
    if alerts:
        alert_data = []
        for alert in alerts:
            alert_data.append({
                '알림 ID': alert.alert_id,
                '레벨': alert.level,
                '메시지': alert.message,
                '시간': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                '해결됨': '예' if alert.resolved else '아니오'
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
        
        # 알림 해결 기능
        unresolved_alerts = [alert for alert in alerts if not alert.resolved]
        if unresolved_alerts:
            st.subheader("🔧 알림 해결")
            alert_to_resolve = st.selectbox(
                "해결할 알림 선택",
                [alert.alert_id for alert in unresolved_alerts]
            )
            
            if st.button("✅ 알림 해결"):
                if robot_service.resolve_alert(alert_to_resolve, "관리자"):
                    st.success("알림이 해결되었습니다!")
                    st.rerun()
                else:
                    st.error("알림 해결에 실패했습니다.")
    else:
        st.success("현재 활성 알림이 없습니다.")

def display_settings_management():
    """설정 관리"""
    st.subheader("⚙️ 설정 관리")
    
    # 시스템 설정
    st.write("**시스템 설정**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**모니터링 설정**")
        refresh_interval = st.slider("새로고침 간격 (초)", 5, 60, 10)
        alert_threshold = st.slider("알림 임계값 (%)", 10, 50, 20)
    
    with col2:
        st.write("**스트림 설정**")
        default_quality = st.selectbox("기본 스트림 품질", ["low", "medium", "high"])
        max_fps = st.slider("최대 FPS", 10, 60, 30)
    
    if st.button("💾 설정 저장"):
        st.success("설정이 저장되었습니다!")
    
    # 데이터 관리
    st.subheader("🗄️ 데이터 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 데이터 백업"):
            st.info("데이터 백업 기능은 추가 구현이 필요합니다.")
        
        if st.button("🗑️ 오래된 데이터 정리"):
            st.info("데이터 정리 기능은 추가 구현이 필요합니다.")
    
    with col2:
        if st.button("📈 통계 리포트 생성"):
            st.info("리포트 생성 기능은 추가 구현이 필요합니다.")
        
        if st.button("🔄 시스템 재시작"):
            st.warning("시스템 재시작 기능은 추가 구현이 필요합니다.")

def display_robot_details(robot_id):
    """로봇 상세 정보 표시"""
    robot = robot_service.get_robot(robot_id)
    if robot:
        st.subheader(f"📋 {robot.name} 상세 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**기본 정보**")
            st.write(f"로봇 ID: {robot.robot_id}")
            st.write(f"이름: {robot.name}")
            st.write(f"모델: {robot.model}")
            st.write(f"제조사: {robot.manufacturer or 'N/A'}")
            st.write(f"시리얼 번호: {robot.serial_number or 'N/A'}")
            st.write(f"펌웨어 버전: {robot.firmware_version or 'N/A'}")
        
        with col2:
            st.write("**운영 정보**")
            st.write(f"상태: {robot.status}")
            st.write(f"배터리: {robot.battery_level:.1f}%")
            st.write(f"총 운영 시간: {robot.total_operating_hours:.1f}시간")
            st.write(f"마지막 정비: {robot.last_maintenance.strftime('%Y-%m-%d') if robot.last_maintenance else 'N/A'}")
            st.write(f"다음 정비: {robot.next_maintenance.strftime('%Y-%m-%d') if robot.next_maintenance else 'N/A'}")
        
        if robot.description:
            st.write("**설명**")
            st.write(robot.description)

if __name__ == "__main__":
    main() 