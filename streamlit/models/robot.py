from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid
from config import ROBOT_STATUS, SENSOR_TYPES

@dataclass
class RobotLocation:
    """로봇 위치 정보"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None

@dataclass
class SensorData:
    """센서 데이터"""
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    robot_id: str
    sensor_id: Optional[str] = None

@dataclass
class Alert:
    """알림 정보"""
    alert_id: str
    robot_id: str
    level: str  # info, warning, error, critical
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

@dataclass
class MaintenanceRecord:
    """정비 기록"""
    maintenance_id: str
    robot_id: str
    maintenance_type: str  # scheduled, emergency, preventive
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    technician: Optional[str] = None
    cost: Optional[float] = None
    parts_replaced: Optional[List[str]] = None
    status: str = 'scheduled'  # scheduled, in_progress, completed, cancelled

@dataclass
class CameraStream:
    """카메라 스트림 정보"""
    stream_id: str
    robot_id: str
    stream_url: str
    stream_type: str  # rtsp, http, webrtc
    quality: str  # low, medium, high
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None

class Robot:
    """로봇 클래스"""
    
    def __init__(self, 
                 robot_id: str,
                 name: str,
                 model: str,
                 status: str = ROBOT_STATUS['OFFLINE'],
                 location: Optional[RobotLocation] = None,
                 battery_level: float = 0.0,
                 created_at: Optional[datetime] = None,
                 description: Optional[str] = None,
                 manufacturer: Optional[str] = None,
                 serial_number: Optional[str] = None,
                 firmware_version: Optional[str] = None,
                 last_maintenance: Optional[datetime] = None,
                 next_maintenance: Optional[datetime] = None,
                 total_operating_hours: float = 0.0,
                 sensors: Optional[List[str]] = None,
                 camera_streams: Optional[List[CameraStream]] = None,
                 documents_processed: Optional[int] = None,
                 search_accuracy: Optional[float] = None,
                 ai_model_version: Optional[str] = None,
                 location_name: Optional[str] = None,
                 building: Optional[str] = None,
                 room_number: Optional[int] = None):
        
        self.robot_id = robot_id
        self.name = name
        self.model = model
        self.status = status
        self.location = location
        self.battery_level = battery_level
        self.created_at = created_at or datetime.now()
        self.updated_at = datetime.now()
        
        # 추가 속성들
        self.description = description
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.firmware_version = firmware_version
        self.last_maintenance = last_maintenance
        self.next_maintenance = next_maintenance
        self.total_operating_hours = total_operating_hours
        self.sensors = sensors or []
        self.camera_streams = camera_streams or []
        self.documents_processed = documents_processed
        self.search_accuracy = search_accuracy
        self.ai_model_version = ai_model_version
        self.location_name = location_name
        self.building = building
        self.room_number = room_number
        
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        if self.location:
            data['location'] = asdict(self.location)
        if self.camera_streams:
            data['camera_streams'] = [asdict(stream) for stream in self.camera_streams]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Robot':
        """딕셔너리에서 생성"""
        # 데이터 복사본 생성
        robot_data = data.copy()
        
        # location과 camera_streams는 별도 처리
        location_data = robot_data.pop('location', None)
        camera_streams_data = robot_data.pop('camera_streams', [])
        
        # Robot 클래스에서 지원하지 않는 필드들 제거
        unsupported_fields = ['updated_at']  # Robot.__init__에서 지원하지 않는 필드들
        for field in unsupported_fields:
            robot_data.pop(field, None)
        
        # location 객체 생성
        location = None
        if location_data:
            try:
                location = RobotLocation(**location_data)
            except Exception as e:
                print(f"Location 데이터 파싱 실패: {e}")
        
        # camera_streams 객체 생성
        camera_streams = []
        for stream_data in camera_streams_data:
            try:
                stream = CameraStream(**stream_data)
                camera_streams.append(stream)
            except Exception as e:
                print(f"Camera stream 데이터 파싱 실패: {e}")
        
        # Robot 객체 생성
        try:
            robot = cls(**robot_data)
            robot.location = location
            robot.camera_streams = camera_streams
            return robot
        except Exception as e:
            print(f"Robot 객체 생성 실패: {e}, 데이터: {robot_data}")
            raise
    
    def update_status(self, status: str):
        """상태 업데이트"""
        self.status = status
        self.updated_at = datetime.now()
    
    def update_location(self, latitude: float, longitude: float, altitude: Optional[float] = None):
        """위치 업데이트"""
        self.location = RobotLocation(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            timestamp=datetime.now()
        )
        self.updated_at = datetime.now()
    
    def update_battery(self, battery_level: float):
        """배터리 레벨 업데이트"""
        self.battery_level = battery_level
        self.updated_at = datetime.now()
    
    def add_sensor_data(self, sensor_type: str, value: float, unit: str) -> SensorData:
        """센서 데이터 추가"""
        sensor_data = SensorData(
            sensor_type=sensor_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            robot_id=self.robot_id,
            sensor_id=str(uuid.uuid4())
        )
        return sensor_data
    
    def add_alert(self, level: str, message: str) -> Alert:
        """알림 추가"""
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            robot_id=self.robot_id,
            level=level,
            message=message,
            timestamp=datetime.now()
        )
        return alert
    
    def add_camera_stream(self, stream_url: str, stream_type: str = 'http', quality: str = 'medium') -> CameraStream:
        """카메라 스트림 추가"""
        stream = CameraStream(
            stream_id=str(uuid.uuid4()),
            robot_id=self.robot_id,
            stream_url=stream_url,
            stream_type=stream_type,
            quality=quality,
            created_at=datetime.now()
        )
        self.camera_streams.append(stream)
        return stream
    
    def get_active_camera_streams(self) -> List[CameraStream]:
        """활성 카메라 스트림 조회"""
        return [stream for stream in self.camera_streams if stream.is_active]
    
    def is_online(self) -> bool:
        """온라인 상태 확인"""
        return self.status == ROBOT_STATUS['ONLINE']
    
    def needs_maintenance(self) -> bool:
        """정비 필요 여부 확인"""
        if not self.next_maintenance:
            return False
        return datetime.now() >= self.next_maintenance
    
    def get_health_score(self) -> float:
        """건강도 점수 계산 (0-100)"""
        score = 100.0
        
        # 배터리 레벨에 따른 점수 감점
        if self.battery_level < 20:
            score -= 30
        elif self.battery_level < 50:
            score -= 15
        
        # 오프라인 상태 감점
        if self.status == ROBOT_STATUS['OFFLINE']:
            score -= 50
        elif self.status == ROBOT_STATUS['ERROR']:
            score -= 40
        elif self.status == ROBOT_STATUS['MAINTENANCE']:
            score -= 20
        
        # 정비 필요 시 감점
        if self.needs_maintenance():
            score -= 25
        
        return max(0.0, score)
