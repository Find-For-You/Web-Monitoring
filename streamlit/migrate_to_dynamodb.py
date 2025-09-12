"""
SQLite에서 DynamoDB로 데이터 마이그레이션 스크립트
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
from dynamodb_manager import DynamoDBManager
from aws_config import aws_config

class DataMigrator:
    def __init__(self, sqlite_db_path: str = "robot_monitoring.db"):
        """데이터 마이그레이션 초기화"""
        self.sqlite_db_path = sqlite_db_path
        self.dynamodb_manager = DynamoDBManager()
        
    def migrate_all_data(self):
        """모든 데이터 마이그레이션 실행"""
        print("데이터 마이그레이션을 시작합니다...")
        
        # AWS 연결 테스트
        if not aws_config.test_connection():
            print("AWS 연결에 실패했습니다. 자격 증명을 확인해주세요.")
            return False
        
        try:
            # 1. 사용자 데이터 마이그레이션
            self.migrate_users()
            
            # 2. 팀 데이터 마이그레이션
            self.migrate_teams()
            
            # 3. 프로젝트 데이터 마이그레이션
            self.migrate_projects()
            
            # 4. 로봇 데이터 마이그레이션
            self.migrate_robots()
            
            # 5. 카메라 데이터 마이그레이션
            self.migrate_cameras()
            
            # 6. 센서 데이터 마이그레이션
            self.migrate_sensor_data()
            
            # 7. 감지 결과 데이터 마이그레이션
            self.migrate_detection_results()
            
            # 8. 보고서 데이터 마이그레이션
            self.migrate_reports()
            
            # 9. 명령 히스토리 데이터 마이그레이션
            self.migrate_command_history()
            
            # 10. 로봇 상태 히스토리 데이터 마이그레이션
            self.migrate_robot_status_history()
            
            print("모든 데이터 마이그레이션이 완료되었습니다!")
            return True
            
        except Exception as e:
            print(f"마이그레이션 중 오류 발생: {e}")
            return False
    
    def get_sqlite_connection(self):
        """SQLite 연결 반환"""
        return sqlite3.connect(self.sqlite_db_path)
    
    def migrate_users(self):
        """사용자 데이터 마이그레이션"""
        print("사용자 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE isdeleted = 0")
        users = cursor.fetchall()
        
        for user in users:
            user_data = {
                'first_name': user[1] or '',
                'last_name': user[2] or '',
                'user_email': user[5],
                'user_password': user[6],
                'user_role': user[7] or 'User'
            }
            self.dynamodb_manager.create_user(user_data)
        
        conn.close()
        print(f"사용자 {len(users)}명 마이그레이션 완료")
    
    def migrate_teams(self):
        """팀 데이터 마이그레이션"""
        print("팀 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM teams")
        teams = cursor.fetchall()
        
        for team in teams:
            team_data = {
                'user_id': str(team[1]),
                'team_name': team[2],
                'team_description': team[4] or ''
            }
            self.dynamodb_manager.create_team(team_data)
        
        conn.close()
        print(f"팀 {len(teams)}개 마이그레이션 완료")
    
    def migrate_projects(self):
        """프로젝트 데이터 마이그레이션"""
        print("프로젝트 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        
        for project in projects:
            project_data = {
                'user_id': str(project[1]),
                'team_id': str(project[2]) if project[2] else None,
                'project_name': project[3],
                'project_description': project[4] or '',
                'project_visibility': bool(project[5]),
                'project_status': project[6] or 'Active',
                'project_start_date': project[7],
                'project_end_date': project[8]
            }
            self.dynamodb_manager.create_project(project_data)
        
        conn.close()
        print(f"프로젝트 {len(projects)}개 마이그레이션 완료")
    
    def migrate_robots(self):
        """로봇 데이터 마이그레이션"""
        print("로봇 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM robots")
        robots = cursor.fetchall()
        
        for robot in robots:
            robot_data = {
                'project_id': str(robot[1]),
                'robot_name': robot[2],
                'robot_battery': robot[3] or 100,
                'robot_connection': robot[4] or 0,
                'robot_ping': robot[5] or 0,
                'robot_status': robot[6] or 'Offline',
                'robot_location_x': robot[7] or 0.0,
                'robot_location_y': robot[8] or 0.0
            }
            self.dynamodb_manager.create_robot(robot_data)
        
        conn.close()
        print(f"로봇 {len(robots)}개 마이그레이션 완료")
    
    def migrate_cameras(self):
        """카메라 데이터 마이그레이션"""
        print("카메라 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cameras")
        cameras = cursor.fetchall()
        
        for camera in cameras:
            camera_data = {
                'robot_id': str(camera[1]),
                'camera_name': camera[2],
                'camera_stream_url': camera[3] or '',
                'camera_isactivate': bool(camera[4]),
                'camera_position': camera[5] or 'head'
            }
            self.dynamodb_manager.create_camera(camera_data)
        
        conn.close()
        print(f"카메라 {len(cameras)}개 마이그레이션 완료")
    
    def migrate_sensor_data(self):
        """센서 데이터 마이그레이션"""
        print("센서 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sensor_data")
        sensor_data = cursor.fetchall()
        
        for sensor in sensor_data:
            sensor_data_dict = {
                'robot_id': str(sensor[1]),
                'sensor_imu_gyro': json.loads(sensor[2]) if sensor[2] else {},
                'sensor_imu_acc': json.loads(sensor[3]) if sensor[3] else {},
                'sensor_temp': sensor[6] or 0.0,
                'sensor_humid': sensor[7] or 0.0,
                'sensor_press': sensor[8] or 0.0
            }
            self.dynamodb_manager.create_sensor_data(sensor_data_dict)
        
        conn.close()
        print(f"센서 데이터 {len(sensor_data)}개 마이그레이션 완료")
    
    def migrate_detection_results(self):
        """감지 결과 데이터 마이그레이션"""
        print("감지 결과 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM detection_results")
        detections = cursor.fetchall()
        
        for detection in detections:
            detection_data = {
                'camera_id': str(detection[1]),
                'detection_class': detection[2],
                'detection_conf': detection[3] or 0.0,
                'detection_bbox': json.loads(detection[4]) if detection[4] else {}
            }
            self.dynamodb_manager.create_detection_result(detection_data)
        
        conn.close()
        print(f"감지 결과 {len(detections)}개 마이그레이션 완료")
    
    def migrate_reports(self):
        """보고서 데이터 마이그레이션"""
        print("보고서 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM reports")
        reports = cursor.fetchall()
        
        for report in reports:
            report_data = {
                'project_id': str(report[1]),
                'user_id': str(report[2]),
                'report_title': report[3],
                'report_content': report[4] or '',
                'report_detected': json.loads(report[5]) if report[5] else {}
            }
            self.dynamodb_manager.create_report(report_data)
        
        conn.close()
        print(f"보고서 {len(reports)}개 마이그레이션 완료")
    
    def migrate_command_history(self):
        """명령 히스토리 데이터 마이그레이션"""
        print("명령 히스토리 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM command_history")
        commands = cursor.fetchall()
        
        for command in commands:
            command_data = {
                'robot_id': str(command[1]),
                'user_id': str(command[2]),
                'command_type': command[3],
                'command_detail': json.loads(command[4]) if command[4] else {}
            }
            self.dynamodb_manager.create_command_history(command_data)
        
        conn.close()
        print(f"명령 히스토리 {len(commands)}개 마이그레이션 완료")
    
    def migrate_robot_status_history(self):
        """로봇 상태 히스토리 데이터 마이그레이션"""
        print("로봇 상태 히스토리 데이터를 마이그레이션하는 중...")
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM robot_status_history")
        status_history = cursor.fetchall()
        
        for status in status_history:
            status_data = {
                'robot_id': str(status[1]),
                'status_battery': status[2] or 0,
                'status_connect': status[3] or 'disconnected',
                'status_robot': status[4] or '',
                'status_event': status[5] or 'unknown'
            }
            self.dynamodb_manager.create_robot_status_history(status_data)
        
        conn.close()
        print(f"로봇 상태 히스토리 {len(status_history)}개 마이그레이션 완료")

# 사용 예시
if __name__ == "__main__":
    migrator = DataMigrator()
    
    # AWS 자격 증명 설정 (실제 사용시에는 환경변수나 AWS CLI 사용 권장)
    # aws_config.setup_credentials(
    #     access_key="YOUR_ACCESS_KEY",
    #     secret_key="YOUR_SECRET_KEY"
    # )
    
    # 데이터 마이그레이션 실행
    migrator.migrate_all_data()
