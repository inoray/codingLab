import os
import cv2
import numpy as np
from typing import Tuple, Dict
from scipy.signal import find_peaks
from scipy.ndimage import label as ndi_label
from scipy.ndimage import binary_dilation
import time
from pathlib import Path
import argparse
import multiprocessing
from tqdm.contrib.concurrent import process_map

parser = argparse.ArgumentParser(description="formOcr",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--image_dir', required=True, help='path to image_dir which contains text images')
parser.add_argument('-r', '--result_dir', type=str, default='result')
parser.add_argument('-c', '--cpu', type=int, default=0)

args = parser.parse_args()


class WavyStrikethroughDetector:
    def __init__(self,
                 min_length_ratio: float = 0.7,    # 텍스트 너비 대비 최소 길이 비율
                 thickness_ratio: float = 0.15,    # 텍스트 높이 대비 최대 두께 비율
                 continuity_threshold: float = 0.6):# 연속성 판단 임계값
        """
        Parameters:
        min_length_ratio: 텍스트 전체 길이 대비 최소 취소선 길이 비율
        thickness_ratio: 텍스트 높이 대비 취소선 최대 두께 비율
        continuity_threshold: 취소선 연속성 판단 임계값
        """
        self.min_length_ratio = min_length_ratio
        self.thickness_ratio = thickness_ratio
        self.continuity_threshold = continuity_threshold

    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """이미지 전처리 및 텍스트 영역 분석"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 노이즈 제거 및 선명도 향상
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        enhanced = cv2.addWeighted(denoised, 1.5, denoised, -0.5, 0)

        # Otsu 이진화
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 텍스트 영역 분석
        text_props = self._analyze_text_region(binary)

        return binary, text_props

    def _analyze_text_region(self, binary: np.ndarray) -> Dict:
        """텍스트 영역 분석"""
        # 외곽 컨투어 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return {'height': 0, 'width': 0, 'center_y': 0, 'bbox': None}

        # 전체 텍스트 영역 계산
        x_coords = []
        y_coords = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            x_coords.extend([x, x + w])
            y_coords.extend([y, y + h])

        left, right = min(x_coords), max(x_coords)
        top, bottom = min(y_coords), max(y_coords)

        return {
            'height': bottom - top,
            'width': right - left,
            'center_y': (top + bottom) // 2,
            'bbox': (left, top, right, bottom)
        }

    def analyze_stroke_pattern(self, binary: np.ndarray, text_props: Dict) -> Tuple[bool, np.ndarray]:
        """웨이비 패턴 분석"""
        bbox = text_props['bbox']
        if not bbox:
            return False, np.array([])

        left, top, right, bottom = bbox
        roi = binary[top:bottom, left:right]

        # 수평 프로젝션 프로필 계산
        h_proj = np.sum(roi, axis=1) / 255

        # 피크 검출
        peaks, _ = find_peaks(h_proj,
                            distance=max(3, text_props['height'] // 10),
                            prominence=roi.shape[1] * 0.1)

        if len(peaks) < 1:
            return False, np.array([])

        # 중심선 주변 피크 필터링
        center_y_local = text_props['height'] // 2
        valid_peaks = peaks[np.abs(peaks - center_y_local) < text_props['height'] * 0.3]

        return len(valid_peaks) > 0, valid_peaks

    def extract_stroke_components(self, binary: np.ndarray, text_props: Dict) -> np.ndarray:
        """취소선 후보 영역 추출"""
        # 텍스트 중심 영역 마스크 생성
        center_y = text_props['center_y']
        height = text_props['height']
        mask = np.zeros_like(binary)
        y1 = max(0, int(center_y - height * 0.3))
        y2 = min(binary.shape[0], int(center_y + height * 0.3))
        mask[y1:y2, :] = 1

        # 중심 영역 내 선 성분 추출
        stroke_region = cv2.bitwise_and(binary, binary, mask=mask)

        # 모폴로지 연산으로 연결성 강화
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        connected = binary_dilation(stroke_region, kernel)

        return connected

    def detect_strikethrough(self, image: np.ndarray) -> Tuple[bool, np.ndarray]:
        """웨이비 취소선 검출"""
        # 전처리
        binary, text_props = self.preprocess(image)
        if text_props['height'] == 0:
            return False, image

        # 결과 이미지 준비
        # result = image.copy()
        # if len(result.shape) == 2:
        #     result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

        # 취소선 패턴 분석
        has_pattern, peaks = self.analyze_stroke_pattern(binary, text_props)
        if not has_pattern:
            return False

        # 취소선 성분 추출
        stroke_components = self.extract_stroke_components(binary, text_props)

        # 연속성 검사
        left, top, right, bottom = text_props['bbox']
        roi_width = right - left
        min_length = roi_width * self.min_length_ratio

        # 레이블링 (수정된 부분)
        labeled_array, num_features = ndi_label(stroke_components)

        valid_strikethrough = False
        for i in range(1, num_features + 1):
            component = (labeled_array == i)

            # 컴포넌트 속성 계산
            coords = np.where(component)
            if len(coords[1]) == 0:
                continue

            x_min, x_max = np.min(coords[1]), np.max(coords[1])
            stroke_length = x_max - x_min

            # 길이 및 연속성 검증
            if stroke_length >= min_length:
                valid_strikethrough = True
                # 검출된 취소선 시각화
                y_coords = coords[0] + top
                x_coords = coords[1] + left
                # result[y_coords, x_coords] = [0, 255, 0]

        # 결과 텍스트 표시
        result_text = "Wavy Strikethrough" if valid_strikethrough else "No Strikethrough"
        text_color = (0, 255, 0) if valid_strikethrough else (0, 0, 255)
        # cv2.putText(result, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

        return valid_strikethrough#, result


def get_image_files(directory):
    """
    Get all image files from the specified directory, including subdirectories.

    Args:
    - directory (str or Path): The path of the directory to search for image files.

    Returns:
    - list of str: List of paths to image files.
    """
    # Define image extensions to filter
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.webp'}

    # List to hold paths to image files
    image_files = []

    # Using pathlib to traverse directories
    directory = Path(directory)

    # Iterate over all files recursively
    for image_path in directory.rglob('*'):
        # Verify the file has a valid image extension
        if image_path.suffix.lower() in image_extensions:
            image_files.append(str(image_path))

    image_files.sort()

    return image_files


def detect_strikethrough(params): #detector, image_name):
    detector = params[0]
    image_name = params[1]

    # 이미지 로드
    img_array = np.fromfile(image_name, np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
    # image = cv2.imread(image_name)

    # 취소선 검출
    has_strikethrough = detector.detect_strikethrough(image)

    # 결과 저장
    # result_name = os.path.join(result_dir, os.path.basename(image_name))
    # cv2.imwrite(result_name, result)

    return {'filename': image_name, 'has_strikethrough': has_strikethrough}


# 사용 예제
if __name__ == "__main__":
    system_cpu_count = multiprocessing.cpu_count()
    used_cpu_count = int(system_cpu_count * 1)
    if args.cpu > 0:
        used_cpu_count = min (args.cpu, used_cpu_count)

    print(f'- test info')
    print(f'  - image dir: {args.image_dir}')
    print(f'  - result dir: {args.result_dir}')
    print('--------------------------------------------------------')

    result_dir = args.result_dir
    os.makedirs(result_dir, exist_ok=True)

    # 검출기 초기화
    detector = WavyStrikethroughDetector()

    image_list = get_image_files(args.image_dir)

    start_time = time.time()
    process_sample_list = [(detector, file) for file in image_list]
    result_list = process_map(detect_strikethrough, process_sample_list, max_workers=used_cpu_count, chunksize=1)
    end_time = time.time()

    # true/false count
    true_count = 0
    false_count = 0
    for result in result_list:
        if result['has_strikethrough']:
            true_count += 1
        else:
            false_count += 1

    # 결과를 파일로 저장
    # args.result_dir의 마지막 경로이름을 가져온다.
    basename = os.path.basename(os.path.normpath(args.image_dir))
    result_file = os.path.join(result_dir, basename + ".txt")
    with open(result_file, 'w') as f:
        f.write(f"Total: {len(result_list)}\n")
        f.write(f"True: {true_count} ({true_count/len(result_list):.3f})\n")
        f.write(f"False: {false_count} ({false_count/len(result_list):.3f})\n")
        for result in result_list:
            f.write(f"{result['filename']}: {result['has_strikethrough']}\n")

    # true/false 결과에 따라서 원본 이미지를 true, false 디렉토리에 복사한다.
    true_dir = os.path.join(result_dir, basename, 'true')
    false_dir = os.path.join(result_dir, basename, 'false')
    os.makedirs(true_dir, exist_ok=True)
    os.makedirs(false_dir, exist_ok=True)

    for result in result_list:
        if result['has_strikethrough']:
            dst_dir = true_dir
        else:
            dst_dir = false_dir
        dst_file = os.path.join(dst_dir, os.path.basename(result['filename']))
        os.system(f'cp {result["filename"]} {dst_file}')

    print(f'Elapsed time: {end_time - start_time:.2f} sec')
    print('')
