import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import sqlite3
from datetime import datetime, timedelta
import json
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="분석/리포트",
    page_icon="📊",
    layout="wide"
)

# 자동 새로고침 (10초마다)
count = st_autorefresh(interval=10000, limit=None, key="report_autorefresh")

def get_environmental_data():
    """환경 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sensor_temp, sensor_humid, sensor_press, sensor_created_at, robot_id
        FROM sensor_data 
        WHERE sensor_created_at >= datetime('now', '-7 days')
        ORDER BY sensor_created_at DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    return data

def get_coverage_data():
    """커버리지 맵 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT robot_location_x, robot_location_y, robot_name, robot_status
        FROM robots 
        WHERE robot_location_x IS NOT NULL AND robot_location_y IS NOT NULL
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    return data

def get_hazardous_areas():
    """위험지역 분포 데이터 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
            SELECT d.detection_class, d.detection_conf, r.robot_location_x, r.robot_location_y,
                   d.detection_created_at, r.robot_name
            FROM detection_results d
        JOIN camera c ON d.camera_id = c.camera_id
        JOIN robots r ON c.robot_id = r.robot_id
        WHERE d.detection_class IN ('fire', 'smoke', 'gas', 'hazardous_material')
        ORDER BY d.detection_created_at DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    return data

def get_fault_history():
    """장애/경고 이력 가져오기"""
    conn = sqlite3.connect('robot_monitoring.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT status_event, status_robot, status_created_at, robot_id
        FROM robot_status_history 
        WHERE status_event IN ('error', 'warning', 'fault')
        ORDER BY status_created_at DESC
        LIMIT 100
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    return data

def create_environmental_analysis(data):
    """환경 데이터 분석"""
    if not data:
        return None
    
    df = pd.DataFrame(data, columns=['온도', '습도', '기압', '시간', '로봇ID'])
    df['시간'] = pd.to_datetime(df['시간'])
    
    # 시간별 평균값 계산
    df_hourly = df.groupby(df['시간'].dt.hour).agg({
        '온도': 'mean',
        '습도': 'mean',
        '기압': 'mean'
    }).reset_index()
    
    # 차트 생성
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_hourly['시간'],
        y=df_hourly['온도'],
        mode='lines+markers',
        name='온도',
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=df_hourly['시간'],
        y=df_hourly['습도'],
        mode='lines+markers',
        name='습도',
        line=dict(color='blue'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='환경 데이터 시간별 분석',
        xaxis_title='시간 (시간)',
        yaxis=dict(title='온도 (°C)', side='left'),
        yaxis2=dict(title='습도 (%)', side='right', overlaying='y'),
        height=400
    )
    
    return fig

def create_coverage_heatmap(data):
    """커버리지 맵 히트맵 생성"""
    if not data:
        return None
    
    # 간단한 히트맵 데이터 생성 (실제로는 더 정교한 계산 필요)
    x_coords = [point[0] for point in data]
    y_coords = [point[1] for point in data]
    
    # 그리드 생성
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    # 간단한 커버리지 계산
    coverage_data = []
    for i in range(int(x_min), int(x_max) + 1):
        for j in range(int(y_min), int(y_max) + 1):
            # 각 그리드 포인트에서 가장 가까운 로봇까지의 거리 계산
            min_distance = min([((i - x)**2 + (j - y)**2)**0.5 for x, y in zip(x_coords, y_coords)])
            coverage_data.append([i, j, max(0, 100 - min_distance * 10)])  # 거리에 따른 커버리지
    
    df_coverage = pd.DataFrame(coverage_data, columns=['X', 'Y', 'Coverage'])
    
    # 히트맵 생성
    fig = px.imshow(
        df_coverage.pivot(index='Y', columns='X', values='Coverage'),
        title='로봇 커버리지 맵',
        labels=dict(x='X 좌표', y='Y 좌표', color='커버리지 (%)'),
        color_continuous_scale='viridis'
    )
    
    # 로봇 위치 표시
    for i, point in enumerate(data):
        fig.add_trace(go.Scatter(
            x=[point[0]],
            y=[point[1]],
            mode='markers',
            marker=dict(size=10, color='red', symbol='x'),
            name=f'로봇 {i+1}',
            showlegend=False
        ))
    
    return fig

def create_hazardous_analysis(data):
    """위험지역 분포 분석"""
    if not data:
        return None
    
    df = pd.DataFrame(data, columns=['위험유형', '신뢰도', 'X좌표', 'Y좌표', '시간', '로봇명'])
    df['시간'] = pd.to_datetime(df['시간'])
    
    # 위험유형별 분포
    hazard_counts = df['위험유형'].value_counts()
    
    fig_pie = px.pie(
        values=hazard_counts.values,
        names=hazard_counts.index,
        title='위험지역 유형별 분포'
    )
    
    # 시간별 위험지역 발생 추이
    df_hourly = df.groupby(df['시간'].dt.hour).size().reset_index(name='발생횟수')
    
    fig_trend = px.line(
        df_hourly,
        x='시간',
        y='발생횟수',
        title='시간별 위험지역 발생 추이'
    )
    
    return fig_pie, fig_trend

def create_fault_analysis(data):
    """장애/경고 이력 분석"""
    if not data:
        return None
    
    df = pd.DataFrame(data, columns=['이벤트유형', '로봇상태', '시간', '로봇ID'])
    df['시간'] = pd.to_datetime(df['시간'])
    
    # 이벤트 유형별 분포
    event_counts = df['이벤트유형'].value_counts()
    
    fig_pie = px.pie(
        values=event_counts.values,
        names=event_counts.index,
        title='장애/경고 이벤트 분포'
    )
    
    # 일별 이벤트 발생 추이
    df_daily = df.groupby(df['시간'].dt.date).size().reset_index(name='발생횟수')
    
    fig_trend = px.line(
        df_daily,
        x='시간',
        y='발생횟수',
        title='일별 장애/경고 발생 추이'
    )
    
    return fig_pie, fig_trend

def generate_report():
    """리포트 생성 및 다운로드"""
    # 리포트 데이터 수집
    env_data = get_environmental_data()
    coverage_data = get_coverage_data()
    hazard_data = get_hazardous_areas()
    fault_data = get_fault_history()
    
    # 리포트 내용 생성
    report_content = f"""
# 로봇 관제 시스템 분석 리포트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 환경 데이터 분석
- 총 데이터 포인트: {len(env_data) if env_data else 0}
- 분석 기간: 최근 7일

## 2. 커버리지 분석
- 활성 로봇 수: {len(coverage_data) if coverage_data else 0}
- 커버리지 영역: {len(set([(d[0], d[1]) for d in coverage_data])) if coverage_data else 0} 개 포인트

## 3. 위험지역 분석
- 탐지된 위험지역: {len(hazard_data) if hazard_data else 0} 개
- 위험유형: {len(set([d[0] for d in hazard_data])) if hazard_data else 0} 종류

## 4. 장애/경고 분석
- 총 이벤트: {len(fault_data) if fault_data else 0} 건
- 분석 기간: 최근 100건
    """
    
    return report_content

def main():
    st.title("📊 분석/리포트")
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "환경 데이터 분석", "커버리지 맵 분석", "위험지역 분포", "장애/경고 이력", "리포트 다운로드"
    ])
    
    with tab1:
        st.subheader("🌡️ 환경 데이터 분석")
        
        env_data = get_environmental_data()
        
        if env_data:
            # 환경 데이터 차트
            fig = create_environmental_analysis(env_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # 통계 정보
            df_env = pd.DataFrame(env_data, columns=['온도', '습도', '기압', '시간', '로봇ID'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("평균 온도", f"{df_env['온도'].mean():.1f}°C")
                st.metric("최고 온도", f"{df_env['온도'].max():.1f}°C")
                st.metric("최저 온도", f"{df_env['온도'].min():.1f}°C")
            
            with col2:
                st.metric("평균 습도", f"{df_env['습도'].mean():.1f}%")
                st.metric("최고 습도", f"{df_env['습도'].max():.1f}%")
                st.metric("최저 습도", f"{df_env['습도'].min():.1f}%")
            
            with col3:
                st.metric("평균 기압", f"{df_env['기압'].mean():.1f}hPa")
                st.metric("최고 기압", f"{df_env['기압'].max():.1f}hPa")
                st.metric("최저 기압", f"{df_env['기압'].min():.1f}hPa")
        
        else:
            st.info("환경 데이터가 없습니다.")
    
    with tab2:
        st.subheader("🗺️ 커버리지 맵 분석")
        
        coverage_data = get_coverage_data()
        
        if coverage_data:
            # 커버리지 히트맵
            fig = create_coverage_heatmap(coverage_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # 커버리지 통계
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("활성 로봇", len(coverage_data))
            
            with col2:
                online_robots = len([d for d in coverage_data if d[3] == "Online"])
                st.metric("온라인 로봇", online_robots)
            
            with col3:
                coverage_area = len(set([(d[0], d[1]) for d in coverage_data]))
                st.metric("커버리지 영역", f"{coverage_area} 포인트")
        
        else:
            st.info("커버리지 데이터가 없습니다.")
    
    with tab3:
        st.subheader("⚠️ 위험지역 분포 통계")
        
        hazard_data = get_hazardous_areas()
        
        if hazard_data:
            # 위험지역 분석
            fig_pie, fig_trend = create_hazardous_analysis(hazard_data)
            
            if fig_pie and fig_trend:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.plotly_chart(fig_trend, use_container_width=True)
            
            # 위험지역 통계
            df_hazard = pd.DataFrame(hazard_data, columns=['위험유형', '신뢰도', 'X좌표', 'Y좌표', '시간', '로봇명'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 위험지역", len(hazard_data))
            
            with col2:
                unique_hazards = len(df_hazard['위험유형'].unique())
                st.metric("위험유형", unique_hazards)
            
            with col3:
                avg_confidence = df_hazard['신뢰도'].mean()
                st.metric("평균 신뢰도", f"{avg_confidence:.2f}")
        
        else:
            st.info("위험지역 데이터가 없습니다.")
    
    with tab4:
        st.subheader("🚨 장애/경고 이력")
        
        fault_data = get_fault_history()
        
        if fault_data:
            # 장애/경고 분석
            fig_pie, fig_trend = create_fault_analysis(fault_data)
            
            if fig_pie and fig_trend:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.plotly_chart(fig_trend, use_container_width=True)
            
            # 장애/경고 통계
            df_fault = pd.DataFrame(fault_data, columns=['이벤트유형', '로봇상태', '시간', '로봇ID'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 이벤트", len(fault_data))
            
            with col2:
                error_count = len(df_fault[df_fault['이벤트유형'] == 'error'])
                st.metric("오류", error_count)
            
            with col3:
                warning_count = len(df_fault[df_fault['이벤트유형'] == 'warning'])
                st.metric("경고", warning_count)
            
            # 최근 이벤트 목록
            st.subheader("최근 이벤트 목록")
            recent_events = df_fault.head(10)
            st.dataframe(recent_events, use_container_width=True)
        
        else:
            st.info("장애/경고 이력이 없습니다.")
    
    with tab5:
        st.subheader("📄 리포트 다운로드")
        
        # 리포트 생성
        report_content = generate_report()
        
        # 리포트 미리보기
        st.subheader("리포트 미리보기")
        st.text(report_content)
        
        # 다운로드 버튼
        if st.button("📥 리포트 다운로드"):
            # CSV 데이터도 포함
            env_data = get_environmental_data()
            if env_data:
                df_env = pd.DataFrame(env_data, columns=['온도', '습도', '기압', '시간', '로봇ID'])
                
                # CSV 파일 생성
                csv_buffer = io.StringIO()
                df_env.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                # 다운로드 링크 생성
                b64_csv = base64.b64encode(csv_data.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64_csv}" download="environmental_data.csv">환경 데이터 CSV 다운로드</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            st.success("리포트가 생성되었습니다!")

if __name__ == "__main__":
    main() 