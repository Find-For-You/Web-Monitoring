"""
AWS 설정 및 인증 관리
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional

class AWSConfig:
    def __init__(self):
        """AWS 설정 초기화"""
        self.region_name = 'ap-northeast-2'  # 서울 리전
        self.table_name = 'RobotMonitoring'
        
    def setup_credentials(self, access_key: str = None, secret_key: str = None, region: str = None):
        """AWS 자격 증명 설정"""
        if access_key and secret_key:
            os.environ['AWS_ACCESS_KEY_ID'] = access_key
            os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        
        if region:
            self.region_name = region
            
        os.environ['AWS_DEFAULT_REGION'] = self.region_name
    
    def get_dynamodb_client(self):
        """DynamoDB 클라이언트 반환"""
        try:
            return boto3.client('dynamodb', region_name=self.region_name)
        except NoCredentialsError:
            raise Exception("AWS 자격 증명이 설정되지 않았습니다. AWS CLI를 설정하거나 자격 증명을 직접 입력해주세요.")
    
    def get_dynamodb_resource(self):
        """DynamoDB 리소스 반환"""
        try:
            return boto3.resource('dynamodb', region_name=self.region_name)
        except NoCredentialsError:
            raise Exception("AWS 자격 증명이 설정되지 않았습니다. AWS CLI를 설정하거나 자격 증명을 직접 입력해주세요.")
    
    def test_connection(self) -> bool:
        """AWS 연결 테스트"""
        try:
            client = self.get_dynamodb_client()
            client.list_tables()
            return True
        except Exception as e:
            print(f"AWS 연결 테스트 실패: {e}")
            return False

# 전역 AWS 설정 인스턴스
aws_config = AWSConfig()
