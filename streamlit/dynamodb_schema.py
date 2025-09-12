"""
DynamoDB 스키마 설계 및 테이블 생성 스크립트
ERD를 DynamoDB NoSQL 구조로 변환
"""

import boto3
from botocore.exceptions import ClientError
import json
from typing import Dict, Any, List

class DynamoDBSchema:
    def __init__(self, region_name: str = 'ap-northeast-2'):
        """DynamoDB 클라이언트 초기화"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.table_name = 'RobotMonitoring'
    
    def create_table(self):
        """메인 DynamoDB 테이블 생성"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'PK',
                        'KeyType': 'HASH'  # Partition Key
                    },
                    {
                        'AttributeName': 'SK',
                        'KeyType': 'RANGE'  # Sort Key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI1PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI1SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI2PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI2SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI3PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI3SK',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'GSI1',
                        'KeySchema': [
                            {
                                'AttributeName': 'GSI1PK',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'GSI1SK',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    },
                    {
                        'IndexName': 'GSI2',
                        'KeySchema': [
                            {
                                'AttributeName': 'GSI2PK',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'GSI2SK',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    },
                    {
                        'IndexName': 'GSI3',
                        'KeySchema': [
                            {
                                'AttributeName': 'GSI3PK',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'GSI3SK',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            
            # 테이블이 생성될 때까지 대기
            table.wait_until_exists()
            print(f"테이블 '{self.table_name}'이 성공적으로 생성되었습니다.")
            return table
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"테이블 '{self.table_name}'이 이미 존재합니다.")
                return self.dynamodb.Table(self.table_name)
            else:
                print(f"테이블 생성 중 오류 발생: {e}")
                raise

    def get_entity_keys(self, entity_type: str, entity_id: str, related_entity: str = None, related_id: str = None) -> Dict[str, str]:
        """
        엔티티 타입에 따른 DynamoDB 키 생성
        
        Args:
            entity_type: 엔티티 타입 (USER, TEAM, PROJECT, ROBOT, CAMERA, etc.)
            entity_id: 엔티티 ID
            related_entity: 관련 엔티티 타입 (선택사항)
            related_id: 관련 엔티티 ID (선택사항)
        
        Returns:
            DynamoDB 키 딕셔너리
        """
        keys = {
            'PK': f"{entity_type}#{entity_id}",
            'SK': f"{entity_type}#{entity_id}"
        }
        
        # GSI 키 설정 (엔티티 타입에 따라)
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
            keys['GSI3PK'] = f"ROBOT#{related_id}"  # 로봇에 속한 카메라
            keys['GSI3SK'] = f"CAMERA#{entity_id}"
        elif entity_type == 'DETECTION_RESULT':
            keys['GSI3PK'] = f"CAMERA#{related_id}"  # 카메라에 속한 감지 결과
            keys['GSI3SK'] = f"DETECTION#{entity_id}"
        elif entity_type == 'SENSOR_DATA':
            keys['GSI3PK'] = f"ROBOT#{related_id}"  # 로봇에 속한 센서 데이터
            keys['GSI3SK'] = f"SENSOR#{entity_id}"
        elif entity_type == 'REPORT':
            keys['GSI2PK'] = f"PROJECT#{related_id}"  # 프로젝트에 속한 보고서
            keys['GSI2SK'] = f"REPORT#{entity_id}"
        elif entity_type == 'COMMAND_HISTORY':
            keys['GSI3PK'] = f"ROBOT#{related_id}"  # 로봇에 속한 명령 히스토리
            keys['GSI3SK'] = f"COMMAND#{entity_id}"
        elif entity_type == 'ROBOT_STATUS_HISTORY':
            keys['GSI3PK'] = f"ROBOT#{related_id}"  # 로봇에 속한 상태 히스토리
            keys['GSI3SK'] = f"STATUS#{entity_id}"
        elif entity_type == 'TEAM_MEMBER':
            keys['GSI1PK'] = f"TEAM#{related_id}"  # 팀에 속한 멤버
            keys['GSI1SK'] = f"USER#{entity_id}"
        
        return keys

    def create_sample_data(self):
        """샘플 데이터 생성"""
        table = self.dynamodb.Table(self.table_name)
        
        # 샘플 사용자 데이터
        sample_users = [
            {
                'user_id': '1',
                'first_name': '관리자',
                'last_name': '시스템',
                'user_email': 'admin@robot.com',
                'user_password': 'hashed_password_here',
                'user_role': 'Admin',
                'created_at': '2024-01-01T00:00:00Z'
            },
            {
                'user_id': '2',
                'first_name': '김',
                'last_name': '로봇',
                'user_email': 'kim@robot.com',
                'user_password': 'hashed_password_here',
                'user_role': 'User',
                'created_at': '2024-01-02T00:00:00Z'
            }
        ]
        
        for user in sample_users:
            keys = self.get_entity_keys('USER', user['user_id'])
            item = {**keys, **user, 'entity_type': 'USER'}
            table.put_item(Item=item)
        
        # 샘플 팀 데이터
        sample_teams = [
            {
                'team_id': '1',
                'user_id': '1',  # 팀 설립자
                'team_name': '로봇개발팀',
                'team_description': '로봇 개발 및 관리 담당',
                'team_created_at': '2024-01-01T00:00:00Z'
            }
        ]
        
        for team in sample_teams:
            keys = self.get_entity_keys('TEAM', team['team_id'])
            item = {**keys, **team, 'entity_type': 'TEAM'}
            table.put_item(Item=item)
        
        # 샘플 프로젝트 데이터
        sample_projects = [
            {
                'project_id': '1',
                'user_id': '1',
                'team_id': '1',
                'project_name': '로봇 모니터링 프로젝트',
                'project_description': '로봇 상태 모니터링 및 제어 시스템',
                'project_visibility': True,
                'project_status': 'Active',
                'project_start_date': '2024-01-01T00:00:00Z',
                'project_created_at': '2024-01-01T00:00:00Z'
            }
        ]
        
        for project in sample_projects:
            keys = self.get_entity_keys('PROJECT', project['project_id'])
            item = {**keys, **project, 'entity_type': 'PROJECT'}
            table.put_item(Item=item)
        
        # 샘플 로봇 데이터
        sample_robots = [
            {
                'robot_id': '1',
                'project_id': '1',
                'robot_name': 'Robot-01',
                'robot_battery': 85,
                'robot_connection': 95,
                'robot_ping': 12,
                'robot_status': 'Online',
                'robot_location_x': 10.5,
                'robot_location_y': 20.3,
                'robot_created_at': '2024-01-01T00:00:00Z'
            },
            {
                'robot_id': '2',
                'project_id': '1',
                'robot_name': 'Robot-02',
                'robot_battery': 72,
                'robot_connection': 88,
                'robot_ping': 15,
                'robot_status': 'Online',
                'robot_location_x': 15.2,
                'robot_location_y': 25.7,
                'robot_created_at': '2024-01-01T00:00:00Z'
            }
        ]
        
        for robot in sample_robots:
            keys = self.get_entity_keys('ROBOT', robot['robot_id'])
            item = {**keys, **robot, 'entity_type': 'ROBOT'}
            table.put_item(Item=item)
        
        print("샘플 데이터가 성공적으로 생성되었습니다.")

# 사용 예시
if __name__ == "__main__":
    schema = DynamoDBSchema()
    
    # 테이블 생성
    table = schema.create_table()
    
    # 샘플 데이터 생성
    schema.create_sample_data()
