import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# AWS 설정
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-2')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# DynamoDB 테이블명
DYNAMODB_TABLES = {
    'users': 'robot_monitoring_users',
    'robots': 'robot_monitoring_robots',
    'sensor_data': 'robot_monitoring_sensor_data',
    'alerts': 'robot_monitoring_alerts',
    'locations': 'robot_monitoring_locations',
    'maintenance': 'robot_monitoring_maintenance',
    'camera_streams': 'robot_monitoring_camera_streams'
}

# 카메라 스트림 설정
CAMERA_STREAM_CONFIG = {
    'rtsp_port': 8554,
    'http_port': 8080,
    'stream_quality': 'medium',  # low, medium, high
    'max_fps': 30
}

# 로봇 상태 정의
ROBOT_STATUS = {
    'ONLINE': 'online',
    'OFFLINE': 'offline',
    'MAINTENANCE': 'maintenance',
    'ERROR': 'error',
    'CHARGING': 'charging',
    'MOVING': 'moving',
    'IDLE': 'idle'
}

# 알림 레벨
ALERT_LEVELS = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'error',
    'CRITICAL': 'critical'
}

# 센서 타입
SENSOR_TYPES = {
    'TEMPERATURE': 'temperature',
    'HUMIDITY': 'humidity',
    'BATTERY': 'battery',
    'GPS': 'gps',
    'ACCELEROMETER': 'accelerometer',
    'GYROSCOPE': 'gyroscope',
    'CAMERA': 'camera',
    'LIDAR': 'lidar'
}
