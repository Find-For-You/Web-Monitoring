import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="탐사로봇 대시보드",
    page_icon="🏭",
    layout="wide"
)

with st.sidebar:
    st.header("Find For You")
    st.markdown("---")

# --- 1. 히어로 섹션 ---
with st.container():
    st.markdown("""
    <style>
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css");
    @import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css");

    * {
        font-family: Pretendard;
        padding: 0;
        margin: 0;
    }

    .section {
        width: 100%;
        height: 100vh;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .section1 {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                    url('https://i.imgur.com/wVwCjnr.jpeg') no-repeat;
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    .section2 {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                    url('https://i.imgur.com/cW4y4s3.jpeg') no-repeat;
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    .section3 {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                    url('https://i.imgur.com/iUenTpM.jpeg') no-repeat;
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    .section4 {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                    url('https://i.imgur.com/c5tnILg.jpeg') no-repeat;
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    .section5 {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                    url('https://i.imgur.com/OHGBO4C.jpeg') no-repeat;
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    .section6 {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                    url('https://i.imgur.com/bcps4wK.jpeg') no-repeat;
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    .section-content {
        color: white;
        padding: 3rem 4rem;
        background: rgba(30, 57, 30, 0.75);
        border-radius: 15px;
        max-width: 1000px;
        position: relative;
        z-index: 1;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }

    .section-content:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px 0 rgba(0, 0, 0, 0.45);
    }

    .hero-title {
        font-size: 5em;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5em;
        line-height: 1.1;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .hero-subtitle {
        font-size: 1.8em;
        text-align: center;
        color: white;
        margin-bottom: 1em;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }

    .section-header {
        font-size: 2.8em;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1em;
        color: white;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }

    .section-text {
        font-size: 1.2em;
        line-height: 1.6;
        text-align: center;
        margin-bottom: 2em;
        color: white;
    }

    .feature-point {
        font-size: 1.1em;
        line-height: 1.5;
        padding: 0.8em 0;
        color: white;
    }

    .contact-info {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 2em;
    }

    .contact-item {
        display: flex;
        align-items: center;
        margin: 0 1em;
    }

    .contact-item i {
        margin-right: 0.5em;
    }

    .contact-item a {
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # 첫 번째 섹션
    st.markdown("""
    <div class='section section1'>
        <div class='section-content'>
            <h1 class='hero-title'>AI 험지탐사 로봇 시스템</h1>
            <p class='hero-subtitle'>극한 환경에서 자율적으로 정보를 수집하고<br>지형과 장애물을 인식하여 구조 및 정찰 임무를 수행하는 AI 로봇 시스템입니다.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 두 번째 섹션
    st.markdown("""
    <div class='section section2'>
        <div class='section-content'>
            <h2 class='section-header'>험지에 존재하는 보이지 않는 위협</h2>
            <p class='section-text'>
                재난 현장, 무너진 건물, 군사 정찰 지역 등 험지는 정보 수집과 인명 구조에 치명적인 위험을 내포하고 있습니다.<br>
                기존의 인력에 의한 탐사나 바퀴형 로봇, 또는 수동 조종 시스템은 자율성과 환경 적응력에서 한계를 드러냅니다.<br>
                이 문제를 해결하기 위해선 복잡한 지형에서도 자율적으로 이동하고, 주변 환경을 인식할 수 있는 새로운 접근이 필요합니다.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 세 번째 섹션
    st.markdown("""
    <div class='section section3'>
        <div class='section-content'>
            <h2 class='section-header'>우리의 솔루션: AI 기반 험지 탐사로봇</h2>
            <p class='section-text'>
            본 시스템은 다관절 족보행 로봇에 고성능 센서와 딥러닝 알고리즘을 결합하여 <br>
            실시간 객체 인식 및 장애물 회피, 경로 재계산 등 자율적인 임무 수행이 가능합니다.
            </p>
            <ul class='section-text'>
                <li class='feature-point'><b>실시간 환경 분석:</b> LiDAR와 카메라로 지형을 인식하고 3D 맵 작성.</li>
                <li class='feature-point'><b>YOLO 기반 객체 탐지:</b> 사람, 균열, 장애물 등 탐지 및 대응.</li>
                <li class='feature-point'><b>지형 적응형 보행:</b> Adaptive Impedance를 통한 다리 높이/각도 조절.</li>
                <li class='feature-point'><b>자율 주행 기능:</b> RRT, A*, POMDP 등 경로 계획 알고리즘 적용.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 네 번째 섹션
    st.markdown("""
    <div class='section section4'>
        <div class='section-content'>
            <h2 class='section-header'>자율성과 안정성을 위한 핵심 기술</h2>
            <p class='section-text'>
            극한 환경에서도 안정적인 탐사를 가능하게 하기 위해<br>최첨단 센서 융합 기술과 로봇 제어 알고리즘을 통합하였습니다.
            </p>
            <ul class='section-text'>
                <li class='feature-point'><b>IMU & PID 제어:</b> 보행 안정화와 전복 방지를 위한 실시간 자세 보정.</li>
                <li class='feature-point'><b>SLAM 기반 자율맵 작성:</b> 미지 환경에서도 자기 위치 추정과 지도 생성.</li>
                <li class='feature-point'><b>P2P 네트워크:</b> 로봇 간 직접 통신을 통해 신뢰성 높은 데이터 공유.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 다섯 번째 섹션
    st.markdown("""
    <div class='section section5'>
        <div class='section-content'>
            <h2 class='section-header'>AI 로봇이 만드는 미래의 구조 전략</h2>
            <p class='section-text'>
            단순한 원격 제어를 넘어, 우리 시스템은 자율적 판단과 데이터 기반 대응이 가능한<br>지능형 플랫폼으로 확장됩니다.
            </p>
            <ul class='section-text'>
                <li class='feature-point'><b>재난 구조 효율화:</b> 구조대원 접근 전 탐색 및 위험 정보 제공.</li>
                <li class='feature-point'><b>군사 정찰 활용:</b> 은폐성 높은 구조로 적진 탐지 및 실시간 영상 수집.</li>
                <li class='feature-point'><b>산업 안전 향상:</b> 고온, 고압 위험지역의 자동 순찰 및 사고 예방.</li>
                <li class='feature-point'><b>정밀 데이터 확보:</b> 극지/지하 등에서 고해상도 시각 정보와 센서 데이터 수집.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 여섯 번째 섹션
    st.markdown("""
    <div class='section section6'>
        <div class='section-content'>
            <h2 class='section-header'>험지 탐사의 미래를 지금 확인하세요.</h2>
            <p class='section-text'>
            본 프로젝트에 대한 더 자세한 정보나 문의 사항, 또는 협업 문의는 아래의 연락처로 연락해주시기 바랍니다.
            </p>
            <div class="contact-info">
                <div class="contact-item">
                    <i class="fas fa-envelope"></i>
                    <a href="mailto:chrisabc94@gmail.com">chrisabc94@gmail.com</a>
                </div>
                <div class="contact-item">
                    <i class="fas fa-phone-alt"></i>
                    <span>+82 10-2204-4587</span>
                </div>
                <div class="contact-item">
                    <i class="fab fa-github"></i>
                    <a href="https://github.com/Find-For-You" target="_blank">GitHub Repository</a>
                </div>
                <div class="contact-item">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>한국공학대학교</span>
                </div>
            </div>
            <p class='section-text' style='margin-top: 2em;'>
            험지에서도 안전하게, 지금 바로 지능형 로봇을 이용한 탐사를 시작하세요.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    pass # Streamlit이 자동으로 실행합니다.