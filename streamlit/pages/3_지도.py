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
    page_title="지도",
    page_icon="🗺️",
    layout="wide"
)

# 자동 새로고침 (2초마다)
count = st_autorefresh(interval=2000, limit=None, key="map_autorefresh")

def get_robot_locations():
    """로봇 위치 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT robot_name, robot_location_x, robot_location_y, robot_status, robot_battery
        FROM robots 
        WHERE robot_location_x IS NOT NULL AND robot_location_y IS NOT NULL
    """)
    
    locations = cursor.fetchall()
    conn.close()
    
    return locations

def get_detected_objects():
    """탐지된 객체 위치 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.detection_class, d.detection_conf, d.detection_bbox,
               r.robot_location_x, r.robot_location_y, r.robot_name,
               d.detection_created_at
        FROM detection_results d
        JOIN camera c ON d.camera_id = c.camera_id
        JOIN robots r ON c.robot_id = r.robot_id
        WHERE r.robot_location_x IS NOT NULL AND r.robot_location_y IS NOT NULL
        ORDER BY d.detection_created_at DESC
        LIMIT 50
    """)
    
    objects = cursor.fetchall()
    conn.close()
    
    return objects

def create_map_with_robots(robot_locations, detected_objects=None):
    """로봇과 탐지된 객체가 표시된 지도 생성"""
    fig = go.Figure()
    
    # 로봇 위치 표시
    if robot_locations:
        robot_x = [loc[1] for loc in robot_locations]
        robot_y = [loc[2] for loc in robot_locations]
        robot_names = [loc[0] for loc in robot_locations]
        robot_status = [loc[3] for loc in robot_locations]
        robot_battery = [loc[4] for loc in robot_locations]
        
        # 상태별 색상
        colors = []
        for status in robot_status:
            if status == "Online":
                colors.append("green")
            elif status == "Offline":
                colors.append("red")
            else:
                colors.append("orange")
        
        # 로봇 마커 추가
        fig.add_trace(go.Scatter(
            x=robot_x,
            y=robot_y,
            mode='markers+text',
            marker=dict(
                size=15,
                color=colors,
                symbol='circle'
            ),
            text=robot_names,
            textposition="top center",
            name="로봇",
            hovertemplate="<b>%{text}</b><br>" +
                         "상태: %{customdata[0]}<br>" +
                         "배터리: %{customdata[1]}%<br>" +
                         "위치: (%{x}, %{y})<extra></extra>",
            customdata=list(zip(robot_status, robot_battery))
        ))
    
    # 탐지된 객체 표시
    if detected_objects:
        object_x = []
        object_y = []
        object_classes = []
        object_confidences = []
        
        for obj in detected_objects:
            # bbox에서 객체 위치 추정 (실제로는 카메라 각도와 거리 계산 필요)
            robot_x = obj[3]
            robot_y = obj[4]
            bbox = json.loads(obj[2]) if obj[2] else {}
            
            # 간단한 위치 추정 (실제로는 더 정확한 계산 필요)
            object_x.append(robot_x + (bbox.get('x', 0) - 0.5) * 10)
            object_y.append(robot_y + (bbox.get('y', 0) - 0.5) * 10)
            object_classes.append(obj[0])
            object_confidences.append(obj[1])
        
        # 객체 마커 추가
        fig.add_trace(go.Scatter(
            x=object_x,
            y=object_y,
            mode='markers',
            marker=dict(
                size=10,
                color='red',
                symbol='diamond'
            ),
            name="탐지된 객체",
            hovertemplate="<b>%{text}</b><br>" +
                         "신뢰도: %{customdata}%<extra></extra>",
            text=object_classes,
            customdata=object_confidences
        ))
    
    # 지도 레이아웃 설정
    fig.update_layout(
        title="로봇 위치 및 탐지된 객체",
        xaxis_title="X 좌표",
        yaxis_title="Y 좌표",
        width=800,
        height=600,
        showlegend=True
    )
    
    return fig

def main():
    st.title("🗺️ 지도")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["전체 맵", "로봇별 위치", "객체 필터링"])
    
    with tab1:
        st.subheader("📊 전체 맵")
        
        # 필터 옵션
        col1, col2 = st.columns(2)
        
        with col1:
            show_robots = st.checkbox("로봇 위치 표시", value=True)
            show_objects = st.checkbox("탐지된 객체 표시", value=True)
        
        with col2:
            time_filter = st.selectbox(
                "시간 필터",
                ["전체", "최근 1시간", "최근 24시간", "최근 7일"]
            )
        
        # 데이터 가져오기
        robot_locations = get_robot_locations()
        detected_objects = get_detected_objects() if show_objects else None
        
        if robot_locations or detected_objects:
            # 지도 생성
            fig = create_map_with_robots(
                robot_locations if show_robots else None,
                detected_objects
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 통계 정보
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("활성 로봇", len([r for r in robot_locations if r[3] == "Online"]))
            
            with col2:
                st.metric("탐지된 객체", len(detected_objects) if detected_objects else 0)
            
            with col3:
                avg_battery = sum(r[4] for r in robot_locations if r[4] is not None) / len(robot_locations) if robot_locations else 0
                st.metric("평균 배터리", f"{avg_battery:.1f}%")
        
        else:
            st.info("표시할 데이터가 없습니다.")
    
    with tab2:
        st.subheader("🤖 로봇별 위치")
        
        robot_locations = get_robot_locations()
        
        if robot_locations:
            # 로봇별 상세 정보
            for robot in robot_locations:
                with st.expander(f"{robot[0]} - {robot[3]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**위치:** ({robot[1]}, {robot[2]})")
                        st.write(f"**배터리:** {robot[4]}%")
                        
                        # 개별 로봇 지도
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=[robot[1]],
                            y=[robot[2]],
                            mode='markers+text',
                            marker=dict(size=20, color='blue'),
                            text=[robot[0]],
                            textposition="top center"
                        ))
                        
                        fig.update_layout(
                            title=f"{robot[0]} 위치",
                            xaxis_title="X 좌표",
                            yaxis_title="Y 좌표",
                            width=400,
                            height=300
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # 로봇 상태 정보
                        status_color = "green" if robot[3] == "Online" else "red"
                        st.markdown(f"**상태:** <span style='color:{status_color}'>{robot[3]}</span>", unsafe_allow_html=True)
                        
                        # 배터리 게이지
                        battery = robot[4] or 0
                        st.progress(battery / 100, text=f"배터리: {battery}%")
                        
                        # 최근 활동 (가상 데이터)
                        st.write("**최근 활동:**")
                        activities = [
                            "센서 데이터 전송",
                            "경로 이동",
                            "객체 탐지",
                            "충전 완료"
                        ]
                        for activity in activities[:3]:
                            st.write(f"• {activity}")
        
        else:
            st.info("로봇 위치 데이터가 없습니다.")
    
    with tab3:
        st.subheader("🔍 객체 필터링")
        
        detected_objects = get_detected_objects()
        
        if detected_objects:
            # 필터 옵션
            col1, col2 = st.columns(2)
            
            with col1:
                # 객체 클래스 필터
                object_classes = list(set([obj[0] for obj in detected_objects]))
                selected_classes = st.multiselect(
                    "객체 클래스 선택",
                    object_classes,
                    default=object_classes
                )
            
            with col2:
                # 신뢰도 필터
                min_confidence = st.slider("최소 신뢰도", 0.0, 1.0, 0.5, 0.1)
            
            # 필터링된 객체
            filtered_objects = [
                obj for obj in detected_objects
                if obj[0] in selected_classes and obj[1] >= min_confidence
            ]
            
            if filtered_objects:
                # 필터링된 객체 테이블
                object_data = []
                for obj in filtered_objects:
                    object_data.append({
                        '객체': obj[0],
                        '신뢰도': f"{obj[1]:.2f}",
                        '로봇': obj[5],
                        '위치': f"({obj[3]}, {obj[4]})",
                        '시간': obj[6]
                    })
                
                df_objects = pd.DataFrame(object_data)
                st.dataframe(df_objects, use_container_width=True)
                
                # 필터링된 객체 지도
                fig = create_map_with_robots(None, filtered_objects)
                st.plotly_chart(fig, use_container_width=True)
                
                # 통계
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    class_counts = df_objects['객체'].value_counts()
                    fig_pie = px.pie(values=class_counts.values, names=class_counts.index, title="객체 분포")
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    confidence_values = [float(x) for x in df_objects['신뢰도']]
                    fig_hist = px.histogram(x=confidence_values, title="신뢰도 분포", nbins=10)
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col3:
                    st.write("**필터링 결과:**")
                    st.write(f"• 총 객체 수: {len(filtered_objects)}")
                    st.write(f"• 선택된 클래스: {len(selected_classes)}개")
                    st.write(f"• 평균 신뢰도: {sum(confidence_values)/len(confidence_values):.2f}")
            
            else:
                st.info("필터 조건에 맞는 객체가 없습니다.")
        
        else:
            st.info("탐지된 객체가 없습니다.")

if __name__ == "__main__":
    main() 