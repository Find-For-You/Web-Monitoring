# AI 지능형 정보 탐색 로봇 모니터링 시스템

## 📋 프로젝트 개요

이 시스템은 AI 지능형 정보 탐색 로봇을 위한 종합 모니터링 플랫폼입니다. AWS DynamoDB를 기반으로 하며, 실시간 로봇 상태 모니터링, 위치 추적, 센서 데이터 분석, 카메라 스트림 관리 등의 기능을 제공합니다.

## 🚀 주요 기능

### 🤖 로봇 관리
- 실시간 로봇 상태 모니터링
- 로봇 등록 및 설정 관리
- 배터리 및 건강도 추적
- 위치 정보 실시간 업데이트

### 📊 데이터 분석
- 센서 데이터 수집 및 분석
- 성능 지표 대시보드
- 알림 및 경고 시스템
- 종합 분석 리포트 생성

### 🗺️ 위치 추적
- 실시간 지도 기반 위치 표시
- 이동 경로 추적
- 위치 통계 및 분석

### 📹 카메라 스트림
- HTTPS 기반 실시간 스트리밍
- 다중 품질 설정 지원
- 스트림 상태 모니터링

### ⚙️ 시스템 관리
- 사용자 권한 관리
- 시스템 설정 및 구성
- 데이터 백업 및 복구
- 보안 설정

## 🏗️ 시스템 아키텍처

### 데이터베이스 구조 (DynamoDB)
- **Users**: 사용자 정보 및 권한
- **Robots**: 로봇 기본 정보 및 상태
- **Sensor_Data**: 센서 데이터 수집
- **Alerts**: 알림 및 경고 관리
- **Locations**: 위치 정보 히스토리
- **Maintenance**: 정비 기록 관리
- **Camera_Streams**: 카메라 스트림 설정

### 기술 스택
- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: AWS DynamoDB
- **Streaming**: HTTPS/RTSP
- **Visualization**: Plotly, Folium
- **Authentication**: Session-based

## 📦 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd streamlit

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# env_example.txt를 .env로 복사하고 설정
cp env_example.txt .env

# .env 파일 편집
# AWS 자격 증명 및 기타 설정 입력
```

### 3. AWS 설정
- AWS 계정 생성
- DynamoDB 테이블 생성
- IAM 사용자 생성 및 권한 설정
- 환경 변수에 AWS 자격 증명 입력

### 4. 애플리케이션 실행
```bash
# 메인 애플리케이션 실행
streamlit run main.py

# 또는 특정 페이지 실행
streamlit run pages/1_홈.py
```

## 🔧 설정 가이드

### DynamoDB 테이블 생성
각 테이블은 다음과 같은 키 구조를 가집니다:

```python
# Users 테이블
{
    'user_id': 'string',  # Partition Key
    'username': 'string',
    'email': 'string',
    'role': 'string',
    'created_at': 'string'
}

# Robots 테이블
{
    'robot_id': 'string',  # Partition Key
    'name': 'string',
    'model': 'string',
    'status': 'string',
    'battery_level': 'number',
    'location': 'map',
    'created_at': 'string',
    'updated_at': 'string'
}

# Sensor_Data 테이블
{
    'sensor_id': 'string',  # Partition Key
    'robot_id': 'string',   # Sort Key
    'sensor_type': 'string',
    'value': 'number',
    'unit': 'string',
    'timestamp': 'string'
}

# Alerts 테이블
{
    'alert_id': 'string',  # Partition Key
    'robot_id': 'string',  # Sort Key
    'level': 'string',
    'message': 'string',
    'timestamp': 'string',
    'resolved': 'boolean'
}
```

### 카메라 스트림 설정
```python
# 스트림 URL 형식
RTSP: rtsp://[IP]:8554/stream/[robot_id]
HTTP: http://[IP]:8080/stream/[robot_id]
HTTPS: https://[domain]:443/stream/[robot_id]
```

## 👥 사용자 가이드

### 로그인
- **관리자 계정**: admin / admin123
- **운영자 계정**: operator / operator123

### 페이지별 기능

#### 🏠 홈
- 전체 시스템 개요
- 실시간 통계
- 최근 활동 모니터링

#### 🔧 로봇 관리
- 로봇 목록 및 상태 확인
- 새 로봇 등록
- 상세 모니터링
- 설정 관리

#### 🗺️ 지도
- 실시간 위치 추적
- 위치 통계 분석
- 이동 경로 시각화

#### 📊 분석 리포트
- 성능 분석
- 알림 분석
- 배터리 분석
- 종합 리포트

#### ⚙️ 설정
- 일반 설정
- 알림 설정
- 스트림 설정
- 보안 설정

#### 👨‍💼 관리자 모드
- 시스템 모니터링
- 사용자 관리
- 데이터 관리
- 시스템 설정

## 🔒 보안 고려사항

### 인증 및 권한
- 세션 기반 인증
- 역할별 권한 관리
- 세션 타임아웃 설정

### 데이터 보안
- HTTPS 통신
- 데이터 암호화
- 접근 로그 기록

### 시스템 보안
- IP 화이트리스트
- 시간 제한 접근
- 보안 헤더 설정

## 📈 성능 최적화

### 데이터베이스 최적화
- DynamoDB 인덱스 활용
- 배치 작업 사용
- 데이터 압축

### 스트리밍 최적화
- 품질 자동 조정
- 캐싱 활용
- 대역폭 관리

### 애플리케이션 최적화
- 비동기 처리
- 메모리 관리
- 로그 정리

## 🐛 문제 해결

### 일반적인 문제

#### DynamoDB 연결 오류
```bash
# AWS 자격 증명 확인
aws configure list

# 환경 변수 확인
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

#### 스트림 연결 실패
```bash
# 포트 확인
netstat -an | grep 8554
netstat -an | grep 8080

# 방화벽 설정 확인
sudo ufw status
```

#### 메모리 부족
```bash
# 로그 파일 크기 확인
du -sh logs/

# 오래된 로그 정리
find logs/ -name "*.log" -mtime +7 -delete
```

## 📞 지원 및 문의

### 개발팀 연락처
- **이메일**: support@robotmonitoring.com
- **문서**: [Wiki 링크]
- **이슈 트래커**: [GitHub Issues]

### 버그 리포트
버그를 발견하셨다면 다음 정보와 함께 리포트해주세요:
- 발생 시간
- 사용 중인 페이지
- 오류 메시지
- 브라우저 정보
- 시스템 정보

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🔄 업데이트 로그

### v1.0.0 (2024-01-15)
- 초기 버전 릴리스
- 기본 모니터링 기능 구현
- DynamoDB 연동
- 실시간 스트리밍 지원

---

**© 2025 AI 지능형 정보 탐색 로봇 모니터링 시스템. All rights reserved.**
