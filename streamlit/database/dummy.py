import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from config import ROBOT_STATUS, ALERT_LEVELS, SENSOR_TYPES, DYNAMODB_TABLES

class DummyDataGenerator:
    """더미 데이터 생성기"""
    
    def __init__(self):
        self.robot_names = [
            "정보탐색로봇-001", "정보탐색로봇-002", "정보탐색로봇-003",
            "정보탐색로봇-004", "정보탐색로봇-005", "정보탐색로봇-006",
            "정보탐색로봇-007", "정보탐색로봇-008", "정보탐색로봇-009",
            "정보탐색로봇-010"
        ]
        
        self.robot_models = [
            "ITR-2024-A", "ITR-2024-B", "ITR-2024-C",
            "ITR-2023-A", "ITR-2023-B"
        ]
        
        self.manufacturers = [
            "로봇테크", "스마트솔루션", "AI로봇시스템", "정보탐색로봇"
        ]
        
        self.technicians = [
            "김기술", "이정비", "박엔지니어", "최전문가", "정수리"
        ]
        
        self.locations = [
            "서울대학교", "연세대학교", "고려대학교", "한양대학교",
            "성균관대학교", "중앙대학교", "경희대학교", "동국대학교",
            "서강대학교", "홍익대학교", "건국대학교", "국민대학교"
        ]
        
        # 서울 지역 좌표 범위
        self.seoul_coords = {
            'lat_range': (37.4133, 37.7151),
            'lng_range': (126.7341, 127.2693)
        }

    def generate_robot_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """로봇 데이터 생성"""
        robots = []
        
        for i in range(count):
            robot_id = f"robot_{str(uuid.uuid4())[:8]}"
            status = random.choice(list(ROBOT_STATUS.values()))
            battery_level = random.uniform(20.0, 100.0)
            
            # 위치 데이터 생성
            lat = random.uniform(*self.seoul_coords['lat_range'])
            lng = random.uniform(*self.seoul_coords['lng_range'])
            
            robot = {
                'robot_id': robot_id,
                'name': self.robot_names[i % len(self.robot_names)],
                'model': random.choice(self.robot_models),
                'status': status,
                'battery_level': round(battery_level, 2),
                'description': f"{self.robot_names[i % len(self.robot_names)]} - 자동화된 정보 탐색 및 수집 시스템",
                'manufacturer': random.choice(self.manufacturers),
                'serial_number': f"SN{random.randint(100000, 999999)}",
                'firmware_version': f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                'location': {
                    'latitude': round(lat, 6),
                    'longitude': round(lng, 6),
                    'altitude': random.uniform(0, 100),
                    'accuracy': random.uniform(1, 10),
                    'timestamp': datetime.now().isoformat()
                },
                'last_maintenance': (datetime.now() - timedelta(days=random.randint(30, 180))).isoformat(),
                'next_maintenance': (datetime.now() + timedelta(days=random.randint(30, 90))).isoformat(),
                'total_operating_hours': round(random.uniform(100, 2000), 2),
                'sensors': random.sample(list(SENSOR_TYPES.values()), random.randint(3, 6)),
                'documents_processed': random.randint(1000, 50000),
                'search_accuracy': round(random.uniform(85.0, 99.5), 2),
                'ai_model_version': f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'location_name': random.choice(self.locations),
                'building': f"건물{random.randint(1, 5)}",
                'room_number': random.randint(101, 999)
            }
            
            robots.append(robot)
        
        return robots

    def generate_sensor_data(self, robot_ids: List[str], hours: int = 24) -> List[Dict[str, Any]]:
        """센서 데이터 생성"""
        sensor_data = []
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        for robot_id in robot_ids:
            current_time = start_time
            while current_time <= end_time:
                # 온도 데이터
                temp_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': SENSOR_TYPES['TEMPERATURE'],
                    'value': round(random.uniform(18.0, 25.0), 2),
                    'unit': '°C',
                    'timestamp': current_time.isoformat()
                }
                sensor_data.append(temp_data)
                
                # 습도 데이터
                humidity_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': SENSOR_TYPES['HUMIDITY'],
                    'value': round(random.uniform(40.0, 70.0), 2),
                    'unit': '%',
                    'timestamp': current_time.isoformat()
                }
                sensor_data.append(humidity_data)
                
                # 배터리 데이터
                battery_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': SENSOR_TYPES['BATTERY'],
                    'value': round(random.uniform(20.0, 100.0), 2),
                    'unit': '%',
                    'timestamp': current_time.isoformat()
                }
                sensor_data.append(battery_data)
                
                # GPS 데이터 (위치 업데이트)
                lat = random.uniform(*self.seoul_coords['lat_range'])
                lng = random.uniform(*self.seoul_coords['lng_range'])
                gps_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': SENSOR_TYPES['GPS'],
                    'value': round(lat, 6),
                    'unit': 'latitude',
                    'timestamp': current_time.isoformat(),
                    'longitude': round(lng, 6)
                }
                sensor_data.append(gps_data)
                
                # 스캐너 상태 데이터
                scanner_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': 'scanner_status',
                    'value': random.choice([0, 1]),  # 0: 비활성, 1: 활성
                    'unit': 'status',
                    'timestamp': current_time.isoformat()
                }
                sensor_data.append(scanner_data)
                
                # AI 처리 속도 데이터
                ai_speed_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': 'ai_processing_speed',
                    'value': round(random.uniform(10.0, 100.0), 2),
                    'unit': 'documents/min',
                    'timestamp': current_time.isoformat()
                }
                sensor_data.append(ai_speed_data)
                
                # 메모리 사용량 데이터
                memory_data = {
                    'sensor_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'sensor_type': 'memory_usage',
                    'value': round(random.uniform(20.0, 90.0), 2),
                    'unit': '%',
                    'timestamp': current_time.isoformat()
                }
                sensor_data.append(memory_data)
                
                current_time += timedelta(minutes=5)  # 5분마다 데이터 생성
        
        return sensor_data

    def generate_alerts(self, robot_ids: List[str], days: int = 30) -> List[Dict[str, Any]]:
        """알림 데이터 생성"""
        alerts = []
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        alert_messages = {
            'info': [
                "정상 작동 중입니다.",
                "배터리 충전 완료",
                "정기 점검 완료",
                "새로운 펌웨어 업데이트 가능",
                "정보 수집 작업 완료",
                "데이터베이스 연결 정상",
                "문서 스캔 완료",
                "정보 인덱싱 완료",
                "검색 엔진 정상 작동",
                "AI 모델 학습 완료"
            ],
            'warning': [
                "배터리 레벨이 낮습니다 (20% 미만)",
                "정기 점검이 필요합니다",
                "센서 데이터 이상 감지",
                "네트워크 연결 불안정",
                "정보 수집 속도 저하",
                "메모리 사용량 증가",
                "스캐너 성능 저하",
                "검색 정확도 감소",
                "AI 모델 성능 저하",
                "저장 공간 부족"
            ],
            'error': [
                "배터리 부족으로 인한 자동 종료",
                "센서 오작동 감지",
                "모터 과열 경고",
                "통신 오류 발생",
                "정보 수집 실패",
                "데이터베이스 연결 오류",
                "스캐너 고장",
                "AI 모델 오류",
                "검색 시스템 오류",
                "문서 처리 실패"
            ],
            'critical': [
                "긴급 정지 필요 - 안전 위험",
                "시스템 오류로 인한 완전 정지",
                "배터리 완전 방전",
                "센서 고장으로 인한 작동 불가",
                "정보 수집 시스템 완전 정지",
                "데이터 손실 위험",
                "AI 시스템 완전 정지",
                "검색 엔진 고장",
                "스캐너 시스템 파손",
                "전체 시스템 복구 필요"
            ]
        }
        
        for robot_id in robot_ids:
            # 각 로봇당 1-5개의 알림 생성
            alert_count = random.randint(1, 5)
            for _ in range(alert_count):
                level = random.choice(list(ALERT_LEVELS.values()))
                message = random.choice(alert_messages[level])
                
                alert_time = start_time + timedelta(
                    seconds=random.randint(0, int((end_time - start_time).total_seconds()))
                )
                
                alert = {
                    'alert_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'level': level,
                    'message': message,
                    'timestamp': alert_time.isoformat(),
                    'resolved': random.choice([True, False]),
                    'resolved_at': alert_time.isoformat() if random.choice([True, False]) else None,
                    'resolved_by': random.choice(self.technicians) if random.choice([True, False]) else None
                }
                alerts.append(alert)
        
        return alerts

    def generate_maintenance_records(self, robot_ids: List[str], months: int = 12) -> List[Dict[str, Any]]:
        """정비 기록 데이터 생성"""
        maintenance_records = []
        end_time = datetime.now()
        start_time = end_time - timedelta(days=months * 30)
        
        maintenance_types = ['scheduled', 'emergency', 'preventive', 'software_update', 'ai_model_update']
        maintenance_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled']
        
        parts_list = [
            "배터리 팩", "모터", "센서 모듈", "카메라", "휠", "브레이크 패드",
            "필터", "펌프", "배선", "컨트롤러", "스캐너", "프린터", "네트워크 모듈",
            "AI 프로세서", "메모리 모듈", "검색 엔진 모듈", "문서 처리 모듈"
        ]
        
        for robot_id in robot_ids:
            # 각 로봇당 2-4개의 정비 기록 생성
            record_count = random.randint(2, 4)
            for _ in range(record_count):
                maintenance_type = random.choice(maintenance_types)
                status = random.choice(maintenance_statuses)
                
                start_date = start_time + timedelta(
                    seconds=random.randint(0, int((end_time - start_time).total_seconds()))
                )
                
                end_date = None
                if status in ['completed', 'in_progress']:
                    end_date = start_date + timedelta(hours=random.randint(1, 8))
                
                maintenance = {
                    'maintenance_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'maintenance_type': maintenance_type,
                    'description': f"{maintenance_type} 정비/업데이트 작업",
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat() if end_date else None,
                    'technician': random.choice(self.technicians),
                    'cost': round(random.uniform(50000, 500000), 2),
                    'parts_replaced': random.sample(parts_list, random.randint(0, 3)),
                    'status': status
                }
                maintenance_records.append(maintenance)
        
        return maintenance_records

    def generate_camera_streams(self, robot_ids: List[str]) -> List[Dict[str, Any]]:
        """카메라 스트림 데이터 생성"""
        camera_streams = []
        
        stream_types = ['rtsp', 'http', 'webrtc']
        qualities = ['low', 'medium', 'high']
        
        for robot_id in robot_ids:
            # 각 로봇당 1-2개의 카메라 스트림 생성
            stream_count = random.randint(1, 2)
            for i in range(stream_count):
                stream = {
                    'stream_id': str(uuid.uuid4()),
                    'robot_id': robot_id,
                    'stream_url': f"rtsp://camera.{robot_id}.local:8554/stream{i+1}",
                    'stream_type': random.choice(stream_types),
                    'quality': random.choice(qualities),
                    'is_active': random.choice([True, False]),
                    'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    'last_accessed': datetime.now().isoformat() if random.choice([True, False]) else None,
                    'stream_purpose': random.choice(['monitoring', 'document_scanning', 'navigation', 'safety'])
                }
                camera_streams.append(stream)
        
        return camera_streams

    def generate_users(self, count: int = 5) -> List[Dict[str, Any]]:
        """사용자 데이터 생성"""
        users = []
        
        user_roles = ['admin', 'operator', 'viewer', 'technician']
        departments = ['IT', '정보관리팀', '정비팀', '관리팀', '데이터분석팀', 'AI개발팀', '연구개발팀']
        
        for i in range(count):
            user = {
                'user_id': str(uuid.uuid4()),
                'username': f"user{i+1}",
                'email': f"user{i+1}@company.com",
                'full_name': f"사용자{i+1}",
                'role': random.choice(user_roles),
                'department': random.choice(departments),
                'is_active': True,
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'last_login': datetime.now().isoformat() if random.choice([True, False]) else None
            }
            users.append(user)
        
        return users

    def generate_all_dummy_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """모든 더미 데이터 생성"""
        print("더미 데이터 생성 중...")
        
        # 로봇 데이터 생성
        robots = self.generate_robot_data(10)
        robot_ids = [robot['robot_id'] for robot in robots]
        
        # 센서 데이터 생성 (최근 24시간)
        sensor_data = self.generate_sensor_data(robot_ids, 24)
        
        # 알림 데이터 생성 (최근 30일)
        alerts = self.generate_alerts(robot_ids, 30)
        
        # 정비 기록 생성 (최근 12개월)
        maintenance_records = self.generate_maintenance_records(robot_ids, 12)
        
        # 카메라 스트림 데이터 생성
        camera_streams = self.generate_camera_streams(robot_ids)
        
        # 사용자 데이터 생성
        users = self.generate_users(5)
        
        dummy_data = {
            'robots': robots,
            'sensor_data': sensor_data,
            'alerts': alerts,
            'maintenance': maintenance_records,
            'camera_streams': camera_streams,
            'users': users
        }
        
        print(f"더미 데이터 생성 완료:")
        print(f"- 로봇: {len(robots)}개")
        print(f"- 센서 데이터: {len(sensor_data)}개")
        print(f"- 알림: {len(alerts)}개")
        print(f"- 정비 기록: {len(maintenance_records)}개")
        print(f"- 카메라 스트림: {len(camera_streams)}개")
        print(f"- 사용자: {len(users)}개")
        
        return dummy_data

    def save_dummy_data_to_json(self, filename: str = "dummy_data.json"):
        """더미 데이터를 JSON 파일로 저장"""
        dummy_data = self.generate_all_dummy_data()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f, ensure_ascii=False, indent=2)
        
        print(f"더미 데이터가 {filename}에 저장되었습니다.")

# 사용 예시
if __name__ == "__main__":
    generator = DummyDataGenerator()
    generator.save_dummy_data_to_json()
