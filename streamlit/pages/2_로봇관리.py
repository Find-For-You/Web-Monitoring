import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import sqlite3
from datetime import datetime, timedelta
import json

# 페이지 설정
st.set_page_config(
    page_title="로봇 관리",
    page_icon="🤖",
    layout="wide"
)

# 자동 새로고침 (3초마다)
count = st_autorefresh(interval=3000, limit=None, key="robot_autorefresh")

def get_robots():
    """로봇 목록 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT robot_id, robot_name, robot_status, robot_battery, 
               robot_connection, robot_ping, robot_location_x, robot_location_y,
               robot_created_at, robot_update_at
        FROM robots
        ORDER BY robot_name
    """)
    
    robots = cursor.fetchall()
    conn.close()
    
    return robots

def get_robot_sensors(robot_id):
    """로봇 센서 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sensor_temp, sensor_humid, sensor_press, sensor_created_at
        FROM sensor_data 
        WHERE robot_id = ?
        ORDER BY sensor_created_at DESC
        LIMIT 50
    """, (robot_id,))
    
    sensors = cursor.fetchall()
    conn.close()
    
    return sensors

def get_detection_results(robot_id):
    """YOLO 탐지 결과 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
            SELECT d.detection_class, d.detection_conf, d.detection_bbox,
                   c.camera_name, d.detection_created_at
            FROM detection_results d
        JOIN camera c ON d.camera_id = c.camera_id
        JOIN robots r ON c.robot_id = r.robot_id
        WHERE r.robot_id = ?
        ORDER BY d.detection_created_at DESC
        LIMIT 20
    """, (robot_id,))
    
    detections = cursor.fetchall()
    conn.close()
    
    return detections

def send_robot_command(robot_id, command_type, command_detail):
    """로봇 명령 전송"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO command_history (robot_id, user_id, command_type, command_detail, command_created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (robot_id, st.session_state.user_id, command_type, json.dumps(command_detail), datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def main():
    st.title("🤖 로봇 관리")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["로봇 목록", "실시간 제어", "센서 상태", "YOLO 탐지"])
    
    with tab1:
        st.subheader("📋 로봇 목록")
        
        robots = get_robots()
        
        if robots:
            # 로봇 상태 테이블
            robot_data = []
            for robot in robots:
                status_icon = "🟢" if robot[2] == "Online" else "🔴"
                robot_data.append({
                    '상태': status_icon,
                    '로봇명': robot[1],
                    '상태': robot[2],
                    '배터리(%)': robot[3] or 0,
                    '연결': robot[4] or 0,
                    '핑(ms)': robot[5] or 0,
                    'X좌표': robot[6] or 0,
                    'Y좌표': robot[7] or 0
                })
            
            df_robots = pd.DataFrame(robot_data)
            st.dataframe(df_robots, use_container_width=True)
            
            # 로봇 추가/삭제
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("➕ 로봇 추가")
                with st.form("add_robot"):
                    robot_name = st.text_input("로봇명")
                    project_id = st.selectbox("프로젝트", [1, 2, 3])  # 실제로는 DB에서 가져와야 함
                    submit_add = st.form_submit_button("로봇 추가")
                    
                    if submit_add and robot_name:
                        # 로봇 추가 로직
                        st.success(f"{robot_name} 로봇이 추가되었습니다.")
            
            with col2:
                st.subheader("🗑️ 로봇 삭제")
                robot_names = [robot[1] for robot in robots]
                selected_robot = st.selectbox("삭제할 로봇 선택", robot_names)
                
                if st.button("로봇 삭제"):
                    st.warning(f"{selected_robot} 로봇을 삭제하시겠습니까?")
        
        else:
            st.info("등록된 로봇이 없습니다.")
    
    with tab2:
        st.subheader("🎮 실시간 제어")
        
        if robots:
            # 로봇 선택
            robot_names = [robot[1] for robot in robots]
            selected_robot = st.selectbox("제어할 로봇 선택", robot_names)
            
            # 선택된 로봇 정보
            selected_robot_data = next((robot for robot in robots if robot[1] == selected_robot), None)
            
            if selected_robot_data:
                robot_id = selected_robot_data[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("수동 제어")
                    
                    # 이동 제어
                    st.write("**이동 제어**")
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        x_speed = st.slider("X축 속도", -100, 100, 0)
                    with col_y:
                        y_speed = st.slider("Y축 속도", -100, 100, 0)
                    
                    if st.button("이동 명령 전송"):
                        command_detail = {"x_speed": x_speed, "y_speed": y_speed}
                        if send_robot_command(robot_id, "MOVE", command_detail):
                            st.success("이동 명령이 전송되었습니다.")
                        else:
                            st.error("명령 전송에 실패했습니다.")
                    
                    # 비상 정지
                    if st.button("🚨 비상 정지", type="primary"):
                        if send_robot_command(robot_id, "EMERGENCY_STOP", {}):
                            st.success("비상 정지 명령이 전송되었습니다.")
                        else:
                            st.error("명령 전송에 실패했습니다.")
                
                with col2:
                    st.subheader("로봇 정보")
                    st.write(f"**로봇명:** {selected_robot_data[1]}")
                    st.write(f"**상태:** {selected_robot_data[2]}")
                    st.write(f"**배터리:** {selected_robot_data[3] or 0}%")
                    st.write(f"**연결:** {selected_robot_data[4] or 0}")
                    st.write(f"**핑:** {selected_robot_data[5] or 0}ms")
                    st.write(f"**위치:** ({selected_robot_data[6] or 0}, {selected_robot_data[7] or 0})")
        
        else:
            st.info("제어할 로봇이 없습니다.")
    
    with tab3:
        st.subheader("📊 센서 상태")
        
        if robots:
            selected_robot = st.selectbox("센서 데이터를 볼 로봇 선택", [robot[1] for robot in robots])
            selected_robot_data = next((robot for robot in robots if robot[1] == selected_robot), None)
            
            if selected_robot_data:
                robot_id = selected_robot_data[0]
                sensors = get_robot_sensors(robot_id)
                
                if sensors:
                    # 센서 데이터 차트
                    sensor_df = pd.DataFrame(sensors, columns=['온도', '습도', '기압', '시간'])
                    sensor_df['시간'] = pd.to_datetime(sensor_df['시간'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_temp = px.line(sensor_df, x='시간', y='온도', title='온도 변화')
                        st.plotly_chart(fig_temp, use_container_width=True)
                        
                        fig_humid = px.line(sensor_df, x='시간', y='습도', title='습도 변화')
                        st.plotly_chart(fig_humid, use_container_width=True)
                    
                    with col2:
                        fig_press = px.line(sensor_df, x='시간', y='기압', title='기압 변화')
                        st.plotly_chart(fig_press, use_container_width=True)
                        
                        # 현재 센서 값
                        latest_sensor = sensors[0]
                        st.subheader("현재 센서 값")
                        st.metric("온도", f"{latest_sensor[0]}°C")
                        st.metric("습도", f"{latest_sensor[1]}%")
                        st.metric("기압", f"{latest_sensor[2]}hPa")
                else:
                    st.info("센서 데이터가 없습니다.")
        
        else:
            st.info("센서 데이터를 볼 로봇이 없습니다.")
    
    with tab4:
        st.subheader("👁️ YOLO 탐지 결과")
        
        if robots:
            selected_robot = st.selectbox("탐지 결과를 볼 로봇 선택", [robot[1] for robot in robots])
            selected_robot_data = next((robot for robot in robots if robot[1] == selected_robot), None)
            
            if selected_robot_data:
                robot_id = selected_robot_data[0]
                detections = get_detection_results(robot_id)
                
                if detections:
                    # 탐지 결과 테이블
                    detection_data = []
                    for detection in detections:
                        bbox = json.loads(detection[2]) if detection[2] else {}
                        detection_data.append({
                            '객체': detection[0],
                            '신뢰도': f"{detection[1]:.2f}",
                            '카메라': detection[3],
                            '시간': detection[4]
                        })
                    
                    df_detections = pd.DataFrame(detection_data)
                    st.dataframe(df_detections, use_container_width=True)
                    
                    # 탐지 통계
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        class_counts = df_detections['객체'].value_counts()
                        fig_pie = px.pie(values=class_counts.values, names=class_counts.index, title="탐지된 객체 분포")
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # 신뢰도 분포
                        confidence_values = [float(x.replace('%', '')) for x in df_detections['신뢰도']]
                        fig_hist = px.histogram(x=confidence_values, title="신뢰도 분포", nbins=10)
                        st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.info("탐지 결과가 없습니다.")
        
        else:
            st.info("탐지 결과를 볼 로봇이 없습니다.")

if __name__ == "__main__":
    main() 