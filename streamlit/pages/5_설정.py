import streamlit as st
import json
import os
from datetime import datetime
from config import ROBOT_STATUS, ALERT_LEVELS, SENSOR_TYPES, CAMERA_STREAM_CONFIG

# 페이지 설정
st.set_page_config(
    page_title="설정",
    page_icon="⚙️",
    layout="wide"
)

def main():
    st.title("⚙️ 시스템 설정")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 일반 설정", "🚨 알림 설정", "📹 스트림 설정", "🔐 보안 설정"])
    
    with tab1:
        display_general_settings()
    
    with tab2:
        display_alert_settings()
    
    with tab3:
        display_stream_settings()
    
    with tab4:
        display_security_settings()

def display_general_settings():
    """일반 설정"""
    st.subheader("🔧 일반 설정")
    
    # 시스템 정보
    st.write("**시스템 정보**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        system_name = st.text_input("시스템 이름", value="AI 지능형 정보 탐색 로봇 모니터링 시스템")
        system_version = st.text_input("시스템 버전", value="1.0.0")
        timezone = st.selectbox("시간대", ["Asia/Seoul", "UTC", "America/New_York", "Europe/London"])
    
    with col2:
        language = st.selectbox("언어", ["한국어", "English", "日本語"])
        date_format = st.selectbox("날짜 형식", ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])
        time_format = st.selectbox("시간 형식", ["24시간", "12시간"])
    
    # 모니터링 설정
    st.subheader("📊 모니터링 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        refresh_interval = st.slider("데이터 새로고침 간격 (초)", 5, 60, 10)
        auto_refresh = st.checkbox("자동 새로고침 활성화", value=True)
        max_data_points = st.number_input("최대 데이터 포인트 수", min_value=100, max_value=10000, value=1000)
    
    with col2:
        data_retention_days = st.number_input("데이터 보관 기간 (일)", min_value=1, max_value=365, value=30)
        enable_logging = st.checkbox("로깅 활성화", value=True)
        log_level = st.selectbox("로그 레벨", ["DEBUG", "INFO", "WARNING", "ERROR"])
    
    # 저장 버튼
    if st.button("💾 일반 설정 저장"):
        save_general_settings({
            'system_name': system_name,
            'system_version': system_version,
            'timezone': timezone,
            'language': language,
            'date_format': date_format,
            'time_format': time_format,
            'refresh_interval': refresh_interval,
            'auto_refresh': auto_refresh,
            'max_data_points': max_data_points,
            'data_retention_days': data_retention_days,
            'enable_logging': enable_logging,
            'log_level': log_level
        })
        st.success("✅ 일반 설정이 저장되었습니다!")

def display_alert_settings():
    """알림 설정"""
    st.subheader("🚨 알림 설정")
    
    # 알림 활성화
    st.write("**알림 활성화**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_email_alerts = st.checkbox("이메일 알림", value=True)
        enable_sms_alerts = st.checkbox("SMS 알림", value=False)
        enable_push_alerts = st.checkbox("푸시 알림", value=True)
    
    with col2:
        enable_sound_alerts = st.checkbox("소리 알림", value=True)
        enable_desktop_alerts = st.checkbox("데스크톱 알림", value=True)
        enable_webhook_alerts = st.checkbox("웹훅 알림", value=False)
    
    # 알림 임계값 설정
    st.subheader("📊 알림 임계값")
    
    col1, col2 = st.columns(2)
    
    with col1:
        battery_warning_threshold = st.slider("배터리 경고 임계값 (%)", 10, 50, 20)
        battery_critical_threshold = st.slider("배터리 위험 임계값 (%)", 5, 30, 10)
        temperature_warning_threshold = st.slider("온도 경고 임계값 (°C)", 30, 50, 40)
    
    with col2:
        temperature_critical_threshold = st.slider("온도 위험 임계값 (°C)", 40, 60, 50)
        connection_timeout_threshold = st.slider("연결 타임아웃 (초)", 10, 300, 60)
        health_score_warning_threshold = st.slider("건강도 경고 임계값 (%)", 30, 80, 50)
    
    # 알림 수신자 설정
    st.subheader("👥 알림 수신자")
    
    email_recipients = st.text_area(
        "이메일 수신자 (한 줄에 하나씩)",
        value="admin@example.com\noperator@example.com",
        help="각 이메일 주소를 새 줄로 구분하여 입력하세요."
    )
    
    phone_numbers = st.text_area(
        "SMS 수신자 (한 줄에 하나씩)",
        value="+82-10-1234-5678",
        help="각 전화번호를 새 줄로 구분하여 입력하세요."
    )
    
    # 알림 스케줄
    st.subheader("⏰ 알림 스케줄")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_start_time = st.time_input("알림 시작 시간", value=datetime.strptime("09:00", "%H:%M").time())
        alert_end_time = st.time_input("알림 종료 시간", value=datetime.strptime("18:00", "%H:%M").time())
    
    with col2:
        enable_weekend_alerts = st.checkbox("주말 알림 활성화", value=False)
        enable_holiday_alerts = st.checkbox("공휴일 알림 활성화", value=True)
    
    # 저장 버튼
    if st.button("💾 알림 설정 저장"):
        save_alert_settings({
            'enable_email_alerts': enable_email_alerts,
            'enable_sms_alerts': enable_sms_alerts,
            'enable_push_alerts': enable_push_alerts,
            'enable_sound_alerts': enable_sound_alerts,
            'enable_desktop_alerts': enable_desktop_alerts,
            'enable_webhook_alerts': enable_webhook_alerts,
            'battery_warning_threshold': battery_warning_threshold,
            'battery_critical_threshold': battery_critical_threshold,
            'temperature_warning_threshold': temperature_warning_threshold,
            'temperature_critical_threshold': temperature_critical_threshold,
            'connection_timeout_threshold': connection_timeout_threshold,
            'health_score_warning_threshold': health_score_warning_threshold,
            'email_recipients': email_recipients.split('\n'),
            'phone_numbers': phone_numbers.split('\n'),
            'alert_start_time': str(alert_start_time),
            'alert_end_time': str(alert_end_time),
            'enable_weekend_alerts': enable_weekend_alerts,
            'enable_holiday_alerts': enable_holiday_alerts
        })
        st.success("✅ 알림 설정이 저장되었습니다!")

def display_stream_settings():
    """스트림 설정"""
    st.subheader("📹 스트림 설정")
    
    # 기본 스트림 설정
    st.write("**기본 스트림 설정**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_stream_quality = st.selectbox("기본 스트림 품질", ["low", "medium", "high"], index=1)
        default_fps = st.slider("기본 FPS", 10, 60, 30)
        default_resolution = st.selectbox("기본 해상도", ["640x480", "1280x720", "1920x1080", "3840x2160"])
    
    with col2:
        enable_auto_quality = st.checkbox("자동 품질 조정", value=True)
        enable_motion_detection = st.checkbox("모션 감지 활성화", value=True)
        enable_recording = st.checkbox("자동 녹화 활성화", value=False)
    
    # 스트림 서버 설정
    st.subheader("🌐 스트림 서버 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rtsp_port = st.number_input("RTSP 포트", min_value=1024, max_value=65535, value=8554)
        http_port = st.number_input("HTTP 포트", min_value=1024, max_value=65535, value=8080)
        https_port = st.number_input("HTTPS 포트", min_value=1024, max_value=65535, value=8443)
    
    with col2:
        enable_ssl = st.checkbox("SSL/TLS 활성화", value=True)
        ssl_cert_path = st.text_input("SSL 인증서 경로", value="/path/to/certificate.pem")
        ssl_key_path = st.text_input("SSL 키 경로", value="/path/to/private.key")
    
    # 스트림 품질 프로필
    st.subheader("🎨 품질 프로필")
    
    quality_profiles = {
        'low': {'resolution': '640x480', 'fps': 15, 'bitrate': '500k'},
        'medium': {'resolution': '1280x720', 'fps': 30, 'bitrate': '2M'},
        'high': {'resolution': '1920x1080', 'fps': 30, 'bitrate': '5M'}
    }
    
    for profile, settings in quality_profiles.items():
        with st.expander(f"📹 {profile.upper()} 품질 프로필"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_resolution = st.selectbox(
                    f"해상도 ({profile})",
                    ["640x480", "1280x720", "1920x1080", "3840x2160"],
                    index=["640x480", "1280x720", "1920x1080", "3840x2160"].index(settings['resolution']),
                    key=f"res_{profile}"
                )
            
            with col2:
                new_fps = st.slider(
                    f"FPS ({profile})",
                    10, 60, settings['fps'],
                    key=f"fps_{profile}"
                )
            
            with col3:
                new_bitrate = st.selectbox(
                    f"비트레이트 ({profile})",
                    ["500k", "1M", "2M", "5M", "10M"],
                    index=["500k", "1M", "2M", "5M", "10M"].index(settings['bitrate']),
                    key=f"bitrate_{profile}"
                )
            
            quality_profiles[profile] = {
                'resolution': new_resolution,
                'fps': new_fps,
                'bitrate': new_bitrate
            }
    
    # 저장 버튼
    if st.button("💾 스트림 설정 저장"):
        save_stream_settings({
            'default_stream_quality': default_stream_quality,
            'default_fps': default_fps,
            'default_resolution': default_resolution,
            'enable_auto_quality': enable_auto_quality,
            'enable_motion_detection': enable_motion_detection,
            'enable_recording': enable_recording,
            'rtsp_port': rtsp_port,
            'http_port': http_port,
            'https_port': https_port,
            'enable_ssl': enable_ssl,
            'ssl_cert_path': ssl_cert_path,
            'ssl_key_path': ssl_key_path,
            'quality_profiles': quality_profiles
        })
        st.success("✅ 스트림 설정이 저장되었습니다!")

def display_security_settings():
    """보안 설정"""
    st.subheader("🔐 보안 설정")
    
    # 인증 설정
    st.write("**🔑 인증 설정**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_authentication = st.checkbox("인증 활성화", value=True)
        session_timeout = st.slider("세션 타임아웃 (분)", 15, 480, 60)
        max_login_attempts = st.number_input("최대 로그인 시도 횟수", min_value=3, max_value=10, value=5)
    
    with col2:
        enable_2fa = st.checkbox("2단계 인증", value=False)
        password_min_length = st.number_input("최소 비밀번호 길이", min_value=6, max_value=20, value=8)
        require_special_chars = st.checkbox("특수문자 포함 필수", value=True)
    
    # 접근 제어
    st.subheader("🚪 접근 제어")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_ip_whitelist = st.checkbox("IP 화이트리스트 활성화", value=False)
        allowed_ips = st.text_area(
            "허용된 IP 주소 (한 줄에 하나씩)",
            value="192.168.1.0/24\n10.0.0.0/8",
            help="각 IP 주소 또는 CIDR을 새 줄로 구분하여 입력하세요."
        )
    
    with col2:
        enable_time_restriction = st.checkbox("시간 제한 활성화", value=False)
        access_start_time = st.time_input("접근 시작 시간", value=datetime.strptime("00:00", "%H:%M").time())
        access_end_time = st.time_input("접근 종료 시간", value=datetime.strptime("23:59", "%H:%M").time())
    
    # 암호화 설정
    st.subheader("🔒 암호화 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_data_encryption = st.checkbox("데이터 암호화", value=True)
        encryption_algorithm = st.selectbox("암호화 알고리즘", ["AES-256", "AES-128", "ChaCha20"])
        enable_ssl_tls = st.checkbox("SSL/TLS 활성화", value=True)
    
    with col2:
        ssl_version = st.selectbox("SSL/TLS 버전", ["TLS 1.3", "TLS 1.2", "TLS 1.1"])
        enable_certificate_validation = st.checkbox("인증서 검증", value=True)
        enable_secure_headers = st.checkbox("보안 헤더 활성화", value=True)
    
    # 감사 로그
    st.subheader("📝 감사 로그")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_audit_logging = st.checkbox("감사 로그 활성화", value=True)
        audit_log_retention = st.number_input("감사 로그 보관 기간 (일)", min_value=30, max_value=365, value=90)
    
    with col2:
        log_sensitive_operations = st.checkbox("민감한 작업 로깅", value=True)
        enable_log_encryption = st.checkbox("로그 암호화", value=False)
    
    # 백업 설정
    st.subheader("💾 백업 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_auto_backup = st.checkbox("자동 백업 활성화", value=True)
        backup_frequency = st.selectbox("백업 빈도", ["매일", "매주", "매월"])
        backup_time = st.time_input("백업 시간", value=datetime.strptime("02:00", "%H:%M").time())
    
    with col2:
        backup_retention = st.number_input("백업 보관 기간 (일)", min_value=7, max_value=365, value=30)
        enable_encrypted_backup = st.checkbox("암호화된 백업", value=True)
        backup_location = st.text_input("백업 위치", value="/backup/robot_monitoring")
    
    # 저장 버튼
    if st.button("💾 보안 설정 저장"):
        save_security_settings({
            'enable_authentication': enable_authentication,
            'session_timeout': session_timeout,
            'max_login_attempts': max_login_attempts,
            'enable_2fa': enable_2fa,
            'password_min_length': password_min_length,
            'require_special_chars': require_special_chars,
            'enable_ip_whitelist': enable_ip_whitelist,
            'allowed_ips': allowed_ips.split('\n'),
            'enable_time_restriction': enable_time_restriction,
            'access_start_time': str(access_start_time),
            'access_end_time': str(access_end_time),
            'enable_data_encryption': enable_data_encryption,
            'encryption_algorithm': encryption_algorithm,
            'enable_ssl_tls': enable_ssl_tls,
            'ssl_version': ssl_version,
            'enable_certificate_validation': enable_certificate_validation,
            'enable_secure_headers': enable_secure_headers,
            'enable_audit_logging': enable_audit_logging,
            'audit_log_retention': audit_log_retention,
            'log_sensitive_operations': log_sensitive_operations,
            'enable_log_encryption': enable_log_encryption,
            'enable_auto_backup': enable_auto_backup,
            'backup_frequency': backup_frequency,
            'backup_time': str(backup_time),
            'backup_retention': backup_retention,
            'enable_encrypted_backup': enable_encrypted_backup,
            'backup_location': backup_location
        })
        st.success("✅ 보안 설정이 저장되었습니다!")

def save_general_settings(settings):
    """일반 설정 저장"""
    try:
        with open('settings/general.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"설정 저장 실패: {e}")

def save_alert_settings(settings):
    """알림 설정 저장"""
    try:
        with open('settings/alerts.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"설정 저장 실패: {e}")

def save_stream_settings(settings):
    """스트림 설정 저장"""
    try:
        with open('settings/streams.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"설정 저장 실패: {e}")

def save_security_settings(settings):
    """보안 설정 저장"""
    try:
        with open('settings/security.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"설정 저장 실패: {e}")

def load_settings(setting_type):
    """설정 로드"""
    try:
        settings_file = f'settings/{setting_type}.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"설정 로드 실패: {e}")
        return {}

if __name__ == "__main__":
    main() 