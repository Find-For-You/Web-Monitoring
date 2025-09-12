# DynamoDB 설정 가이드

이 가이드는 ERD를 DynamoDB로 마이그레이션하는 과정을 단계별로 설명합니다.

## 1. AWS 계정 설정

### 1.1 AWS 계정 생성
1. [AWS 콘솔](https://aws.amazon.com/console/)에 접속
2. 새 계정 생성 또는 기존 계정 로그인
3. 결제 정보 입력 (DynamoDB는 사용량 기반 과금)

### 1.2 IAM 사용자 생성
1. AWS 콘솔에서 IAM 서비스로 이동
2. "사용자" → "사용자 추가" 클릭
3. 사용자 이름: `robot-monitoring-user`
4. 액세스 유형: "프로그래밍 방식 액세스" 선택
5. 권한: "기존 정책 직접 연결" → `AmazonDynamoDBFullAccess` 선택
6. 사용자 생성 후 Access Key ID와 Secret Access Key 저장

## 2. DynamoDB 테이블 생성

### 2.1 테이블 생성 스크립트 실행
```bash
cd streamlit
python dynamodb_schema.py
```

### 2.2 수동 테이블 생성 (AWS 콘솔)
1. AWS 콘솔에서 DynamoDB 서비스로 이동
2. "테이블 생성" 클릭
3. 테이블 이름: `RobotMonitoring`
4. 파티션 키: `PK` (문자열)
5. 정렬 키: `SK` (문자열)
6. 설정: 온디맨드 또는 프로비저닝된 용량 선택

## 3. 환경 설정

### 3.1 AWS 자격 증명 설정

#### 방법 1: AWS CLI 사용 (권장)
```bash
aws configure
```
- AWS Access Key ID: [입력]
- AWS Secret Access Key: [입력]
- Default region name: ap-northeast-2
- Default output format: json

#### 방법 2: 환경 변수 설정
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-northeast-2
```

#### 방법 3: Streamlit 앱에서 직접 설정
- `main_dynamodb.py` 실행 후 AWS 설정 탭에서 입력

### 3.2 Python 의존성 설치
```bash
pip install -r requirements.txt
```

## 4. 데이터 마이그레이션

### 4.1 기존 SQLite 데이터 백업
```bash
cp robot_monitoring.db robot_monitoring_backup.db
```

### 4.2 DynamoDB로 데이터 마이그레이션
```bash
python migrate_to_dynamodb.py
```

## 5. 애플리케이션 실행

### 5.1 DynamoDB 버전 실행
```bash
streamlit run main_dynamodb.py
```

### 5.2 기존 SQLite 버전과 비교
```bash
# SQLite 버전
streamlit run main.py

# DynamoDB 버전
streamlit run main_dynamodb.py
```

## 6. DynamoDB 스키마 구조

### 6.1 테이블 설계
- **메인 테이블**: `RobotMonitoring`
- **파티션 키 (PK)**: `{ENTITY_TYPE}#{ENTITY_ID}`
- **정렬 키 (SK)**: `{ENTITY_TYPE}#{ENTITY_ID}` 또는 관계 정보
- **GSI1**: 사용자별 데이터 조회
- **GSI2**: 프로젝트별 데이터 조회  
- **GSI3**: 로봇별 데이터 조회

### 6.2 엔티티 타입
- `USER#`: 사용자 정보
- `TEAM#`: 팀 정보
- `PROJECT#`: 프로젝트 정보
- `ROBOT#`: 로봇 정보
- `CAMERA#`: 카메라 정보
- `DETECTION#`: 감지 결과
- `SENSOR#`: 센서 데이터
- `REPORT#`: 보고서
- `COMMAND#`: 명령 히스토리
- `STATUS#`: 로봇 상태 히스토리

## 7. 주요 차이점

### 7.1 SQLite vs DynamoDB
| 기능 | SQLite | DynamoDB |
|------|--------|----------|
| 데이터베이스 타입 | 관계형 | NoSQL |
| 스키마 | 고정 | 유연 |
| 쿼리 | SQL | API 기반 |
| 확장성 | 제한적 | 무제한 |
| 비용 | 무료 | 사용량 기반 |
| 백업 | 수동 | 자동 |

### 7.2 쿼리 패턴 변경
```python
# SQLite (기존)
cursor.execute("SELECT * FROM users WHERE user_email = ?", (email,))

# DynamoDB (신규)
response = table.scan(
    FilterExpression=Attr('user_email').eq(email) & Attr('entity_type').eq('USER')
)
```

## 8. 비용 최적화

### 8.1 온디맨드 vs 프로비저닝
- **온디맨드**: 사용량에 따라 자동 조정, 예측하기 어려운 워크로드에 적합
- **프로비저닝**: 미리 용량을 설정, 예측 가능한 워크로드에 적합

### 8.2 비용 모니터링
1. AWS 콘솔 → DynamoDB → 테이블 → 모니터링
2. CloudWatch에서 비용 알림 설정
3. 예상 비용 계산기 사용

## 9. 문제 해결

### 9.1 일반적인 오류
- **NoCredentialsError**: AWS 자격 증명이 설정되지 않음
- **ResourceNotFoundException**: DynamoDB 테이블이 존재하지 않음
- **ValidationException**: 잘못된 파라미터 전달

### 9.2 디버깅 팁
1. AWS CloudTrail에서 API 호출 로그 확인
2. DynamoDB 콘솔에서 테이블 상태 확인
3. Python 코드에 try-catch 블록 추가

## 10. 보안 고려사항

### 10.1 IAM 권한 최소화
- 필요한 DynamoDB 작업만 허용
- 읽기 전용 사용자는 별도 생성

### 10.2 데이터 암호화
- DynamoDB는 기본적으로 암호화됨
- 민감한 데이터는 애플리케이션 레벨에서 추가 암호화

### 10.3 네트워크 보안
- VPC 엔드포인트 사용 고려
- IP 화이트리스트 설정

## 11. 모니터링 및 알림

### 11.1 CloudWatch 메트릭
- 읽기/쓰기 용량 사용률
- 에러율
- 지연 시간

### 11.2 알림 설정
- 용량 사용률 80% 초과시 알림
- 에러율 증가시 알림
- 비용 한도 초과시 알림

이 가이드를 따라하면 ERD를 DynamoDB로 성공적으로 마이그레이션할 수 있습니다.
