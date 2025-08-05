import random
from datetime import datetime, timedelta
from database import db

def create_sample_data():
    """ERD에 맞는 샘플 데이터 생성"""
    
    # 1. 사용자 생성
    users = [
        {'first_name': '김', 'last_name': '관리자', 'user_email': 'admin@robot.com', 'user_password': 'admin123', 'user_role': 'Admin'},
        {'first_name': '이', 'last_name': '엔지니어', 'user_email': 'engineer@robot.com', 'user_password': 'engineer123', 'user_role': 'User'},
        {'first_name': '박', 'last_name': '운영자', 'user_email': 'operator@robot.com', 'user_password': 'operator123', 'user_role': 'User'},
    ]
    
    user_ids = []
    for user in users:
        user_id = db.create_user(user)
        user_ids.append(user_id)
    
    # 2. 팀 생성
    teams = [
        {'user_id': user_ids[0], 'team_name': '로봇개발팀', 'team_description': '탐사로봇 개발 및 운영'},
        {'user_id': user_ids[1], 'team_name': '데이터분석팀', 'team_description': '센서 데이터 분석 및 AI 모델 개발'},
    ]
    
    team_ids = []
    for team in teams:
        team_id = db.create_team(team)
        team_ids.append(team_id)
    
    # 3. 프로젝트 생성
    projects = [
        {
            'user_id': user_ids[0], 
            'team_id': team_ids[0], 
            'project_name': '탐사로봇 모니터링 시스템',
            'project_description': '산업용 탐사로봇의 실시간 모니터링 및 제어 시스템',
            'project_status': 'Active',
            'project_start_date': datetime.now() - timedelta(days=30),
            'project_end_date': datetime.now() + timedelta(days=90)
        },
        {
            'user_id': user_ids[1], 
            'team_id': team_ids[1], 
            'project_name': 'AI 객체 감지 시스템',
            'project_description': '카메라 기반 실시간 객체 감지 및 분석 시스템',
            'project_status': 'Active',
            'project_start_date': datetime.now() - timedelta(days=15),
            'project_end_date': datetime.now() + timedelta(days=60)
        }
    ]
    
    project_ids = []
    for project in projects:
        project_id = db.create_project(project)
        project_ids.append(project_id)
    
    # 4. 로봇 생성
    robots = [
        {
            'project_id': project_ids[0],
            'robot_name': 'Explorer-001',
            'robot_battery': random.randint(60, 100),
            'robot_connection': random.randint(0, 1),
            'robot_ping': random.randint(10, 100),
            'robot_status': random.choice(['Online', 'Offline', 'Maintenance']),
            'robot_location_x': random.uniform(0, 100),
            'robot_location_y': random.uniform(0, 100)
        },
        {
            'project_id': project_ids[0],
            'robot_name': 'Explorer-002',
            'robot_battery': random.randint(60, 100),
            'robot_connection': random.randint(0, 1),
            'robot_ping': random.randint(10, 100),
            'robot_status': random.choice(['Online', 'Offline', 'Maintenance']),
            'robot_location_x': random.uniform(0, 100),
            'robot_location_y': random.uniform(0, 100)
        },
        {
            'project_id': project_ids[1],
            'robot_name': 'Scanner-001',
            'robot_battery': random.randint(60, 100),
            'robot_connection': random.randint(0, 1),
            'robot_ping': random.randint(10, 100),
            'robot_status': random.choice(['Online', 'Offline', 'Maintenance']),
            'robot_location_x': random.uniform(0, 100),
            'robot_location_y': random.uniform(0, 100)
        }
    ]
    
    robot_ids = []
    for robot in robots:
        robot_id = db.create_robot(robot)
        robot_ids.append(robot_id)
    
    # 5. 카메라 생성
    cameras = [
        {
            'robot_id': robot_ids[0],
            'camera_name': 'Front Camera',
            'camera_stream_url': 'rtsp://192.168.1.100:554/stream1',
            'camera_isactivate': True,
            'camera_position': 'head'
        },
        {
            'robot_id': robot_ids[0],
            'camera_name': 'Side Camera',
            'camera_stream_url': 'rtsp://192.168.1.100:554/stream2',
            'camera_isactivate': True,
            'camera_position': 'leg'
        },
        {
            'robot_id': robot_ids[1],
            'camera_name': 'Main Camera',
            'camera_stream_url': 'rtsp://192.168.1.101:554/stream1',
            'camera_isactivate': True,
            'camera_position': 'head'
        },
        {
            'robot_id': robot_ids[2],
            'camera_name': 'Scan Camera',
            'camera_stream_url': 'rtsp://192.168.1.102:554/stream1',
            'camera_isactivate': True,
            'camera_position': 'head'
        }
    ]
    
    camera_ids = []
    for camera in cameras:
        camera_id = db.create_camera(camera)
        camera_ids.append(camera_id)
    
    # 6. 감지 결과 생성
    detection_classes = ['person', 'vehicle', 'equipment', 'hazard', 'obstacle']
    
    for _ in range(50):  # 50개의 감지 결과 생성
        detection = {
            'camera_id': random.choice(camera_ids),
            'detection_class': random.choice(detection_classes),
            'detection_conf': random.uniform(0.7, 0.99),
            'detection_bbox': {
                'x1': random.uniform(0, 1),
                'y1': random.uniform(0, 1),
                'x2': random.uniform(0, 1),
                'y2': random.uniform(0, 1)
            }
        }
        db.create_detection_result(detection)
    
    # 7. 센서 데이터 생성
    for _ in range(100):  # 100개의 센서 데이터 생성
        sensor_data = {
            'robot_id': random.choice(robot_ids),
            'sensor_imu_gyro': {
                'x': random.uniform(-180, 180),
                'y': random.uniform(-180, 180),
                'z': random.uniform(-180, 180)
            },
            'sensor_imu_acc': {
                'x': random.uniform(-9.8, 9.8),
                'y': random.uniform(-9.8, 9.8),
                'z': random.uniform(-9.8, 9.8)
            },
            'sensor_temp': random.uniform(15, 35),
            'sensor_humid': random.uniform(30, 80),
            'sensor_press': random.uniform(1000, 1100)
        }
        db.create_sensor_data(sensor_data)
    
    # 8. 로봇 상태 히스토리 생성
    status_events = ['startup', 'shutdown', 'error', 'maintenance', 'normal']
    
    for _ in range(30):  # 30개의 상태 히스토리 생성
        status_history = {
            'robot_id': random.choice(robot_ids),
            'status_battery': random.randint(20, 100),
            'status_connect': random.choice(['Connected', 'Disconnected']),
            'status_robot': random.choice(['Idle', 'Moving', 'Working', 'Error']),
            'status_event': random.choice(status_events)
        }
        db.create_robot_status_history(status_history)
    
    # 9. 보고서 생성
    reports = [
        {
            'project_id': project_ids[0],
            'user_id': user_ids[0],
            'report_title': '탐사로봇 일일 보고서',
            'report_content': '오늘 탐사로봇들이 정상적으로 작동했습니다. 총 15개의 객체가 감지되었습니다.',
            'report_detected': {
                'total_detections': 15,
                'detection_classes': {'person': 5, 'vehicle': 3, 'equipment': 7}
            }
        },
        {
            'project_id': project_ids[1],
            'user_id': user_ids[1],
            'report_title': 'AI 감지 시스템 성능 보고서',
            'report_content': 'AI 모델의 정확도가 95%를 달성했습니다. 개선이 필요한 부분을 식별했습니다.',
            'report_detected': {
                'accuracy': 0.95,
                'total_detections': 25,
                'false_positives': 2
            }
        }
    ]
    
    for report in reports:
        db.create_report(report)
    
    # 10. 명령 히스토리 생성
    command_types = ['move', 'stop', 'scan', 'return_home', 'emergency_stop']
    
    for _ in range(20):  # 20개의 명령 히스토리 생성
        command = {
            'robot_id': random.choice(robot_ids),
            'user_id': random.choice(user_ids),
            'command_type': random.choice(command_types),
            'command_detail': {
                'x': random.uniform(0, 100),
                'y': random.uniform(0, 100),
                'speed': random.uniform(0.1, 2.0),
                'duration': random.randint(10, 300)
            }
        }
        db.create_command_history(command)
    
    print("샘플 데이터 생성 완료!")
    print(f"- 사용자: {len(users)}명")
    print(f"- 팀: {len(teams)}개")
    print(f"- 프로젝트: {len(projects)}개")
    print(f"- 로봇: {len(robots)}대")
    print(f"- 카메라: {len(cameras)}개")
    print(f"- 감지 결과: 50개")
    print(f"- 센서 데이터: 100개")
    print(f"- 상태 히스토리: 30개")
    print(f"- 보고서: {len(reports)}개")
    print(f"- 명령 히스토리: 20개")

if __name__ == "__main__":
    create_sample_data() 