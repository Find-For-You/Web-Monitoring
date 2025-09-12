"""
DynamoDB 데이터 접근 레이어
기존 SQLite DatabaseManager를 DynamoDB로 대체
"""

import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from boto3.dynamodb.conditions import Key, Attr

class DynamoDBManager:
    def __init__(self, region_name: str = 'ap-northeast-2', table_name: str = 'RobotMonitoring'):
        """DynamoDB 매니저 초기화"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
    
    def _get_entity_keys(self, entity_type: str, entity_id: str, related_entity: str = None, related_id: str = None) -> Dict[str, str]:
        """엔티티 타입에 따른 DynamoDB 키 생성"""
        keys = {
            'PK': f"{entity_type}#{entity_id}",
            'SK': f"{entity_type}#{entity_id}"
        }
        
        # GSI 키 설정
        if entity_type == 'USER':
            keys['GSI1PK'] = f"USER#{entity_id}"
            keys['GSI1SK'] = f"USER#{entity_id}"
        elif entity_type == 'TEAM':
            keys['GSI1PK'] = f"TEAM#{entity_id}"
            keys['GSI1SK'] = f"TEAM#{entity_id}"
        elif entity_type == 'PROJECT':
            keys['GSI2PK'] = f"PROJECT#{entity_id}"
            keys['GSI2SK'] = f"PROJECT#{entity_id}"
        elif entity_type == 'ROBOT':
            keys['GSI3PK'] = f"ROBOT#{entity_id}"
            keys['GSI3SK'] = f"ROBOT#{entity_id}"
        elif entity_type == 'CAMERA':
            keys['GSI3PK'] = f"ROBOT#{related_id}"
            keys['GSI3SK'] = f"CAMERA#{entity_id}"
        elif entity_type == 'DETECTION_RESULT':
            keys['GSI3PK'] = f"CAMERA#{related_id}"
            keys['GSI3SK'] = f"DETECTION#{entity_id}"
        elif entity_type == 'SENSOR_DATA':
            keys['GSI3PK'] = f"ROBOT#{related_id}"
            keys['GSI3SK'] = f"SENSOR#{entity_id}"
        elif entity_type == 'REPORT':
            keys['GSI2PK'] = f"PROJECT#{related_id}"
            keys['GSI2SK'] = f"REPORT#{entity_id}"
        elif entity_type == 'COMMAND_HISTORY':
            keys['GSI3PK'] = f"ROBOT#{related_id}"
            keys['GSI3SK'] = f"COMMAND#{entity_id}"
        elif entity_type == 'ROBOT_STATUS_HISTORY':
            keys['GSI3PK'] = f"ROBOT#{related_id}"
            keys['GSI3SK'] = f"STATUS#{entity_id}"
        elif entity_type == 'TEAM_MEMBER':
            keys['GSI1PK'] = f"TEAM#{related_id}"
            keys['GSI1SK'] = f"USER#{entity_id}"
        
        return keys

    def _generate_id(self, entity_type: str) -> str:
        """새로운 ID 생성 (타임스탬프 기반)"""
        return str(int(datetime.now().timestamp() * 1000))

    # === User 관련 함수들 ===
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """사용자 생성"""
        user_id = self._generate_id('USER')
        keys = self._get_entity_keys('USER', user_id)
        
        item = {
            **keys,
            'entity_type': 'USER',
            'user_id': user_id,
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'user_email': user_data.get('user_email'),
            'user_password': user_data.get('user_password'),
            'user_role': user_data.get('user_role', 'User'),
            'isdeleted': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return user_id

    def get_users(self) -> List[Dict[str, Any]]:
        """모든 사용자 조회"""
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').begins_with('USER#'),
            FilterExpression=Attr('isdeleted').eq(False)
        )
        return response['Items']

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """이메일로 사용자 조회"""
        response = self.table.scan(
            FilterExpression=Attr('user_email').eq(email) & Attr('entity_type').eq('USER') & Attr('isdeleted').eq(False)
        )
        return response['Items'][0] if response['Items'] else None

    # === Team 관련 함수들 ===
    def create_team(self, team_data: Dict[str, Any]) -> str:
        """팀 생성"""
        team_id = self._generate_id('TEAM')
        keys = self._get_entity_keys('TEAM', team_id)
        
        item = {
            **keys,
            'entity_type': 'TEAM',
            'team_id': team_id,
            'user_id': team_data.get('user_id'),
            'team_name': team_data.get('team_name'),
            'team_description': team_data.get('team_description'),
            'team_created_at': datetime.now().isoformat(),
            'team_updated_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return team_id

    def get_teams(self) -> List[Dict[str, Any]]:
        """모든 팀 조회"""
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').begins_with('TEAM#')
        )
        return response['Items']

    def add_team_member(self, team_id: str, user_id: str, role: str = 'Member') -> str:
        """팀 멤버 추가"""
        member_id = self._generate_id('TEAM_MEMBER')
        keys = self._get_entity_keys('TEAM_MEMBER', member_id, 'TEAM', team_id)
        
        item = {
            **keys,
            'entity_type': 'TEAM_MEMBER',
            'teammember_id': member_id,
            'team_id': team_id,
            'user_id': user_id,
            'teammember_role': role,
            'teammember_joined_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return member_id

    # === Project 관련 함수들 ===
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """프로젝트 생성"""
        project_id = self._generate_id('PROJECT')
        keys = self._get_entity_keys('PROJECT', project_id)
        
        item = {
            **keys,
            'entity_type': 'PROJECT',
            'project_id': project_id,
            'user_id': project_data.get('user_id'),
            'team_id': project_data.get('team_id'),
            'project_name': project_data.get('project_name'),
            'project_description': project_data.get('project_description'),
            'project_visibility': project_data.get('project_visibility', True),
            'project_status': project_data.get('project_status', 'Active'),
            'project_start_date': project_data.get('project_start_date'),
            'project_end_date': project_data.get('project_end_date'),
            'project_created_at': datetime.now().isoformat(),
            'project_updated_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return project_id

    def get_projects(self) -> List[Dict[str, Any]]:
        """모든 프로젝트 조회"""
        response = self.table.query(
            IndexName='GSI2',
            KeyConditionExpression=Key('GSI2PK').begins_with('PROJECT#')
        )
        return response['Items']

    # === Robot 관련 함수들 ===
    def create_robot(self, robot_data: Dict[str, Any]) -> str:
        """로봇 생성"""
        robot_id = self._generate_id('ROBOT')
        keys = self._get_entity_keys('ROBOT', robot_id)
        
        item = {
            **keys,
            'entity_type': 'ROBOT',
            'robot_id': robot_id,
            'project_id': robot_data.get('project_id'),
            'robot_name': robot_data.get('robot_name'),
            'robot_battery': robot_data.get('robot_battery', 100),
            'robot_connection': robot_data.get('robot_connection', 0),
            'robot_ping': robot_data.get('robot_ping', 0),
            'robot_status': robot_data.get('robot_status', 'Offline'),
            'robot_location_x': robot_data.get('robot_location_x', 0.0),
            'robot_location_y': robot_data.get('robot_location_y', 0.0),
            'robot_created_at': datetime.now().isoformat(),
            'robot_update_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return robot_id

    def get_robots(self) -> List[Dict[str, Any]]:
        """모든 로봇 조회"""
        response = self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').begins_with('ROBOT#')
        )
        return response['Items']

    def update_robot_status(self, robot_id: str, status_data: Dict[str, Any]):
        """로봇 상태 업데이트"""
        keys = self._get_entity_keys('ROBOT', robot_id)
        
        update_expression = "SET robot_battery = :battery, robot_connection = :connection, robot_ping = :ping, robot_status = :status, robot_location_x = :x, robot_location_y = :y, robot_update_at = :updated_at"
        
        expression_values = {
            ':battery': status_data.get('robot_battery'),
            ':connection': status_data.get('robot_connection'),
            ':ping': status_data.get('robot_ping'),
            ':status': status_data.get('robot_status'),
            ':x': status_data.get('robot_location_x'),
            ':y': status_data.get('robot_location_y'),
            ':updated_at': datetime.now().isoformat()
        }
        
        self.table.update_item(
            Key={'PK': keys['PK'], 'SK': keys['SK']},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

    # === Camera 관련 함수들 ===
    def create_camera(self, camera_data: Dict[str, Any]) -> str:
        """카메라 생성"""
        camera_id = self._generate_id('CAMERA')
        robot_id = camera_data.get('robot_id')
        keys = self._get_entity_keys('CAMERA', camera_id, 'ROBOT', robot_id)
        
        item = {
            **keys,
            'entity_type': 'CAMERA',
            'camera_id': camera_id,
            'robot_id': robot_id,
            'camera_name': camera_data.get('camera_name'),
            'camera_stream_url': camera_data.get('camera_stream_url'),
            'camera_isactivate': camera_data.get('camera_isactivate', True),
            'camera_position': camera_data.get('camera_position', 'head'),
            'camera_created_at': datetime.now().isoformat(),
            'camera_updated_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return camera_id

    def get_cameras_by_robot(self, robot_id: str) -> List[Dict[str, Any]]:
        """로봇별 카메라 조회"""
        response = self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').eq(f'ROBOT#{robot_id}') & Key('GSI3SK').begins_with('CAMERA#')
        )
        return response['Items']

    # === Detection Result 관련 함수들 ===
    def create_detection_result(self, detection_data: Dict[str, Any]) -> str:
        """감지 결과 생성"""
        detection_id = self._generate_id('DETECTION_RESULT')
        camera_id = detection_data.get('camera_id')
        keys = self._get_entity_keys('DETECTION_RESULT', detection_id, 'CAMERA', camera_id)
        
        item = {
            **keys,
            'entity_type': 'DETECTION_RESULT',
            'detection_id': detection_id,
            'camera_id': camera_id,
            'detection_class': detection_data.get('detection_class'),
            'detection_conf': detection_data.get('detection_conf'),
            'detection_bbox': detection_data.get('detection_bbox', {}),
            'detection_created_at': datetime.now().isoformat(),
            'detection_update_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return detection_id

    def get_detection_results_by_camera(self, camera_id: str) -> List[Dict[str, Any]]:
        """카메라별 감지 결과 조회"""
        response = self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').eq(f'CAMERA#{camera_id}') & Key('GSI3SK').begins_with('DETECTION#'),
            ScanIndexForward=False  # 최신순 정렬
        )
        return response['Items']

    # === Sensor Data 관련 함수들 ===
    def create_sensor_data(self, sensor_data: Dict[str, Any]) -> str:
        """센서 데이터 생성"""
        sensor_id = self._generate_id('SENSOR_DATA')
        robot_id = sensor_data.get('robot_id')
        keys = self._get_entity_keys('SENSOR_DATA', sensor_id, 'ROBOT', robot_id)
        
        item = {
            **keys,
            'entity_type': 'SENSOR_DATA',
            'sensor_id': sensor_id,
            'robot_id': robot_id,
            'sensor_imu_gyro': sensor_data.get('sensor_imu_gyro', {}),
            'sensor_imu_acc': sensor_data.get('sensor_imu_acc', {}),
            'sensor_temp': sensor_data.get('sensor_temp'),
            'sensor_humid': sensor_data.get('sensor_humid'),
            'sensor_press': sensor_data.get('sensor_press'),
            'sensor_created_at': datetime.now().isoformat(),
            'sensor_update_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return sensor_id

    def get_sensor_data_by_robot(self, robot_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """로봇별 센서 데이터 조회"""
        response = self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').eq(f'ROBOT#{robot_id}') & Key('GSI3SK').begins_with('SENSOR#'),
            ScanIndexForward=False,  # 최신순 정렬
            Limit=limit
        )
        return response['Items']

    # === Report 관련 함수들 ===
    def create_report(self, report_data: Dict[str, Any]) -> str:
        """보고서 생성"""
        report_id = self._generate_id('REPORT')
        project_id = report_data.get('project_id')
        keys = self._get_entity_keys('REPORT', report_id, 'PROJECT', project_id)
        
        item = {
            **keys,
            'entity_type': 'REPORT',
            'report_id': report_id,
            'project_id': project_id,
            'user_id': report_data.get('user_id'),
            'report_title': report_data.get('report_title'),
            'report_content': report_data.get('report_content'),
            'report_detected': report_data.get('report_detected', {}),
            'report_created_at': datetime.now().isoformat(),
            'report_updated_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return report_id

    def get_reports_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """프로젝트별 보고서 조회"""
        response = self.table.query(
            IndexName='GSI2',
            KeyConditionExpression=Key('GSI2PK').eq(f'PROJECT#{project_id}') & Key('GSI2SK').begins_with('REPORT#'),
            ScanIndexForward=False  # 최신순 정렬
        )
        return response['Items']

    # === Command History 관련 함수들 ===
    def create_command_history(self, command_data: Dict[str, Any]) -> str:
        """명령 히스토리 생성"""
        command_id = self._generate_id('COMMAND_HISTORY')
        robot_id = command_data.get('robot_id')
        keys = self._get_entity_keys('COMMAND_HISTORY', command_id, 'ROBOT', robot_id)
        
        item = {
            **keys,
            'entity_type': 'COMMAND_HISTORY',
            'command_id': command_id,
            'robot_id': robot_id,
            'user_id': command_data.get('user_id'),
            'command_type': command_data.get('command_type'),
            'command_detail': command_data.get('command_detail', {}),
            'command_created_at': datetime.now().isoformat(),
            'command_update_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return command_id

    def get_command_history_by_robot(self, robot_id: str) -> List[Dict[str, Any]]:
        """로봇별 명령 히스토리 조회"""
        response = self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').eq(f'ROBOT#{robot_id}') & Key('GSI3SK').begins_with('COMMAND#'),
            ScanIndexForward=False  # 최신순 정렬
        )
        return response['Items']

    # === Robot Status History 관련 함수들 ===
    def create_robot_status_history(self, status_data: Dict[str, Any]) -> str:
        """로봇 상태 히스토리 생성"""
        status_id = self._generate_id('ROBOT_STATUS_HISTORY')
        robot_id = status_data.get('robot_id')
        keys = self._get_entity_keys('ROBOT_STATUS_HISTORY', status_id, 'ROBOT', robot_id)
        
        item = {
            **keys,
            'entity_type': 'ROBOT_STATUS_HISTORY',
            'status_id': status_id,
            'robot_id': robot_id,
            'status_battery': status_data.get('status_battery'),
            'status_connect': status_data.get('status_connect'),
            'status_robot': status_data.get('status_robot'),
            'status_event': status_data.get('status_event'),
            'status_created_at': datetime.now().isoformat(),
            'status_update_at': datetime.now().isoformat()
        }
        
        self.table.put_item(Item=item)
        return status_id

    def get_robot_status_history_by_robot(self, robot_id: str) -> List[Dict[str, Any]]:
        """로봇별 상태 히스토리 조회"""
        response = self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').eq(f'ROBOT#{robot_id}') & Key('GSI3SK').begins_with('STATUS#'),
            ScanIndexForward=False  # 최신순 정렬
        )
        return response['Items']

    # === 통계 함수들 ===
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """대시보드 통계 데이터"""
        # 로봇 통계
        robots = self.get_robots()
        total_robots = len(robots)
        online_robots = len([r for r in robots if r.get('robot_status') == 'Online'])
        avg_battery = sum([r.get('robot_battery', 0) for r in robots]) / total_robots if total_robots > 0 else 0
        
        # 최근 24시간 감지 결과 통계 (실제로는 시간 필터링 필요)
        all_detections = []
        for robot in robots:
            cameras = self.get_cameras_by_robot(robot['robot_id'])
            for camera in cameras:
                detections = self.get_detection_results_by_camera(camera['camera_id'])
                all_detections.extend(detections)
        
        total_detections = len(all_detections)
        active_cameras = len(set([d.get('camera_id') for d in all_detections]))
        
        # 센서 데이터 통계
        all_sensor_data = []
        for robot in robots:
            sensor_data = self.get_sensor_data_by_robot(robot['robot_id'], limit=100)
            all_sensor_data.extend(sensor_data)
        
        total_sensor_readings = len(all_sensor_data)
        avg_temperature = sum([s.get('sensor_temp', 0) for s in all_sensor_data]) / total_sensor_readings if total_sensor_readings > 0 else 0
        avg_humidity = sum([s.get('sensor_humid', 0) for s in all_sensor_data]) / total_sensor_readings if total_sensor_readings > 0 else 0
        
        return {
            'robot_stats': {
                'total_robots': total_robots,
                'online_robots': online_robots,
                'avg_battery': round(avg_battery, 2)
            },
            'detection_stats': {
                'total_detections': total_detections,
                'active_cameras': active_cameras
            },
            'sensor_stats': {
                'total_sensor_readings': total_sensor_readings,
                'avg_temperature': round(avg_temperature, 2),
                'avg_humidity': round(avg_humidity, 2)
            }
        }

# 전역 DynamoDB 매니저 인스턴스
dynamodb_manager = DynamoDBManager()
