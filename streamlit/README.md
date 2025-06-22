# Production System TeamProject
2025년 1학기 생산시스템 구축실무 과목의 팀 프로젝트에 대한 레포지토리입니다.

이 레포지토리는 열풍건조 공정의 이상을 실시간으로 감지하고 모니터링하는 **Streamlit 기반의 지능형 생산시스템 대시보드**입니다.

개발용 레포지토리는 [여기](https://github.com/Nekerworld/Production_System_TeamProject)를 클릭해주세요.

## ✨ 주요 특징 및 기능

이 프로젝트는 열풍건조 공정 데이터를 기반으로 한 딥러닝 품질 예측 모델을 구현하며, 아래와 같은 장점이 있습니다.

*   **직관적인 대시보드**: Streamlit을 활용하여 사용자가 공정 상태와 이상 징후를 한눈에 파악할 수 있는 시각적인 대시보드 제공
*   **스크롤 반응형 소개 페이지**: 스크롤에 반응하는 다이나믹한 프로젝트 소개 페이지를 통해 시스템의 핵심 가치를 효과적으로 전달
*   **AI 기반 이상 감지**: 온도와 전류 데이터를 딥러닝 모델(LSTM)이 분석하여 실시간으로 비정상 패턴 탐지
*   **예지 보전 지원**: 고장 전 미세한 징후를 포착하여 선제적인 유지보수 계획 수립을 도움
*   **확장성 있는 모듈 구조**: 각 기능이 독립적인 페이지로 구성되어 있어 유지보수 및 기능 확장 용이

### [데이터 링크 (Kamp AI)](https://www.kamp-ai.kr/aidataDetail?page=1&DATASET_SEQ=23)

## 📊 데이터 소개 (Dataset Overview)

| 항목     | 내용                                                    |
| ------ | ----------------------------------------------------- |
| 데이터셋 명 | 장비이상 조기탐지 AI 데이터셋                                     |
| 적용 공정  | 열풍건조(Baking·Heat‐Dry)                                 |
| 제공 기관  | KAIST (수행: ㈜에이비에이치, ㈜임픽스)                             |
| 목적     | 설비 예지보전 및 이상 탐지                                       |
| 등록·수정일 | 2021-12-27 등록, 2025-04-02 최종 수정                       |
| 데이터 크기 | 307 083 개의 데이터 포인트, 실제 데이터의 개수는 CSV가 51,084, WAV가 183개, 총 1.8 GB                                 |

이 데이터에는 CSV, WAV 파일 형태의 데이터가 있습니다.

아래는 최종발표자료의 일부입니다.

![image](https://github.com/user-attachments/assets/2d49e857-427e-4ecb-9956-f132c9a356bd)
![image](https://github.com/user-attachments/assets/022c1680-2e64-4f60-be73-5e0e16a0ee0f)
![image](https://github.com/user-attachments/assets/b37d5bec-c5f0-4dd3-80c0-d8f6d0f9d856)
![image](https://github.com/user-attachments/assets/f6bb1cd8-bbbd-4a44-b9b8-2e6f7fed1607)

Process 컬럼은 어떠한 공정에서 측정된 데이터인지 나타내는 컬럼으로, 예를 들자면 1번은 배추 건조 공정, 2번은 웨이퍼 건조 공정.... 과 같은 식입니다.

---

### 수집 방법과 형태

* 열풍건조 장비에 설치된 센서로부터 온도, 전압, 시간 등 실시간 데이터를 수신하여 CSV 파일로 저장
* 열풍건조 공정 팬에 부착된 사운드 센서로 음성 신호를 수집해 WAV 파일로 저장
* 최종 데이터셋은 데이터 CSV 33종, Error Lot List, WAV 183종으로 구성

### 주요 특징

* 센서·사운드 데이터의 이중 입력 구조로 설비 상태를 다각도로 파악
* 48개 이상의 공정 변수를 포함해 모델 학습에 충분한 피처를 제공

---

### 📌 사용된 Python 환경

* **Python 버전**: `3.12.3`
* **가상환경 추천**: `venv` 또는 `conda` 환경 사용 권장

---

### 📦 주요 패키지 및 라이브러리

| 라이브러리                   | 버전             | 용도                   |
| ----------------------- | -------------- | -------------------- |
| `tensorflow`            | 2.18.0         | DNN 모델 구축 및 학습       |
| `keras`                 | 3.6.0          | 딥러닝 전처리 유틸           |
| `numpy`                 | 1.26.4         | 수치 연산                |
| `pandas`                | 2.1.4          | 데이터프레임 처리            |
| `scikit-learn`          | 1.4.2          | 전처리, 모델 평가 등         |
| `scipy`                 | 1.11.4         | 수학/통계 기반 함수          |
| `matplotlib`            | 3.7.5          | 시각화                  |
| `seaborn`               | 0.13.2         | 시각화                  |
| `imbalanced-learn`      | 0.12.3         | 클래스 불균형 처리 (SMOTE 등) |
| `xgboost`               | 4.6.0          | 비교용 머신러닝 모델          |
| `streamlit`             | 1.37.1         | 웹 대시보드 구축            |
| `plotly`                | 5.24.1         | 인터랙티브 시각화           |
| `joblib`                | 1.3.2          | 모델 직렬화/역직렬화         |
| `h5py`                  | 3.11.0         | HDF5 파일 입출력            |
| `protobuf`              | 3.20.3         | 데이터 직렬화             |

추가적으로 `tensorboard`, `graphviz` 등도 함께 사용되었습니다.

---

### 개발된 대시보드 사진
![KakaoTalk_20250618_181714194](https://github.com/user-attachments/assets/84024c4c-bdaa-4050-b944-d4970bde1422)
![KakaoTalk_20250618_181721557](https://github.com/user-attachments/assets/4100a256-3b6b-4572-a800-05a01eae65cd)
![KakaoTalk_20250618_181732989](https://github.com/user-attachments/assets/51a21db6-0041-44df-9b07-8e328af8b002)
![KakaoTalk_20250618_181746214](https://github.com/user-attachments/assets/0bc40f74-23ab-41ce-8de8-e1b5a6defc7a)
![KakaoTalk_20250618_181757490](https://github.com/user-attachments/assets/5790fe47-4c1d-46f8-a674-3bf0bd899f18)

---

### 🚀 실행 방법

이 레포지토리를 클론한 후, 해당 폴더에서 터미널/명령 프롬프트를 열고 아래의 명령어를 입력해주세요.

1.  **레포지토리 클론**:
    ```bash
    git clone https://github.com/Nekerworld/Production-System-Public.git
    ```
2.  **필요한 패키지 설치**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Streamlit 애플리케이션 실행**:
    ```bash
    streamlit run main.py
    ```
