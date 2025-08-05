import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path: str = "robot_monitoring.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """데이터베이스 연결 반환"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """ERD에 맞는 데이터베이스 스키마 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # User 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                profile_picture BLOB,
                isdeleted BOOLEAN DEFAULT FALSE,
                user_email VARCHAR(100) UNIQUE,
                user_password VARCHAR(255),
                user_role VARCHAR(20) DEFAULT 'User',
                last_login_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Team 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                team_name VARCHAR(100),
                team_picture BLOB,
                team_description TEXT,
                team_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                team_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Team Member 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                teammember_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                user_id INTEGER,
                teammember_role VARCHAR(50),
                teammember_joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Project 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                team_id INTEGER,
                project_name VARCHAR(100),
                project_description TEXT,
                project_visibility BOOLEAN DEFAULT TRUE,
                project_status VARCHAR(20) DEFAULT 'Active',
                project_start_date DATETIME,
                project_end_date DATETIME,
                project_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                project_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        # Robots 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robots (
                robot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                robot_name VARCHAR(100),
                robot_battery INTEGER DEFAULT 100,
                robot_connection INTEGER DEFAULT 0,
                robot_ping INTEGER DEFAULT 0,
                robot_status VARCHAR(20) DEFAULT 'Offline',
                robot_location_x FLOAT DEFAULT 0.0,
                robot_location_y FLOAT DEFAULT 0.0,
                robot_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                robot_update_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # Camera 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                camera_id INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id INTEGER,
                camera_name VARCHAR(100),
                camera_stream_url TEXT,
                camera_isactivate BOOLEAN DEFAULT TRUE,
                camera_position VARCHAR(20) DEFAULT 'head',
                camera_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                camera_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (robot_id) REFERENCES robots (robot_id)
            )
        ''')
        
        # Detection Result 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_results (
                detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER,
                detection_class VARCHAR(100),
                detection_conf FLOAT,
                detection_bbox TEXT, -- JSON 형태로 저장
                detection_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                detection_update_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (camera_id) REFERENCES cameras (camera_id)
            )
        ''')
        
        # Sensor Data 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id INTEGER,
                sensor_imu_gyro TEXT, -- JSON 형태로 저장
                sensor_imu_acc TEXT, -- JSON 형태로 저장
                sensor_lidar_map BLOB,
                sensor_temp FLOAT,
                sensor_humid FLOAT,
                sensor_press FLOAT,
                sensor_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sensor_update_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (robot_id) REFERENCES robots (robot_id)
            )
        ''')
        
        # Robot Status History 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS robot_status_history (
                status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id INTEGER,
                status_battery INTEGER,
                status_connect VARCHAR(20),
                status_robot VARCHAR(100),
                status_event VARCHAR(50),
                status_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status_update_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (robot_id) REFERENCES robots (robot_id)
            )
        ''')
        
        # Report 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_id INTEGER,
                report_title VARCHAR(100),
                report_content TEXT,
                report_detected TEXT, -- JSON 형태로 저장
                report_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                report_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (project_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Command History 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                command_id INTEGER PRIMARY KEY AUTOINCREMENT,
                robot_id INTEGER,
                user_id INTEGER,
                command_type VARCHAR(100),
                command_detail TEXT, -- JSON 형태로 저장
                command_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                command_update_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (robot_id) REFERENCES robots (robot_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # === User 관련 함수들 ===
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """사용자 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (first_name, last_name, user_email, user_password, user_role)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_data.get('first_name'),
            user_data.get('last_name'),
            user_data.get('user_email'),
            user_data.get('user_password'),
            user_data.get('user_role', 'User')
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_users(self) -> List[Dict[str, Any]]:
        """모든 사용자 조회"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM users WHERE isdeleted = FALSE", conn)
        conn.close()
        return df.to_dict('records')
    
    # === Team 관련 함수들 ===
    def create_team(self, team_data: Dict[str, Any]) -> int:
        """팀 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teams (user_id, team_name, team_description)
            VALUES (?, ?, ?)
        ''', (
            team_data.get('user_id'),
            team_data.get('team_name'),
            team_data.get('team_description')
        ))
        
        team_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return team_id
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """모든 팀 조회"""
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT t.*, u.first_name, u.last_name 
            FROM teams t 
            LEFT JOIN users u ON t.user_id = u.user_id
        """, conn)
        conn.close()
        return df.to_dict('records')
    
    # === Project 관련 함수들 ===
    def create_project(self, project_data: Dict[str, Any]) -> int:
        """프로젝트 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO projects (user_id, team_id, project_name, project_description, 
                                project_visibility, project_status, project_start_date, project_end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_data.get('user_id'),
            project_data.get('team_id'),
            project_data.get('project_name'),
            project_data.get('project_description'),
            project_data.get('project_visibility', True),
            project_data.get('project_status', 'Active'),
            project_data.get('project_start_date'),
            project_data.get('project_end_date')
        ))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """모든 프로젝트 조회"""
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT p.*, u.first_name, u.last_name, t.team_name
            FROM projects p 
            LEFT JOIN users u ON p.user_id = u.user_id
            LEFT JOIN teams t ON p.team_id = t.team_id
        """, conn)
        conn.close()
        return df.to_dict('records')
    
    # === Robot 관련 함수들 ===
    def create_robot(self, robot_data: Dict[str, Any]) -> int:
        """로봇 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO robots (project_id, robot_name, robot_battery, robot_connection, 
                              robot_ping, robot_status, robot_location_x, robot_location_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            robot_data.get('project_id'),
            robot_data.get('robot_name'),
            robot_data.get('robot_battery', 100),
            robot_data.get('robot_connection', 0),
            robot_data.get('robot_ping', 0),
            robot_data.get('robot_status', 'Offline'),
            robot_data.get('robot_location_x', 0.0),
            robot_data.get('robot_location_y', 0.0)
        ))
        
        robot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return robot_id
    
    def get_robots(self) -> List[Dict[str, Any]]:
        """모든 로봇 조회"""
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT r.*, p.project_name 
            FROM robots r 
            LEFT JOIN projects p ON r.project_id = p.project_id
        """, conn)
        conn.close()
        return df.to_dict('records')
    
    def update_robot_status(self, robot_id: int, status_data: Dict[str, Any]):
        """로봇 상태 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE robots 
            SET robot_battery = ?, robot_connection = ?, robot_ping = ?, 
                robot_status = ?, robot_location_x = ?, robot_location_y = ?,
                robot_update_at = CURRENT_TIMESTAMP
            WHERE robot_id = ?
        ''', (
            status_data.get('robot_battery'),
            status_data.get('robot_connection'),
            status_data.get('robot_ping'),
            status_data.get('robot_status'),
            status_data.get('robot_location_x'),
            status_data.get('robot_location_y'),
            robot_id
        ))
        
        conn.commit()
        conn.close()
    
    # === Camera 관련 함수들 ===
    def create_camera(self, camera_data: Dict[str, Any]) -> int:
        """카메라 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cameras (robot_id, camera_name, camera_stream_url, 
                               camera_isactivate, camera_position)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            camera_data.get('robot_id'),
            camera_data.get('camera_name'),
            camera_data.get('camera_stream_url'),
            camera_data.get('camera_isactivate', True),
            camera_data.get('camera_position', 'head')
        ))
        
        camera_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return camera_id
    
    def get_cameras(self) -> List[Dict[str, Any]]:
        """모든 카메라 조회"""
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT c.*, r.robot_name 
            FROM cameras c 
            LEFT JOIN robots r ON c.robot_id = r.robot_id
        """, conn)
        conn.close()
        return df.to_dict('records')
    
    # === Detection Result 관련 함수들 ===
    def create_detection_result(self, detection_data: Dict[str, Any]) -> int:
        """감지 결과 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detection_results (camera_id, detection_class, detection_conf, detection_bbox)
            VALUES (?, ?, ?, ?)
        ''', (
            detection_data.get('camera_id'),
            detection_data.get('detection_class'),
            detection_data.get('detection_conf'),
            json.dumps(detection_data.get('detection_bbox', {}))
        ))
        
        detection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return detection_id
    
    def get_detection_results(self, camera_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """감지 결과 조회"""
        conn = self.get_connection()
        
        if camera_id:
            df = pd.read_sql_query("""
                SELECT dr.*, c.camera_name 
                FROM detection_results dr 
                LEFT JOIN cameras c ON dr.camera_id = c.camera_id
                WHERE dr.camera_id = ?
                ORDER BY dr.detection_created_at DESC
            """, conn, params=[camera_id])
        else:
            df = pd.read_sql_query("""
                SELECT dr.*, c.camera_name 
                FROM detection_results dr 
                LEFT JOIN cameras c ON dr.camera_id = c.camera_id
                ORDER BY dr.detection_created_at DESC
            """, conn)
        
        conn.close()
        return df.to_dict('records')
    
    # === Sensor Data 관련 함수들 ===
    def create_sensor_data(self, sensor_data: Dict[str, Any]) -> int:
        """센서 데이터 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data (robot_id, sensor_imu_gyro, sensor_imu_acc, 
                                   sensor_temp, sensor_humid, sensor_press)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            sensor_data.get('robot_id'),
            json.dumps(sensor_data.get('sensor_imu_gyro', {})),
            json.dumps(sensor_data.get('sensor_imu_acc', {})),
            sensor_data.get('sensor_temp'),
            sensor_data.get('sensor_humid'),
            sensor_data.get('sensor_press')
        ))
        
        sensor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return sensor_id
    
    def get_sensor_data(self, robot_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """센서 데이터 조회"""
        conn = self.get_connection()
        
        if robot_id:
            df = pd.read_sql_query("""
                SELECT * FROM sensor_data 
                WHERE robot_id = ?
                ORDER BY sensor_created_at DESC 
                LIMIT ?
            """, conn, params=[robot_id, limit])
        else:
            df = pd.read_sql_query("""
                SELECT * FROM sensor_data 
                ORDER BY sensor_created_at DESC 
                LIMIT ?
            """, conn, params=[limit])
        
        conn.close()
        return df.to_dict('records')
    
    # === Report 관련 함수들 ===
    def create_report(self, report_data: Dict[str, Any]) -> int:
        """보고서 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (project_id, user_id, report_title, report_content, report_detected)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            report_data.get('project_id'),
            report_data.get('user_id'),
            report_data.get('report_title'),
            report_data.get('report_content'),
            json.dumps(report_data.get('report_detected', {}))
        ))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id
    
    def get_reports(self) -> List[Dict[str, Any]]:
        """모든 보고서 조회"""
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT r.*, p.project_name, u.first_name, u.last_name
            FROM reports r 
            LEFT JOIN projects p ON r.project_id = p.project_id
            LEFT JOIN users u ON r.user_id = u.user_id
            ORDER BY r.report_created_at DESC
        """, conn)
        conn.close()
        return df.to_dict('records')
    
    # === Command History 관련 함수들 ===
    def create_command_history(self, command_data: Dict[str, Any]) -> int:
        """명령 히스토리 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO command_history (robot_id, user_id, command_type, command_detail)
            VALUES (?, ?, ?, ?)
        ''', (
            command_data.get('robot_id'),
            command_data.get('user_id'),
            command_data.get('command_type'),
            json.dumps(command_data.get('command_detail', {}))
        ))
        
        command_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return command_id
    
    def get_command_history(self, robot_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """명령 히스토리 조회"""
        conn = self.get_connection()
        
        if robot_id:
            df = pd.read_sql_query("""
                SELECT ch.*, r.robot_name, u.first_name, u.last_name
                FROM command_history ch 
                LEFT JOIN robots r ON ch.robot_id = r.robot_id
                LEFT JOIN users u ON ch.user_id = u.user_id
                WHERE ch.robot_id = ?
                ORDER BY ch.command_created_at DESC
            """, conn, params=[robot_id])
        else:
            df = pd.read_sql_query("""
                SELECT ch.*, r.robot_name, u.first_name, u.last_name
                FROM command_history ch 
                LEFT JOIN robots r ON ch.robot_id = r.robot_id
                LEFT JOIN users u ON ch.user_id = u.user_id
                ORDER BY ch.command_created_at DESC
            """, conn)
        
        conn.close()
        return df.to_dict('records')
    
    # === Robot Status History 관련 함수들 ===
    def create_robot_status_history(self, status_data: Dict[str, Any]) -> int:
        """로봇 상태 히스토리 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO robot_status_history (robot_id, status_battery, status_connect, 
                                           status_robot, status_event)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            status_data.get('robot_id'),
            status_data.get('status_battery'),
            status_data.get('status_connect'),
            status_data.get('status_robot'),
            status_data.get('status_event')
        ))
        
        status_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return status_id
    
    def get_robot_status_history(self, robot_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """로봇 상태 히스토리 조회"""
        conn = self.get_connection()
        
        if robot_id:
            df = pd.read_sql_query("""
                SELECT rsh.*, r.robot_name
                FROM robot_status_history rsh 
                LEFT JOIN robots r ON rsh.robot_id = r.robot_id
                WHERE rsh.robot_id = ?
                ORDER BY rsh.status_created_at DESC
            """, conn, params=[robot_id])
        else:
            df = pd.read_sql_query("""
                SELECT rsh.*, r.robot_name
                FROM robot_status_history rsh 
                LEFT JOIN robots r ON rsh.robot_id = r.robot_id
                ORDER BY rsh.status_created_at DESC
            """, conn)
        
        conn.close()
        return df.to_dict('records')
    
    # === 통계 함수들 ===
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """대시보드 통계 데이터"""
        conn = self.get_connection()
        
        # 로봇 통계
        robot_stats = pd.read_sql_query("""
            SELECT 
                COUNT(*) as total_robots,
                SUM(CASE WHEN robot_status = 'Online' THEN 1 ELSE 0 END) as online_robots,
                AVG(robot_battery) as avg_battery
            FROM robots
        """, conn)
        
        # 감지 결과 통계
        detection_stats = pd.read_sql_query("""
            SELECT 
                COUNT(*) as total_detections,
                COUNT(DISTINCT camera_id) as active_cameras
            FROM detection_results
            WHERE detection_created_at >= datetime('now', '-24 hours')
        """, conn)
        
        # 센서 데이터 통계
        sensor_stats = pd.read_sql_query("""
            SELECT 
                COUNT(*) as total_sensor_readings,
                AVG(sensor_temp) as avg_temperature,
                AVG(sensor_humid) as avg_humidity
            FROM sensor_data
            WHERE sensor_created_at >= datetime('now', '-24 hours')
        """, conn)
        
        conn.close()
        
        return {
            'robot_stats': robot_stats.to_dict('records')[0] if not robot_stats.empty else {},
            'detection_stats': detection_stats.to_dict('records')[0] if not detection_stats.empty else {},
            'sensor_stats': sensor_stats.to_dict('records')[0] if not sensor_stats.empty else {}
        }

# 전역 데이터베이스 매니저 인스턴스
db = DatabaseManager() 