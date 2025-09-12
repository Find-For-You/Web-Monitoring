import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
from datetime import datetime
import logging
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DYNAMODB_TABLES
from .dummy import DummyDataGenerator

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamoDBClient:
    def __init__(self, use_dummy_data=False):
        """DynamoDB 클라이언트 초기화"""
        self.use_dummy_data = use_dummy_data
        
        if use_dummy_data:
            logger.info("더미 데이터 모드로 초기화")
            self.dummy_generator = DummyDataGenerator()
            self.dummy_data = self.dummy_generator.generate_all_dummy_data()
        else:
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
        if self.use_dummy_data:
            logger.info(f"더미 모드: 테이블 {table_name} 생성 요청 무시")
            return None
            
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
        if self.use_dummy_data:
            logger.info(f"더미 모드: {table_name}에 아이템 추가 요청 무시")
            return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            
        try:
            response = self.tables[table_name].put_item(Item=item)
            return response
        except ClientError as e:
            logger.error(f"아이템 추가 실패: {e}")
            raise

    def get_item(self, table_name, key):
        """아이템 조회"""
        if self.use_dummy_data:
            # 더미 데이터에서 해당 키로 아이템 찾기
            table_data = self.dummy_data.get(table_name, [])
            for item in table_data:
                if all(item.get(k) == v for k, v in key.items()):
                    return item
            return None
            
        try:
            response = self.tables[table_name].get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            logger.error(f"아이템 조회 실패: {e}")
            raise

    def query(self, table_name, key_condition_expression, filter_expression=None, **kwargs):
        """쿼리 실행"""
        if self.use_dummy_data:
            # 더미 데이터에서 간단한 필터링
            table_data = self.dummy_data.get(table_name, [])
            # 실제 쿼리 로직은 복잡하므로 전체 데이터 반환
            return table_data
            
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
        if self.use_dummy_data:
            # 더미 데이터에서 전체 스캔
            table_data = self.dummy_data.get(table_name, [])
            
            # 간단한 필터링 (실제 DynamoDB 필터와는 다름)
            if filter_expression:
                # 예: robot_id = 'robot_123'
                if 'robot_id' in filter_expression:
                    robot_id = filter_expression.split("'")[1]
                    table_data = [item for item in table_data if item.get('robot_id') == robot_id]
            
            return table_data
            
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
        if self.use_dummy_data:
            logger.info(f"더미 모드: {table_name} 아이템 업데이트 요청 무시")
            return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            
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
        if self.use_dummy_data:
            logger.info(f"더미 모드: {table_name} 아이템 삭제 요청 무시")
            return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            
        try:
            response = self.tables[table_name].delete_item(Key=key)
            return response
        except ClientError as e:
            logger.error(f"아이템 삭제 실패: {e}")
            raise

    def batch_write(self, table_name, items, operation='put'):
        """배치 쓰기 작업"""
        if self.use_dummy_data:
            logger.info(f"더미 모드: {table_name} 배치 {operation} 작업 요청 무시")
            return
            
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

    def get_all_robots(self):
        """모든 로봇 데이터 조회"""
        if self.use_dummy_data:
            return self.dummy_data.get('robots', [])
        return self.scan('robots')

    def get_robot_by_id(self, robot_id):
        """로봇 ID로 조회"""
        if self.use_dummy_data:
            robots = self.dummy_data.get('robots', [])
            for robot in robots:
                if robot.get('robot_id') == robot_id:
                    return robot
            return None
        return self.get_item('robots', {'robot_id': robot_id})

    def get_sensor_data_by_robot(self, robot_id, hours=24):
        """로봇의 센서 데이터 조회"""
        if self.use_dummy_data:
            sensor_data = self.dummy_data.get('sensor_data', [])
            return [data for data in sensor_data if data.get('robot_id') == robot_id]
        return self.scan('sensor_data', filter_expression=f"robot_id = '{robot_id}'")

    def get_alerts_by_robot(self, robot_id):
        """로봇의 알림 데이터 조회"""
        if self.use_dummy_data:
            alerts = self.dummy_data.get('alerts', [])
            return [alert for alert in alerts if alert.get('robot_id') == robot_id]
        return self.scan('alerts', filter_expression=f"robot_id = '{robot_id}'")

    def get_maintenance_by_robot(self, robot_id):
        """로봇의 정비 기록 조회"""
        if self.use_dummy_data:
            maintenance = self.dummy_data.get('maintenance', [])
            return [record for record in maintenance if record.get('robot_id') == robot_id]
        return self.scan('maintenance', filter_expression=f"robot_id = '{robot_id}'")

    def get_camera_streams_by_robot(self, robot_id):
        """로봇의 카메라 스트림 조회"""
        if self.use_dummy_data:
            streams = self.dummy_data.get('camera_streams', [])
            return [stream for stream in streams if stream.get('robot_id') == robot_id]
        return self.scan('camera_streams', filter_expression=f"robot_id = '{robot_id}'")

# 전역 DynamoDB 클라이언트 인스턴스 (더미 데이터 모드)
db_client = DynamoDBClient(use_dummy_data=True)
