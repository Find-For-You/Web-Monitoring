# 🤖 Web Monitoring System for Spider Robot

![project](https://img.shields.io/badge/Project-Spider%20Robot-blue.svg)
![license](https://img.shields.io/badge/License-MIT-green.svg)
![status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

이 레포지토리는 **AI 기반 지능형 6족보행 탐사로봇**의 **웹 기반 실시간 관제 시스템**을 개발하는 프로젝트입니다.  
로봇의 상태를 실시간으로 시각화하고, 수동 제어 및 경고 알림 기능을 포함한 **Streamlit 기반 대시보드**를 제공합니다.

본 프로젝트는 **2025년 ICT 한이음 드림업 캡스톤 프로젝트**의 일환으로 개발 중입니다.

---

## 🛠️ 현재까지 구현된 기능

- 로그인/회원가입 및 세션 기반 인증
- 실시간 센서 데이터 시각화 (온도, 습도, 기압 등)
- 로봇 실시간 상태 모니터링 및 제어 (수동 제어, 비상 정지)
- YOLO 탐지 결과 시각화 및 통계 분석
- 대시보드 자동 새로고침 (2~10초)
- 관리자 권한 기반 제어 (PID 조정, 사용자 관리)
- Streamlit 기반 다중 페이지 UI 구성

---

## 📁 프로젝트 구조

```

streamlit/
├── main.py                  # 메인 애플리케이션 (로그인/라우팅)
├── pages/
│   ├── 1\_홈.py              # 홈 (대시보드 개요)
│   ├── 2\_로봇관리.py        # 로봇 목록 및 실시간 제어
│   ├── 3\_지도.py            # 로봇 및 객체 위치 시각화
│   ├── 4\_분석리포트.py      # 환경 데이터 및 장애 분석
│   ├── 5\_설정.py            # 북마크, 알림, 사용자 정보 설정
│   └── 6\_관리자모드.py      # 관리자 전용 기능 (PID, 권한 등)
├── robot\_monitoring.db      # SQLite DB (향후 PostgreSQL 이관 예정)
├── requirements.txt         # Python 패키지 의존성 목록
└── README.md                # 프로젝트 설명 파일

````

---

## 🚀 실행 방법

```bash
# 가상환경 활성화 후
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run main.py
````

* 기본 관리자 계정

  * ID: `admin`
  * PW: `admin123`

---

## 📌 TODO (예정 기능)

* [ ] 대시보드 정보 확장 (배터리 상태, 위치, 장애 감지 등)
* [ ] 로봇 수동 조작 모드 UI/UX 개선
* [ ] 실시간 알림/경고 시스템 고도화 (배터리 부족, 장애 등)
* [ ] Firebase → PostgreSQL 마이그레이션
* [ ] WebSocket 기반 실시간 통신 구현
* [ ] AWS 기반 클라우드 아키텍처 설계 및 배포
* [ ] 실시간 카메라 영상 스트리밍 연동 (Kinesis Video 예정)
* [ ] 모바일 및 태블릿 대응 UI
* [ ] 다국어 지원 (영어/한국어)
* [ ] 보안 강화 (JWT, OAuth2.0 등)

---

## 🔧 기술 스택

| 구성 요소         | 기술                                                  |
| ------------- | --------------------------------------------------- |
| **Frontend**  | Streamlit + Plotly + Streamlit Community Components |
| **Backend**   | SQLite → PostgreSQL 예정, AWS Lambda / IoT Core 예정    |
| **Real-time** | `st_autorefresh`, WebSocket (예정)                    |
| **AI Module** | YOLOv5 / YOLOv8 (탐지 결과 시각화)                         |
| **System**    | psutil 기반 로컬 시스템 모니터링                               |
| **Auth**      | SHA256 비밀번호 해싱 + 세션 기반 인증 + 역할 기반 접근 제어(RBAC)       |

---

## 🗄️ 데이터베이스 스키마 (주요 테이블)

* `users`: 사용자 계정 정보 및 권한
* `robots`: 로봇 메타데이터 및 상태 정보
* `sensor_data`: 센서별 시계열 데이터 저장
* `detection_result`: YOLO 탐지 클래스 및 바운딩 박스
* `command_history`: 로봇 제어 명령 이력
* `robot_status_history`: 배터리, 속도, 방향 등 상태 이력
* `bookmarks`: 사용자가 설정한 위치 북마크
* `notification_settings`: 사용자별 알림 수신 설정
* `pid_parameters`: 로봇 PID 제어 파라미터

---

## 🔐 보안 기능

* 비밀번호 해싱 (SHA-256)
* 세션 기반 로그인 인증
* 관리자/사용자 역할 기반 페이지 접근 제어
* 관리자 모드 내 권한 제어 기능 포함

---

## 🛰️ AWS 통합 계획 (예정)

| 기능             | AWS 서비스                                       |
| -------------- | --------------------------------------------- |
| 사용자 인증         | Amazon Cognito                                |
| 로봇 ↔ 서버 실시간 통신 | AWS IoT Core (MQTT) / API Gateway (WebSocket) |
| 센서 시계열 데이터 저장  | Amazon Timestream                             |
| YOLO 결과/이력 저장  | DynamoDB or Aurora                            |
| 실시간 카메라 스트리밍   | Kinesis Video Streams                         |
| 알림 시스템         | Amazon SNS                                    |
| 리포트 생성 및 다운로드  | AWS Lambda + S3 + API Gateway                 |
| 로그 및 모니터링      | Amazon CloudWatch + X-Ray                     |

---

## 📬 연락처

* ✉️ 학교 이메일: [2020144005@tukorea.ac.kr](mailto:2020144005@tukorea.ac.kr)
* ✉️ 개인 이메일: [chrisabc94@gmail.com](mailto:chrisabc94@gmail.com)

---

## 🔓 라이선스

본 프로젝트는 [MIT License](LICENSE)를 따릅니다. 자유롭게 사용, 수정, 배포하실 수 있습니다.

---

> 본 시스템은 **실시간 탐사 로봇 운영 상태를 시각화 및 제어**할 수 있도록 설계되었으며,
> **긴급 상황에 대한 즉각적 대응과 장애 예방**을 목표로 합니다.

```