from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from database.dynamodb_client import db_client
from models.robot import Robot, SensorData, Alert, MaintenanceRecord, CameraStream
from config import ROBOT_STATUS, ALERT_LEVELS, SENSOR_TYPES

logger = logging.getLogger(__name__)

class RobotService:
    """로봇 서비스 클래스"""
    
    def __init__(self):
        self.db = db_client
    
    def create_robot(self, name: str, model: str, **kwargs) -> Robot:
        """새로운 로봇 생성"""
        try:
            robot_id = f"robot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
            robot = Robot(robot_id=robot_id, name=name, model=model, **kwargs)
            
            # DynamoDB에 저장
            robot_data = robot.to_dict()
            self.db.put_item('robots', robot_data)
            
            logger.info(f"로봇 생성 완료: {robot_id}")
            return robot
        except Exception as e:
            logger.error(f"로봇 생성 실패: {e}")
            raise
    
    def get_robot(self, robot_id: str) -> Optional[Robot]:
        """로봇 조회"""
        try:
            robot_data = self.db.get_item('robots', {'robot_id': robot_id})
            if robot_data:
                return Robot.from_dict(robot_data)
            return None
        except Exception as e:
            logger.error(f"로봇 조회 실패: {e}")
            raise
    
    def get_all_robots(self) -> List[Robot]:
        """모든 로봇 조회"""
        try:
            robots_data = self.db.scan('robots')
            robots = []
            for robot_data in robots_data:
                try:
                    # datetime 문자열을 datetime 객체로 변환
                    if 'created_at' in robot_data and isinstance(robot_data['created_at'], str):
                        robot_data['created_at'] = datetime.fromisoformat(robot_data['created_at'].replace('Z', '+00:00'))
                    if 'updated_at' in robot_data and isinstance(robot_data['updated_at'], str):
                        robot_data['updated_at'] = datetime.fromisoformat(robot_data['updated_at'].replace('Z', '+00:00'))
                    if 'last_maintenance' in robot_data and robot_data['last_maintenance'] and isinstance(robot_data['last_maintenance'], str):
                        robot_data['last_maintenance'] = datetime.fromisoformat(robot_data['last_maintenance'].replace('Z', '+00:00'))
                    if 'next_maintenance' in robot_data and robot_data['next_maintenance'] and isinstance(robot_data['next_maintenance'], str):
                        robot_data['next_maintenance'] = datetime.fromisoformat(robot_data['next_maintenance'].replace('Z', '+00:00'))
                    
                    # location 데이터 처리
                    if 'location' in robot_data and robot_data['location']:
                        location_data = robot_data['location']
                        if 'timestamp' in location_data and isinstance(location_data['timestamp'], str):
                            location_data['timestamp'] = datetime.fromisoformat(location_data['timestamp'].replace('Z', '+00:00'))
                    
                    robot = Robot.from_dict(robot_data)
                    robots.append(robot)
                except Exception as robot_error:
                    logger.warning(f"로봇 데이터 파싱 실패: {robot_error}, 데이터: {robot_data}")
                    continue
            return robots
        except Exception as e:
            logger.error(f"모든 로봇 조회 실패: {e}")
            raise
    
    def get_online_robots(self) -> List[Robot]:
        """온라인 로봇만 조회"""
        try:
            robots_data = self.db.scan(
                'robots',
                filter_expression='#status = :status',
                expression_attribute_names={'#status': 'status'},
                expression_attribute_values={':status': ROBOT_STATUS['ONLINE']}
            )
            return [Robot.from_dict(robot_data) for robot_data in robots_data]
        except Exception as e:
            logger.error(f"온라인 로봇 조회 실패: {e}")
            raise
    
    def update_robot_status(self, robot_id: str, status: str) -> bool:
        """로봇 상태 업데이트"""
        try:
            update_expression = 'SET #status = :status, updated_at = :updated_at'
            expression_attribute_names = {'#status': 'status'}
            expression_attribute_values = {
                ':status': status,
                ':updated_at': datetime.now().isoformat()
            }
            
            self.db.update_item(
                'robots',
                {'robot_id': robot_id},
                update_expression,
                expression_attribute_values
            )
            
            logger.info(f"로봇 상태 업데이트: {robot_id} -> {status}")
            return True
        except Exception as e:
            logger.error(f"로봇 상태 업데이트 실패: {e}")
            return False
    
    def update_robot_location(self, robot_id: str, latitude: float, longitude: float, altitude: Optional[float] = None) -> bool:
        """로봇 위치 업데이트"""
        try:
            location_data = {
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': datetime.now().isoformat()
            }
            if altitude is not None:
                location_data['altitude'] = altitude
            
            update_expression = 'SET #location = :location, updated_at = :updated_at'
            expression_attribute_names = {'#location': 'location'}
            expression_attribute_values = {
                ':location': location_data,
                ':updated_at': datetime.now().isoformat()
            }
            
            self.db.update_item(
                'robots',
                {'robot_id': robot_id},
                update_expression,
                expression_attribute_values
            )
            
            logger.info(f"로봇 위치 업데이트: {robot_id}")
            return True
        except Exception as e:
            logger.error(f"로봇 위치 업데이트 실패: {e}")
            return False
    
    def save_sensor_data(self, robot_id: str, sensor_type: str, value: float, unit: str) -> SensorData:
        """센서 데이터 저장"""
        try:
            sensor_data = SensorData(
                sensor_type=sensor_type,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                robot_id=robot_id
            )
            
            sensor_dict = {
                'sensor_id': sensor_data.sensor_id,
                'robot_id': robot_id,
                'sensor_type': sensor_type,
                'value': value,
                'unit': unit,
                'timestamp': sensor_data.timestamp.isoformat()
            }
            
            self.db.put_item('sensor_data', sensor_dict)
            
            # 로봇의 배터리 레벨 업데이트 (배터리 센서인 경우)
            if sensor_type == SENSOR_TYPES['BATTERY']:
                self.update_robot_battery(robot_id, value)
            
            logger.info(f"센서 데이터 저장: {robot_id} - {sensor_type}")
            return sensor_data
        except Exception as e:
            logger.error(f"센서 데이터 저장 실패: {e}")
            raise
    
    def update_robot_battery(self, robot_id: str, battery_level: float) -> bool:
        """로봇 배터리 레벨 업데이트"""
        try:
            update_expression = 'SET battery_level = :battery_level, updated_at = :updated_at'
            expression_attribute_values = {
                ':battery_level': battery_level,
                ':updated_at': datetime.now().isoformat()
            }
            
            self.db.update_item(
                'robots',
                {'robot_id': robot_id},
                update_expression,
                expression_attribute_values
            )
            
            # 배터리 레벨이 낮으면 알림 생성
            if battery_level < 20:
                self.create_alert(robot_id, ALERT_LEVELS['WARNING'], f"배터리 레벨이 낮습니다: {battery_level}%")
            elif battery_level < 10:
                self.create_alert(robot_id, ALERT_LEVELS['CRITICAL'], f"배터리 레벨이 매우 낮습니다: {battery_level}%")
            
            return True
        except Exception as e:
            logger.error(f"배터리 레벨 업데이트 실패: {e}")
            return False
    
    def create_alert(self, robot_id: str, level: str, message: str) -> Alert:
        """알림 생성"""
        try:
            alert = Alert(
                alert_id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{robot_id}",
                robot_id=robot_id,
                level=level,
                message=message,
                timestamp=datetime.now()
            )
            
            alert_dict = {
                'alert_id': alert.alert_id,
                'robot_id': robot_id,
                'level': level,
                'message': message,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': False
            }
            
            self.db.put_item('alerts', alert_dict)
            
            logger.info(f"알림 생성: {robot_id} - {level} - {message}")
            return alert
        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")
            raise
    
    def get_robot_alerts(self, robot_id: str, resolved: Optional[bool] = None) -> List[Alert]:
        """로봇 알림 조회"""
        try:
            alerts_data = self.db.scan('alerts')
            alerts = []
            
            for alert_data in alerts_data:
                try:
                    # robot_id 필터링
                    if alert_data.get('robot_id') != robot_id:
                        continue
                    
                    # resolved 필터링
                    if resolved is not None and alert_data.get('resolved') != resolved:
                        continue
                    
                    # datetime 문자열을 datetime 객체로 변환
                    if 'timestamp' in alert_data and isinstance(alert_data['timestamp'], str):
                        alert_data['timestamp'] = datetime.fromisoformat(alert_data['timestamp'].replace('Z', '+00:00'))
                    if 'resolved_at' in alert_data and alert_data['resolved_at'] and isinstance(alert_data['resolved_at'], str):
                        alert_data['resolved_at'] = datetime.fromisoformat(alert_data['resolved_at'].replace('Z', '+00:00'))
                    
                    alert = Alert(**alert_data)
                    alerts.append(alert)
                except Exception as alert_error:
                    logger.warning(f"알림 데이터 파싱 실패: {alert_error}")
                    continue
            
            return alerts
        except Exception as e:
            logger.error(f"로봇 알림 조회 실패: {e}")
            raise
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """알림 해결"""
        try:
            update_expression = 'SET resolved = :resolved, resolved_at = :resolved_at, resolved_by = :resolved_by'
            expression_attribute_values = {
                ':resolved': True,
                ':resolved_at': datetime.now().isoformat(),
                ':resolved_by': resolved_by
            }
            
            self.db.update_item(
                'alerts',
                {'alert_id': alert_id},
                update_expression,
                expression_attribute_values
            )
            
            logger.info(f"알림 해결: {alert_id}")
            return True
        except Exception as e:
            logger.error(f"알림 해결 실패: {e}")
            return False
    
    def add_camera_stream(self, robot_id: str, stream_url: str, stream_type: str = 'http', quality: str = 'medium') -> CameraStream:
        """카메라 스트림 추가"""
        try:
            stream = CameraStream(
                stream_id=f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{robot_id}",
                robot_id=robot_id,
                stream_url=stream_url,
                stream_type=stream_type,
                quality=quality,
                created_at=datetime.now()
            )
            
            stream_dict = {
                'stream_id': stream.stream_id,
                'robot_id': robot_id,
                'stream_url': stream_url,
                'stream_type': stream_type,
                'quality': quality,
                'is_active': True,
                'created_at': stream.created_at.isoformat()
            }
            
            self.db.put_item('camera_streams', stream_dict)
            
            logger.info(f"카메라 스트림 추가: {robot_id} - {stream_url}")
            return stream
        except Exception as e:
            logger.error(f"카메라 스트림 추가 실패: {e}")
            raise
    
    def get_robot_camera_streams(self, robot_id: str) -> List[CameraStream]:
        """로봇 카메라 스트림 조회"""
        try:
            streams_data = self.db.query(
                'camera_streams',
                '#robot_id = :robot_id',
                expression_attribute_names={'#robot_id': 'robot_id'},
                expression_attribute_values={':robot_id': robot_id}
            )
            
            return [CameraStream(**stream_data) for stream_data in streams_data]
        except Exception as e:
            logger.error(f"카메라 스트림 조회 실패: {e}")
            raise
    
    def get_robot_health_summary(self, robot_id: str) -> Dict[str, Any]:
        """로봇 건강도 요약"""
        try:
            robot = self.get_robot(robot_id)
            if not robot:
                return {}
            
            # 최근 센서 데이터 조회
            recent_sensor_data = self.db.query(
                'sensor_data',
                '#robot_id = :robot_id',
                expression_attribute_names={'#robot_id': 'robot_id'},
                expression_attribute_values={':robot_id': robot_id},
                scan_index_forward=False,  # 최신 데이터부터
                limit=10
            )
            
            # 최근 알림 조회
            recent_alerts = self.get_robot_alerts(robot_id, resolved=False)
            
            health_score = robot.get_health_score()
            
            return {
                'robot_id': robot_id,
                'name': robot.name,
                'status': robot.status,
                'battery_level': robot.battery_level,
                'health_score': health_score,
                'location': robot.location.__dict__ if robot.location else None,
                'recent_sensor_data': recent_sensor_data,
                'active_alerts_count': len(recent_alerts),
                'needs_maintenance': robot.needs_maintenance(),
                'last_updated': robot.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"로봇 건강도 요약 조회 실패: {e}")
            raise

# 전역 서비스 인스턴스
robot_service = RobotService()
