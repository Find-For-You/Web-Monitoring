import cv2
import numpy as np
from typing import Optional, Tuple
import logging
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class StreamUtils:
    """스트림 유틸리티 클래스"""
    
    @staticmethod
    def generate_rtsp_url(robot_id: str, ip_address: str, port: int = 8554) -> str:
        """RTSP 스트림 URL 생성"""
        return f"rtsp://{ip_address}:{port}/stream/{robot_id}"
    
    @staticmethod
    def generate_http_url(robot_id: str, ip_address: str, port: int = 8080) -> str:
        """HTTP 스트림 URL 생성"""
        return f"http://{ip_address}:{port}/stream/{robot_id}"
    
    @staticmethod
    def generate_https_url(robot_id: str, domain: str, port: int = 443) -> str:
        """HTTPS 스트림 URL 생성"""
        return f"https://{domain}:{port}/stream/{robot_id}"
    
    @staticmethod
    def test_stream_connection(stream_url: str, timeout: int = 5) -> bool:
        """스트림 연결 테스트"""
        try:
            cap = cv2.VideoCapture(stream_url)
            cap.set(cv2.CAP_PROP_TIMEOUT, timeout * 1000)
            
            if not cap.isOpened():
                logger.warning(f"스트림 연결 실패: {stream_url}")
                return False
            
            # 첫 프레임 읽기 시도
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logger.warning(f"스트림에서 프레임 읽기 실패: {stream_url}")
                return False
            
            logger.info(f"스트림 연결 성공: {stream_url}")
            return True
            
        except Exception as e:
            logger.error(f"스트림 연결 테스트 중 오류: {e}")
            return False
    
    @staticmethod
    def capture_frame(stream_url: str) -> Optional[np.ndarray]:
        """스트림에서 단일 프레임 캡처"""
        try:
            cap = cv2.VideoCapture(stream_url)
            cap.set(cv2.CAP_PROP_TIMEOUT, 5000)  # 5초 타임아웃
            
            if not cap.isOpened():
                logger.warning(f"스트림 열기 실패: {stream_url}")
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logger.warning(f"프레임 읽기 실패: {stream_url}")
                return None
            
            return frame
            
        except Exception as e:
            logger.error(f"프레임 캡처 중 오류: {e}")
            return None
    
    @staticmethod
    def frame_to_base64(frame: np.ndarray, quality: int = 80) -> str:
        """프레임을 Base64로 인코딩"""
        try:
            # BGR to RGB 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # PIL Image로 변환
            pil_image = Image.fromarray(rgb_frame)
            
            # JPEG로 압축
            buffer = BytesIO()
            pil_image.save(buffer, format='JPEG', quality=quality)
            
            # Base64 인코딩
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"프레임 Base64 인코딩 실패: {e}")
            return ""
    
    @staticmethod
    def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
        """프레임 크기 조정"""
        try:
            return cv2.resize(frame, (width, height))
        except Exception as e:
            logger.error(f"프레임 크기 조정 실패: {e}")
            return frame
    
    @staticmethod
    def apply_quality_settings(frame: np.ndarray, quality: str = 'medium') -> np.ndarray:
        """품질 설정에 따른 프레임 처리"""
        try:
            if quality == 'low':
                # 낮은 품질: 크기 축소
                height, width = frame.shape[:2]
                new_width = int(width * 0.5)
                new_height = int(height * 0.5)
                frame = cv2.resize(frame, (new_width, new_height))
                
            elif quality == 'high':
                # 높은 품질: 노이즈 제거
                frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
            
            return frame
            
        except Exception as e:
            logger.error(f"품질 설정 적용 실패: {e}")
            return frame
    
    @staticmethod
    def detect_motion(frame1: np.ndarray, frame2: np.ndarray, threshold: float = 0.1) -> bool:
        """모션 감지"""
        try:
            # 그레이스케일 변환
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # 차이 계산
            diff = cv2.absdiff(gray1, gray2)
            
            # 임계값 적용
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            # 모션 픽셀 비율 계산
            motion_ratio = np.sum(thresh > 0) / thresh.size
            
            return motion_ratio > threshold
            
        except Exception as e:
            logger.error(f"모션 감지 실패: {e}")
            return False
    
    @staticmethod
    def get_frame_info(frame: np.ndarray) -> dict:
        """프레임 정보 추출"""
        try:
            height, width = frame.shape[:2]
            channels = frame.shape[2] if len(frame.shape) > 2 else 1
            
            return {
                'width': width,
                'height': height,
                'channels': channels,
                'size_bytes': frame.nbytes,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"프레임 정보 추출 실패: {e}")
            return {}
    
    @staticmethod
    def create_thumbnail(frame: np.ndarray, max_size: Tuple[int, int] = (320, 240)) -> np.ndarray:
        """썸네일 생성"""
        try:
            height, width = frame.shape[:2]
            max_width, max_height = max_size
            
            # 비율 유지하면서 크기 조정
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            thumbnail = cv2.resize(frame, (new_width, new_height))
            return thumbnail
            
        except Exception as e:
            logger.error(f"썸네일 생성 실패: {e}")
            return frame
    
    @staticmethod
    def validate_stream_url(url: str) -> bool:
        """스트림 URL 유효성 검사"""
        try:
            # 기본적인 URL 형식 검사
            if not url.startswith(('rtsp://', 'http://', 'https://')):
                return False
            
            # IP 주소나 도메인 형식 검사
            parts = url.split('/')
            if len(parts) < 3:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL 유효성 검사 실패: {e}")
            return False
    
    @staticmethod
    def get_stream_statistics(stream_url: str, duration: int = 10) -> dict:
        """스트림 통계 정보 수집"""
        try:
            cap = cv2.VideoCapture(stream_url)
            cap.set(cv2.CAP_PROP_TIMEOUT, 5000)
            
            if not cap.isOpened():
                return {'error': '스트림을 열 수 없습니다'}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = 0
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < duration:
                ret, frame = cap.read()
                if ret:
                    frame_count += 1
                else:
                    break
            
            cap.release()
            
            actual_duration = (datetime.now() - start_time).seconds
            actual_fps = frame_count / actual_duration if actual_duration > 0 else 0
            
            return {
                'fps': fps,
                'actual_fps': actual_fps,
                'frame_count': frame_count,
                'duration': actual_duration,
                'dropped_frames': max(0, int(fps * actual_duration) - frame_count) if fps > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"스트림 통계 수집 실패: {e}")
            return {'error': str(e)}
