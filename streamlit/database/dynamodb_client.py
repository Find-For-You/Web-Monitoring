import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
from datetime import datetime
import logging
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DYNAMODB_TABLES

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamoDBClient:
    def __init__(self):
        """DynamoDB 클라이언트 초기화"""
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            self.tables = {}
            self._initialize_tables()
        except Exception as e:
            logger.error(f"DynamoDB 클라이언트 초기화 실패: {e}")
            raise

    def _initialize_tables(self):
        """테이블 객체 초기화"""
        for table_name, table_id in DYNAMODB_TABLES.items():
            try:
                self.tables[table_name] = self.dynamodb.Table(table_id)
            except ClientError as e:
                logger.warning(f"테이블 {table_id} 접근 실패: {e}")

    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput=None):
        """테이블 생성"""
        try:
            table_params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions
            }
            
            if provisioned_throughput:
                table_params['ProvisionedThroughput'] = provisioned_throughput
            else:
                table_params['BillingMode'] = 'PAY_PER_REQUEST'
            
            table = self.dynamodb.create_table(**table_params)
            table.wait_until_exists()
            logger.info(f"테이블 {table_name} 생성 완료")
            return table
        except ClientError as e:
            logger.error(f"테이블 생성 실패: {e}")
            raise

    def put_item(self, table_name, item):
        """아이템 추가/업데이트"""
        try:
            response = self.tables[table_name].put_item(Item=item)
            return response
        except ClientError as e:
            logger.error(f"아이템 추가 실패: {e}")
            raise

    def get_item(self, table_name, key):
        """아이템 조회"""
        try:
            response = self.tables[table_name].get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            logger.error(f"아이템 조회 실패: {e}")
            raise

    def query(self, table_name, key_condition_expression, filter_expression=None, **kwargs):
        """쿼리 실행"""
        try:
            query_params = {
                'KeyConditionExpression': key_condition_expression,
                **kwargs
            }
            
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            
            response = self.tables[table_name].query(**query_params)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"쿼리 실행 실패: {e}")
            raise

    def scan(self, table_name, filter_expression=None, **kwargs):
        """스캔 실행"""
        try:
            scan_params = kwargs
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            
            response = self.tables[table_name].scan(**scan_params)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"스캔 실행 실패: {e}")
            raise

    def update_item(self, table_name, key, update_expression, expression_attribute_values=None):
        """아이템 업데이트"""
        try:
            update_params = {
                'Key': key,
                'UpdateExpression': update_expression
            }
            
            if expression_attribute_values:
                update_params['ExpressionAttributeValues'] = expression_attribute_values
            
            response = self.tables[table_name].update_item(**update_params)
            return response
        except ClientError as e:
            logger.error(f"아이템 업데이트 실패: {e}")
            raise

    def delete_item(self, table_name, key):
        """아이템 삭제"""
        try:
            response = self.tables[table_name].delete_item(Key=key)
            return response
        except ClientError as e:
            logger.error(f"아이템 삭제 실패: {e}")
            raise

    def batch_write(self, table_name, items, operation='put'):
        """배치 쓰기 작업"""
        try:
            with self.tables[table_name].batch_writer() as batch:
                for item in items:
                    if operation == 'put':
                        batch.put_item(Item=item)
                    elif operation == 'delete':
                        batch.delete_item(Key=item)
            logger.info(f"배치 {operation} 작업 완료: {len(items)}개 아이템")
        except ClientError as e:
            logger.error(f"배치 쓰기 실패: {e}")
            raise

# 전역 DynamoDB 클라이언트 인스턴스
db_client = DynamoDBClient()
