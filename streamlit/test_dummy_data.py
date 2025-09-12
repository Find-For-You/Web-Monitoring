#!/usr/bin/env python3
"""
더미 데이터 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.dynamodb_client import db_client

def test_dummy_data():
    """더미 데이터 테스트"""
    print("=== 더미 데이터 테스트 시작 ===")
    
    # 1. 모든 로봇 데이터 조회
    print("\n1. 모든 로봇 데이터 조회:")
    robots = db_client.get_all_robots()
    print(f"총 {len(robots)}개의 로봇이 있습니다.")
    
    if robots:
        first_robot = robots[0]
        print(f"첫 번째 로봇: {first_robot['name']} (ID: {first_robot['robot_id']})")
        print(f"상태: {first_robot['status']}, 배터리: {first_robot['battery_level']}%")
        print(f"위치: {first_robot['location']['latitude']}, {first_robot['location']['longitude']}")
        print(f"처리된 문서: {first_robot.get('documents_processed', 'N/A')}개")
        print(f"검색 정확도: {first_robot.get('search_accuracy', 'N/A')}%")
        print(f"AI 모델 버전: {first_robot.get('ai_model_version', 'N/A')}")
    
    # 2. 특정 로봇 조회
    if robots:
        robot_id = robots[0]['robot_id']
        print(f"\n2. 로봇 ID '{robot_id}' 조회:")
        robot = db_client.get_robot_by_id(robot_id)
        if robot:
            print(f"로봇 이름: {robot['name']}")
            print(f"모델: {robot['model']}")
            print(f"제조사: {robot['manufacturer']}")
            print(f"위치: {robot.get('location_name', 'N/A')}")
            print(f"건물: {robot.get('building', 'N/A')}")
    
    # 3. 센서 데이터 조회
    if robots:
        robot_id = robots[0]['robot_id']
        print(f"\n3. 로봇 '{robot_id}'의 센서 데이터 조회:")
        sensor_data = db_client.get_sensor_data_by_robot(robot_id)
        print(f"총 {len(sensor_data)}개의 센서 데이터가 있습니다.")
        
        if sensor_data:
            # 센서 타입별로 그룹화
            sensor_types = {}
            for data in sensor_data:
                sensor_type = data['sensor_type']
                if sensor_type not in sensor_types:
                    sensor_types[sensor_type] = []
                sensor_types[sensor_type].append(data)
            
            for sensor_type, data_list in sensor_types.items():
                print(f"  {sensor_type}: {len(data_list)}개 데이터")
                if data_list:
                    latest = data_list[-1]
                    print(f"    최신 값: {latest['value']} {latest['unit']}")
    
    # 4. 알림 데이터 조회
    if robots:
        robot_id = robots[0]['robot_id']
        print(f"\n4. 로봇 '{robot_id}'의 알림 데이터 조회:")
        alerts = db_client.get_alerts_by_robot(robot_id)
        print(f"총 {len(alerts)}개의 알림이 있습니다.")
        
        if alerts:
            # 레벨별로 그룹화
            alert_levels = {}
            for alert in alerts:
                level = alert['level']
                if level not in alert_levels:
                    alert_levels[level] = []
                alert_levels[level].append(alert)
            
            for level, alert_list in alert_levels.items():
                print(f"  {level}: {len(alert_list)}개")
                if alert_list:
                    latest = alert_list[-1]
                    print(f"    최신 알림: {latest['message']}")
    
    # 5. 정비 기록 조회
    if robots:
        robot_id = robots[0]['robot_id']
        print(f"\n5. 로봇 '{robot_id}'의 정비 기록 조회:")
        maintenance = db_client.get_maintenance_by_robot(robot_id)
        print(f"총 {len(maintenance)}개의 정비 기록이 있습니다.")
        
        if maintenance:
            for record in maintenance:
                print(f"  - {record['maintenance_type']}: {record['description']}")
                print(f"    상태: {record['status']}, 기술자: {record['technician']}")
    
    # 6. 카메라 스트림 조회
    if robots:
        robot_id = robots[0]['robot_id']
        print(f"\n6. 로봇 '{robot_id}'의 카메라 스트림 조회:")
        streams = db_client.get_camera_streams_by_robot(robot_id)
        print(f"총 {len(streams)}개의 카메라 스트림이 있습니다.")
        
        for stream in streams:
            print(f"  - {stream['stream_type']} 스트림: {stream['stream_url']}")
            print(f"    품질: {stream['quality']}, 활성: {stream['is_active']}")
    
    # 7. 전체 데이터 통계
    print("\n7. 전체 데이터 통계:")
    all_robots = db_client.get_all_robots()
    all_sensor_data = db_client.scan('sensor_data')
    all_alerts = db_client.scan('alerts')
    all_maintenance = db_client.scan('maintenance')
    all_streams = db_client.scan('camera_streams')
    all_users = db_client.scan('users')
    
    print(f"  로봇: {len(all_robots)}개")
    print(f"  센서 데이터: {len(all_sensor_data)}개")
    print(f"  알림: {len(all_alerts)}개")
    print(f"  정비 기록: {len(all_maintenance)}개")
    print(f"  카메라 스트림: {len(all_streams)}개")
    print(f"  사용자: {len(all_users)}개")
    
    print("\n=== 더미 데이터 테스트 완료 ===")

if __name__ == "__main__":
    test_dummy_data()
