import os
import ctypes
import numpy as np
from PIL import Image
import argparse

"""명령줄에서 실행 시 메인 함수"""
parser = argparse.ArgumentParser(description='텍스트 이미지에서 취소선 검출')
parser.add_argument('image_path', help='검사할 이미지 파일 경로')
parser.add_argument('--dll', default='strikethrough_detector.dll', help='DLL 파일 경로')
args = parser.parse_args()

class StrikethroughDetector:
    def __init__(self, dll_path='strikethrough_detector.dll'):
        """
        취소선 검출기 초기화

        Parameters:
        -----------
        dll_path : str
            DLL 파일 경로
        """
        # DLL 로드
        try:
            self.lib = ctypes.CDLL(dll_path)
        except Exception as e:
            raise RuntimeError(f"DLL 로드 실패: {e}")

        # 함수 프로토타입 설정
        self.lib.CreateDetector.restype = ctypes.c_void_p

        self.lib.DestroyDetector.argtypes = [ctypes.c_void_p]
        self.lib.DestroyDetector.restype = None

        self.lib.DetectStrikethrough.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int
        ]
        self.lib.DetectStrikethrough.restype = ctypes.c_int

        # 검출기 인스턴스 생성
        self.detector = self.lib.CreateDetector()
        if not self.detector:
            raise RuntimeError("검출기 생성 실패")

    def __del__(self):
        """소멸자: 검출기 리소스 해제"""
        if hasattr(self, 'lib') and hasattr(self, 'detector') and self.detector:
            self.lib.DestroyDetector(self.detector)

    def detect(self, image):
        """
        이미지에서 취소선 검출

        Parameters:
        -----------
        image : PIL.Image or numpy.ndarray or str
            검사할 이미지 또는 이미지 파일 경로

        Returns:
        --------
        bool
            취소선 존재 여부
        """
        if isinstance(image, str):
            # 파일 경로인 경우 이미지 로드
            try:
                image = Image.open(image)
            except Exception as e:
                raise ValueError(f"이미지 파일 로드 실패: {e}")

        if isinstance(image, Image.Image):
            # PIL 이미지를 NumPy 배열로 변환
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_np = np.array(image)
        elif isinstance(image, np.ndarray):
            # NumPy 배열인 경우 그대로 사용
            image_np = image
        else:
            raise TypeError("지원되지 않는 이미지 형식. PIL.Image, numpy.ndarray 또는 파일 경로가 필요합니다.")

        # 이미지 차원 확인
        if len(image_np.shape) == 2:  # 그레이스케일
            height, width = image_np.shape
            channels = 1
            # 재구성
            image_np = image_np.reshape(height, width, 1)
        elif len(image_np.shape) == 3:  # 컬러
            height, width, channels = image_np.shape
            if channels != 3:
                raise ValueError(f"지원되지 않는 채널 수: {channels}. 1(그레이스케일) 또는 3(RGB)만 지원합니다.")
        else:
            raise ValueError(f"지원되지 않는 이미지 형태: {image_np.shape}")

        # 연속된 메모리 보장 (C order)
        if not image_np.flags['C_CONTIGUOUS']:
            image_np = np.ascontiguousarray(image_np)

        # 이미지 데이터 포인터 생성
        data_ptr = image_np.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))

        # DLL 함수 호출
        result = self.lib.DetectStrikethrough(
            self.detector,
            data_ptr,
            width,
            height,
            channels
        )

        if result == -1:
            raise RuntimeError("취소선 검출 중 오류 발생")

        return result == 1


def main():

    try:
        # 검출기 초기화
        detector = StrikethroughDetector(args.dll)

        # 이미지 로드 및 취소선 검출
        result = detector.detect(args.image_path)

        # 결과 출력
        if result:
            print(f"[결과] '{args.image_path}': 취소선이 검출되었습니다.")
        else:
            print(f"[결과] '{args.image_path}': 취소선이 검출되지 않았습니다.")

        return 0
    except Exception as e:
        print(f"오류: {e}")
        return 1


def batch_process(directory, dll_path='strikethrough_detector.dll'):
    """
    디렉토리 내 모든 이미지 파일에 대해 취소선 검출 수행

    Parameters:
    -----------
    directory : str
        이미지 파일이 있는 디렉토리 경로
    dll_path : str
        DLL 파일 경로
    """
    # 지원하는 이미지 확장자
    supported_ext = ('.jpg', '.jpeg', '.png', '.bmp')

    # 검출기 초기화
    detector = StrikethroughDetector(dll_path)

    # 결과 저장 리스트
    results = []

    # 디렉토리 내 모든 파일 검사
    for filename in os.listdir(directory):
        if filename.lower().endswith(supported_ext):
            file_path = os.path.join(directory, filename)
            try:
                result = detector.detect(file_path)
                results.append((filename, result))
                print(f"[처리] '{filename}': {'취소선 있음' if result else '취소선 없음'}")
            except Exception as e:
                print(f"[오류] '{filename}': {e}")

    # 결과 요약
    strikethrough_count = sum(1 for _, res in results if res)
    total_count = len(results)

    print(f"\n===== 처리 완료 =====")
    print(f"총 파일: {total_count}")
    print(f"취소선 있음: {strikethrough_count}")
    print(f"취소선 없음: {total_count - strikethrough_count}")

    return results


if __name__ == '__main__':
    # exit(main())
    batch_process (args.image_path, args.dll)
