import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from services.robot_service import robot_service
from config import ROBOT_STATUS, ALERT_LEVELS, SENSOR_TYPES

# 페이지 설정
st.set_page_config(
    page_title="분석 리포트",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 분석 리포트")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📈 성능 분석", "🚨 알림 분석", "🔋 배터리 분석", "📋 종합 리포트"])
    
    with tab1:
        display_performance_analysis()
    
    with tab2:
        display_alert_analysis()
    
    with tab3:
        display_battery_analysis()
    
    with tab4:
        display_comprehensive_report()

def display_performance_analysis():
    """성능 분석"""
    st.subheader("📈 로봇 성능 분석")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 기간 선택
            col1, col2 = st.columns(2)
            
            with col1:
                analysis_period = st.selectbox(
                    "분석 기간",
                    ["최근 24시간", "최근 7일", "최근 30일", "전체"]
                )
            
            with col2:
                if st.button("🔄 분석 실행"):
                    st.session_state.analysis_data = generate_performance_data(all_robots, analysis_period)
            
            # 성능 지표 카드
            display_performance_metrics(all_robots)
            
            # 성능 차트
            display_performance_charts(all_robots)
            
            # 로봇별 상세 성능
            display_robot_performance_details(all_robots)
            
        else:
            st.info("분석할 로봇 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"성능 분석 실패: {e}")

def display_performance_metrics(all_robots):
    """성능 지표 카드"""
    st.subheader("📊 주요 성능 지표")
    
    # 온라인율 계산
    online_robots = [r for r in all_robots if r.status == ROBOT_STATUS['ONLINE']]
    online_rate = len(online_robots) / len(all_robots) * 100 if all_robots else 0
    
    # 평균 건강도
    avg_health_score = sum(r.get_health_score() for r in all_robots) / len(all_robots) if all_robots else 0
    
    # 평균 배터리
    avg_battery = sum(r.battery_level for r in all_robots) / len(all_robots) if all_robots else 0
    
    # 정비 필요 로봇 수
    maintenance_needed = sum(1 for r in all_robots if r.needs_maintenance())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "온라인율",
            f"{online_rate:.1f}%",
            delta=f"{len(online_robots)}/{len(all_robots)}"
        )
    
    with col2:
        st.metric(
            "평균 건강도",
            f"{avg_health_score:.1f}%",
            delta="정상" if avg_health_score > 80 else "주의" if avg_health_score > 50 else "위험"
        )
    
    with col3:
        st.metric(
            "평균 배터리",
            f"{avg_battery:.1f}%",
            delta="양호" if avg_battery > 50 else "주의" if avg_battery > 20 else "위험"
        )
    
    with col4:
        st.metric(
            "정비 필요",
            maintenance_needed,
            delta="대기" if maintenance_needed > 0 else "완료"
        )

def display_performance_charts(all_robots):
    """성능 차트"""
    st.subheader("📈 성능 추이 차트")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 상태별 분포
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
        # 건강도 분포
        health_scores = [robot.get_health_score() for robot in all_robots]
        robot_names = [robot.name for robot in all_robots]
        
        fig_health = px.bar(
            x=robot_names,
            y=health_scores,
            title="로봇별 건강도 점수",
            labels={'x': '로봇 이름', 'y': '건강도 점수 (%)'}
        )
        fig_health.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_health, use_container_width=True)
    
    # 시간대별 성능 추이 (시뮬레이션)
    st.subheader("⏰ 시간대별 성능 추이")
    
    time_periods = ['00-06', '06-12', '12-18', '18-24']
    performance_data = {
        '시간대': time_periods,
        '온라인율': [85, 95, 90, 88],
        '평균 배터리': [75, 82, 78, 80],
        '평균 건강도': [88, 92, 89, 91]
    }
    
    df_performance = pd.DataFrame(performance_data)
    
    fig_trend = px.line(
        df_performance,
        x='시간대',
        y=['온라인율', '평균 배터리', '평균 건강도'],
        title="시간대별 성능 지표 추이"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

def display_robot_performance_details(all_robots):
    """로봇별 상세 성능"""
    st.subheader("🤖 로봇별 상세 성능")
    
    # 로봇 선택
    selected_robot_id = st.selectbox(
        "상세 분석할 로봇 선택",
        [robot.robot_id for robot in all_robots]
    )
    
    if selected_robot_id:
        robot = robot_service.get_robot(selected_robot_id)
        if robot:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**기본 정보**")
                st.write(f"로봇 이름: {robot.name}")
                st.write(f"모델: {robot.model}")
                st.write(f"상태: {robot.status}")
                st.write(f"배터리: {robot.battery_level:.1f}%")
                st.write(f"건강도: {robot.get_health_score():.1f}%")
            
            with col2:
                st.write("**성능 지표**")
                
                # 성능 점수 계산
                performance_score = calculate_performance_score(robot)
                st.metric("종합 성능 점수", f"{performance_score:.1f}/100")
                
                # 성능 게이지
                st.progress(performance_score / 100, text=f"성능: {performance_score:.1f}%")
                
                # 개선 권장사항
                recommendations = get_performance_recommendations(robot)
                st.write("**개선 권장사항:**")
                for rec in recommendations:
                    st.write(f"• {rec}")
            
            # 상세 차트
            display_robot_detailed_charts(robot)

def calculate_performance_score(robot):
    """로봇 성능 점수 계산"""
    score = 0
    
    # 상태 점수 (40점)
    if robot.status == ROBOT_STATUS['ONLINE']:
        score += 40
    elif robot.status == ROBOT_STATUS['IDLE']:
        score += 30
    elif robot.status == ROBOT_STATUS['CHARGING']:
        score += 25
    elif robot.status == ROBOT_STATUS['MAINTENANCE']:
        score += 15
    else:
        score += 5
    
    # 배터리 점수 (30점)
    if robot.battery_level >= 80:
        score += 30
    elif robot.battery_level >= 50:
        score += 20
    elif robot.battery_level >= 20:
        score += 10
    else:
        score += 0
    
    # 건강도 점수 (30점)
    health_score = robot.get_health_score()
    score += health_score * 0.3
    
    return min(100, score)

def get_performance_recommendations(robot):
    """성능 개선 권장사항"""
    recommendations = []
    
    if robot.status != ROBOT_STATUS['ONLINE']:
        recommendations.append("온라인 상태로 전환하여 성능 향상")
    
    if robot.battery_level < 50:
        recommendations.append("배터리 충전 필요")
    
    if robot.needs_maintenance():
        recommendations.append("정기 정비 수행 필요")
    
    health_score = robot.get_health_score()
    if health_score < 80:
        recommendations.append("건강도 개선을 위한 점검 필요")
    
    if not recommendations:
        recommendations.append("현재 상태 양호 - 유지 관리 계속")
    
    return recommendations

def display_robot_detailed_charts(robot):
    """로봇 상세 차트"""
    st.subheader("📊 상세 성능 차트")
    
    # 센서 데이터 시뮬레이션
    sensor_data = generate_sensor_data_simulation(robot)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 센서 데이터 추이
        fig_sensor = px.line(
            sensor_data,
            x='시간',
            y='값',
            color='센서',
            title="센서 데이터 추이"
        )
        st.plotly_chart(fig_sensor, use_container_width=True)
    
    with col2:
        # 성능 지표 레이더 차트
        performance_indicators = {
            '온라인율': 85,
            '배터리': robot.battery_level,
            '건강도': robot.get_health_score(),
            '응답성': 90,
            '안정성': 88
        }
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(performance_indicators.values()),
            theta=list(performance_indicators.keys()),
            fill='toself',
            name='성능 지표'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="성능 지표 레이더 차트"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)

def generate_sensor_data_simulation(robot):
    """센서 데이터 시뮬레이션"""
    # 24시간 데이터 생성
    hours = list(range(24))
    data = []
    
    for hour in hours:
        # 온도 데이터
        temp = 20 + 5 * np.sin(hour * np.pi / 12) + np.random.normal(0, 1)
        data.append({'시간': hour, '값': temp, '센서': '온도'})
        
        # 배터리 데이터
        battery = max(0, robot.battery_level - hour * 0.5 + np.random.normal(0, 2))
        data.append({'시간': hour, '값': battery, '센서': '배터리'})
        
        # 신호 강도
        signal = 80 + np.random.normal(0, 5)
        data.append({'시간': hour, '값': signal, '센서': '신호강도'})
    
    return pd.DataFrame(data)

def display_alert_analysis():
    """알림 분석"""
    st.subheader("🚨 알림 분석")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 알림 통계
            display_alert_statistics(all_robots)
            
            # 알림 트렌드
            display_alert_trends()
            
            # 알림 패턴 분석
            display_alert_patterns()
            
        else:
            st.info("분석할 알림 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"알림 분석 실패: {e}")

def display_alert_statistics(all_robots):
    """알림 통계"""
    st.subheader("📊 알림 통계")
    
    # 모든 알림 수집
    all_alerts = []
    for robot in all_robots:
        alerts = robot_service.get_robot_alerts(robot.robot_id)
        all_alerts.extend(alerts)
    
    if all_alerts:
        # 레벨별 알림 수
        level_counts = {}
        for alert in all_alerts:
            level = alert.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_level = px.pie(
                values=list(level_counts.values()),
                names=list(level_counts.keys()),
                title="알림 레벨별 분포"
            )
            st.plotly_chart(fig_level, use_container_width=True)
        
        with col2:
            # 해결된 알림 vs 미해결 알림
            resolved_count = sum(1 for alert in all_alerts if alert.resolved)
            unresolved_count = len(all_alerts) - resolved_count
            
            fig_resolution = px.pie(
                values=[resolved_count, unresolved_count],
                names=['해결됨', '미해결'],
                title="알림 해결 상태"
            )
            st.plotly_chart(fig_resolution, use_container_width=True)
        
        # 알림 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 알림 수", len(all_alerts))
        
        with col2:
            st.metric("해결된 알림", resolved_count)
        
        with col3:
            resolution_rate = resolved_count / len(all_alerts) * 100 if all_alerts else 0
            st.metric("해결율", f"{resolution_rate:.1f}%")
        
        with col4:
            critical_alerts = sum(1 for alert in all_alerts if alert.level == ALERT_LEVELS['CRITICAL'])
            st.metric("긴급 알림", critical_alerts)
    else:
        st.success("현재 알림이 없습니다.")

def display_alert_trends():
    """알림 트렌드"""
    st.subheader("📈 알림 트렌드")
    
    # 시뮬레이션된 알림 트렌드 데이터
    days = list(range(1, 31))
    alert_trend_data = {
        '일': days,
        '총 알림': [5, 8, 3, 12, 7, 4, 9, 6, 11, 8, 5, 7, 10, 6, 4, 8, 12, 9, 7, 5, 6, 8, 11, 7, 4, 9, 6, 8, 5, 7],
        '긴급 알림': [1, 2, 0, 3, 1, 0, 2, 1, 3, 2, 1, 1, 2, 1, 0, 2, 3, 2, 1, 1, 1, 2, 3, 1, 0, 2, 1, 2, 1, 1]
    }
    
    df_trend = pd.DataFrame(alert_trend_data)
    
    fig_trend = px.line(
        df_trend,
        x='일',
        y=['총 알림', '긴급 알림'],
        title="일별 알림 발생 추이"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

def display_alert_patterns():
    """알림 패턴 분석"""
    st.subheader("🔍 알림 패턴 분석")
    
    # 시간대별 알림 발생 패턴
    hours = list(range(24))
    alert_pattern_data = {
        '시간': hours,
        '알림 수': [2, 1, 0, 0, 1, 3, 8, 12, 15, 18, 20, 22, 25, 23, 21, 19, 17, 15, 12, 10, 8, 6, 4, 3]
    }
    
    df_pattern = pd.DataFrame(alert_pattern_data)
    
    fig_pattern = px.bar(
        df_pattern,
        x='시간',
        y='알림 수',
        title="시간대별 알림 발생 패턴"
    )
    st.plotly_chart(fig_pattern, use_container_width=True)

def display_battery_analysis():
    """배터리 분석"""
    st.subheader("🔋 배터리 분석")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 배터리 통계
            display_battery_statistics(all_robots)
            
            # 배터리 사용 패턴
            display_battery_usage_patterns()
            
            # 충전 효율성 분석
            display_charging_efficiency()
            
        else:
            st.info("분석할 배터리 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"배터리 분석 실패: {e}")

def display_battery_statistics(all_robots):
    """배터리 통계"""
    st.subheader("📊 배터리 통계")
    
    battery_levels = [robot.battery_level for robot in all_robots]
    robot_names = [robot.name for robot in all_robots]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 배터리 레벨 분포
        fig_distribution = px.histogram(
            x=battery_levels,
            title="배터리 레벨 분포",
            labels={'x': '배터리 레벨 (%)', 'y': '로봇 수'}
        )
        st.plotly_chart(fig_distribution, use_container_width=True)
    
    with col2:
        # 로봇별 배터리 상태
        fig_battery = px.bar(
            x=robot_names,
            y=battery_levels,
            title="로봇별 배터리 레벨",
            labels={'x': '로봇 이름', 'y': '배터리 레벨 (%)'}
        )
        fig_battery.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_battery, use_container_width=True)
    
    # 배터리 지표
    avg_battery = sum(battery_levels) / len(battery_levels)
    low_battery_count = sum(1 for level in battery_levels if level < 20)
    critical_battery_count = sum(1 for level in battery_levels if level < 10)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("평균 배터리", f"{avg_battery:.1f}%")
    
    with col2:
        st.metric("낮은 배터리", low_battery_count)
    
    with col3:
        st.metric("위험 배터리", critical_battery_count)
    
    with col4:
        battery_health = "양호" if avg_battery > 70 else "주의" if avg_battery > 40 else "위험"
        st.metric("배터리 상태", battery_health)

def display_battery_usage_patterns():
    """배터리 사용 패턴"""
    st.subheader("📈 배터리 사용 패턴")
    
    # 시뮬레이션된 배터리 사용 패턴
    hours = list(range(24))
    usage_pattern_data = {
        '시간': hours,
        '평균 배터리': [85, 83, 81, 79, 77, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 0, 0, 0, 0]
    }
    
    df_usage = pd.DataFrame(usage_pattern_data)
    
    fig_usage = px.line(
        df_usage,
        x='시간',
        y='평균 배터리',
        title="24시간 배터리 사용 패턴"
    )
    fig_usage.update_layout(yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_usage, use_container_width=True)

def display_charging_efficiency():
    """충전 효율성 분석"""
    st.subheader("⚡ 충전 효율성 분석")
    
    # 시뮬레이션된 충전 데이터
    charging_data = {
        '로봇': ['Robot-01', 'Robot-02', 'Robot-03', 'Robot-04', 'Robot-05'],
        '충전 시간': [2.5, 3.0, 2.8, 2.2, 3.2],
        '충전 효율': [95, 88, 92, 98, 85]
    }
    
    df_charging = pd.DataFrame(charging_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_time = px.bar(
            df_charging,
            x='로봇',
            y='충전 시간',
            title="로봇별 충전 시간 (시간)"
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        fig_efficiency = px.bar(
            df_charging,
            x='로봇',
            y='충전 효율',
            title="로봇별 충전 효율 (%)"
        )
        fig_efficiency.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_efficiency, use_container_width=True)

def display_comprehensive_report():
    """종합 리포트"""
    st.subheader("📋 종합 분석 리포트")
    
    try:
        all_robots = robot_service.get_all_robots()
        
        if all_robots:
            # 리포트 생성 버튼
            if st.button("📊 종합 리포트 생성"):
                generate_comprehensive_report(all_robots)
            
            # 리포트 미리보기
            display_report_preview(all_robots)
            
        else:
            st.info("리포트를 생성할 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"종합 리포트 생성 실패: {e}")

def generate_comprehensive_report(all_robots):
    """종합 리포트 생성"""
    st.success("📋 종합 리포트가 생성되었습니다!")
    
    # 리포트 내용
    report_data = {
        '생성일': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '분석 대상': f"{len(all_robots)}개 로봇",
        '평균 온라인율': f"{len([r for r in all_robots if r.status == 'online']) / len(all_robots) * 100:.1f}%",
        '평균 배터리': f"{sum(r.battery_level for r in all_robots) / len(all_robots):.1f}%",
        '평균 건강도': f"{sum(r.get_health_score() for r in all_robots) / len(all_robots):.1f}%",
        '정비 필요': f"{sum(1 for r in all_robots if r.needs_maintenance())}개"
    }
    
    # 리포트 표시
    st.subheader("📊 종합 성과 지표")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        for key, value in list(report_data.items())[:2]:
            st.write(f"**{key}:** {value}")
    
    with col2:
        for key, value in list(report_data.items())[2:4]:
            st.write(f"**{key}:** {value}")
    
    with col3:
        for key, value in list(report_data.items())[4:]:
            st.write(f"**{key}:** {value}")
    
    # 권장사항
    st.subheader("💡 개선 권장사항")
    
    recommendations = []
    
    # 배터리 관련 권장사항
    low_battery_count = sum(1 for r in all_robots if r.battery_level < 20)
    if low_battery_count > 0:
        recommendations.append(f"배터리 레벨이 낮은 로봇 {low_battery_count}개에 대한 충전 필요")
    
    # 정비 관련 권장사항
    maintenance_needed = sum(1 for r in all_robots if r.needs_maintenance())
    if maintenance_needed > 0:
        recommendations.append(f"정비가 필요한 로봇 {maintenance_needed}개에 대한 정비 계획 수립")
    
    # 온라인율 관련 권장사항
    offline_count = len(all_robots) - len([r for r in all_robots if r.status == 'online'])
    if offline_count > 0:
        recommendations.append(f"오프라인 상태인 로봇 {offline_count}개에 대한 연결 상태 점검")
    
    if not recommendations:
        recommendations.append("현재 모든 로봇이 정상 상태입니다.")
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

def display_report_preview(all_robots):
    """리포트 미리보기"""
    st.subheader("👀 리포트 미리보기")
    
    # 요약 통계
    st.write("**📈 주요 지표 요약**")
    
    online_count = len([r for r in all_robots if r.status == 'online'])
    avg_battery = sum(r.battery_level for r in all_robots) / len(all_robots)
    avg_health = sum(r.get_health_score() for r in all_robots) / len(all_robots)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("온라인 로봇", f"{online_count}/{len(all_robots)}")
    
    with col2:
        st.metric("평균 배터리", f"{avg_battery:.1f}%")
    
    with col3:
        st.metric("평균 건강도", f"{avg_health:.1f}%")
    
    # 상세 분석
    st.write("**🔍 상세 분석**")
    
    # 로봇별 상태 요약
    robot_summary = []
    for robot in all_robots:
        robot_summary.append({
            '로봇 이름': robot.name,
            '상태': robot.status,
            '배터리': f"{robot.battery_level:.1f}%",
            '건강도': f"{robot.get_health_score():.1f}%",
            '정비 필요': "예" if robot.needs_maintenance() else "아니오"
        })
    
    df_summary = pd.DataFrame(robot_summary)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main() 