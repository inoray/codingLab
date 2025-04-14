#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <memory>
#include <queue>
#include <limits>

#define DLL_EXPORT __declspec(dllexport)

// 이미지 데이터를 위한 간단한 구조체
struct Image {
    std::vector<uint8_t> data;
    int width;
    int height;
    int channels;

    Image() : width(0), height(0), channels(0) {}

    Image(int w, int h, int c) : width(w), height(h), channels(c) {
        data.resize(width * height * channels, 0);
    }

    uint8_t& at(int x, int y, int channel = 0) {
        return data[(y * width + x) * channels + channel];
    }

    const uint8_t& at(int x, int y, int channel = 0) const {
        return data[(y * width + x) * channels + channel];
    }

    // 그레이스케일 변환
    Image toGrayscale() const {
        if (channels == 1) return *this;

        Image result(width, height, 1);
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                // BT.709 휘도 가중치 사용
                result.at(x, y) = static_cast<uint8_t>(
                    0.2126 * at(x, y, 0) +
                    0.7152 * at(x, y, 1) +
                    0.0722 * at(x, y, 2)
                );
            }
        }
        return result;
    }

    // 이진화
    Image threshold(uint8_t threshold_value) const {
        Image result(width, height, 1);
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                result.at(x, y) = (at(x, y) > threshold_value) ? 0 : 255;
            }
        }
        return result;
    }

    // Otsu 이진화
    Image otsuThreshold() const {
        // 히스토그램 계산
        std::vector<int> histogram(256, 0);
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                histogram[at(x, y)]++;
            }
        }

        // 총 픽셀 수
        int total_pixels = width * height;

        double max_variance = 0.0;
        uint8_t optimal_threshold = 0;

        // 총 합계 및 평균
        double sum = 0;
        for (int i = 0; i < 256; ++i) {
            sum += i * histogram[i];
        }

        double sum_background = 0;
        int weight_background = 0;

        // 각 임계값에 대해 분산 계산
        for (int t = 0; t < 256; ++t) {
            weight_background += histogram[t];
            if (weight_background == 0) continue;

            int weight_foreground = total_pixels - weight_background;
            if (weight_foreground == 0) break;

            sum_background += t * histogram[t];
            double mean_background = sum_background / weight_background;
            double mean_foreground = (sum - sum_background) / weight_foreground;

            // 클래스 간 분산 계산
            double variance = weight_background * weight_foreground *
                              std::pow(mean_background - mean_foreground, 2);

            if (variance > max_variance) {
                max_variance = variance;
                optimal_threshold = t;
            }
        }

        return threshold(optimal_threshold);
    }
};

// 2D 바운딩 박스 구조체
struct BoundingBox {
    int left;
    int top;
    int right;
    int bottom;

    BoundingBox() : left(0), top(0), right(0), bottom(0) {}

    BoundingBox(int l, int t, int r, int b) :
        left(l), top(t), right(r), bottom(b) {}

    int width() const { return right - left; }
    int height() const { return bottom - top; }
};

// 텍스트 영역 특성 저장 구조체
struct TextProperties {
    int height;
    int width;
    int center_y;
    BoundingBox bbox;

    TextProperties() : height(0), width(0), center_y(0) {}
};

// 웨이비 취소선 검출 클래스
class WavyStrikethroughDetector {
private:
    double min_length_ratio;
    double thickness_ratio;
    double continuity_threshold;

public:
    WavyStrikethroughDetector(
        double min_length_ratio_ = 0.7,
        double thickness_ratio_ = 0.15,
        double continuity_threshold_ = 0.6
    ) : min_length_ratio(min_length_ratio_),
        thickness_ratio(thickness_ratio_),
        continuity_threshold(continuity_threshold_) {}

    // 이미지 전처리 및 텍스트 영역 분석
    std::pair<Image, TextProperties> preprocess(const Image& image) {
        // 그레이스케일 변환
        Image gray = image.toGrayscale();

        // 노이즈 제거 (간단한 구현으로 대체)
        Image denoised = applyMedianFilter(gray, 3);

        // 대비 향상 (간단한 구현)
        Image enhanced = enhanceContrast(denoised, 1.5);

        // Otsu 이진화
        Image binary = enhanced.otsuThreshold();

        // 텍스트 영역 분석
        TextProperties text_props = analyzeTextRegion(binary);

        return std::make_pair(binary, text_props);
    }

    // 중간값 필터 적용 (노이즈 제거)
    Image applyMedianFilter(const Image& src, int kernel_size) {
        Image dst(src.width, src.height, src.channels);
        int radius = kernel_size / 2;

        for (int y = 0; y < src.height; ++y) {
            for (int x = 0; x < src.width; ++x) {
                for (int c = 0; c < src.channels; ++c) {
                    std::vector<uint8_t> values;

                    for (int ky = -radius; ky <= radius; ++ky) {
                        for (int kx = -radius; kx <= radius; ++kx) {
                            int nx = x + kx;
                            int ny = y + ky;

                            if (nx >= 0 && nx < src.width && ny >= 0 && ny < src.height) {
                                values.push_back(src.at(nx, ny, c));
                            }
                        }
                    }

                    std::sort(values.begin(), values.end());
                    dst.at(x, y, c) = values[values.size() / 2];
                }
            }
        }

        return dst;
    }

    // 대비 향상
    Image enhanceContrast(const Image& src, double alpha) {
        Image dst(src.width, src.height, src.channels);

        for (int y = 0; y < src.height; ++y) {
            for (int x = 0; x < src.width; ++x) {
                for (int c = 0; c < src.channels; ++c) {
                    double val = static_cast<double>(src.at(x, y, c));
                    val = val * alpha;
                    val = std::min(255.0, std::max(0.0, val));
                    dst.at(x, y, c) = static_cast<uint8_t>(val);
                }
            }
        }

        return dst;
    }

    // 텍스트 영역 분석
    TextProperties analyzeTextRegion(const Image& binary) {
        TextProperties props;

        // 연결 컴포넌트 찾기 (간단한 구현)
        std::vector<BoundingBox> components = findConnectedComponents(binary);

        if (components.empty()) {
            return props;
        }

        // 전체 텍스트 영역 계산
        int left = std::numeric_limits<int>::max();
        int top = std::numeric_limits<int>::max();
        int right = 0;
        int bottom = 0;

        for (const auto& box : components) {
            left = std::min(left, box.left);
            top = std::min(top, box.top);
            right = std::max(right, box.right);
            bottom = std::max(bottom, box.bottom);
        }

        props.bbox = BoundingBox(left, top, right, bottom);
        props.width = right - left;
        props.height = bottom - top;
        props.center_y = (top + bottom) / 2;

        return props;
    }

    // 연결 컴포넌트 찾기
    std::vector<BoundingBox> findConnectedComponents(const Image& binary) {
        std::vector<BoundingBox> components;

        // 방문 여부 추적
        std::vector<std::vector<bool>> visited(binary.height, std::vector<bool>(binary.width, false));

        const int dx[] = {-1, 0, 1, -1, 1, -1, 0, 1}; // 8방향 이동
        const int dy[] = {-1, -1, -1, 0, 0, 1, 1, 1};

        for (int y = 0; y < binary.height; ++y) {
            for (int x = 0; x < binary.width; ++x) {
                if (binary.at(x, y) > 0 && !visited[y][x]) {
                    // 새로운 컴포넌트 시작
                    int min_x = x, min_y = y, max_x = x, max_y = y;

                    // BFS를 사용한 플러드 필
                    std::queue<std::pair<int, int>> queue;
                    queue.push(std::make_pair(x, y));
                    visited[y][x] = true;

                    while (!queue.empty()) {
                        std::pair<int, int> front = queue.front();
                        int cx = front.first;
                        int cy = front.second;
                        queue.pop();

                        min_x = std::min(min_x, cx);
                        min_y = std::min(min_y, cy);
                        max_x = std::max(max_x, cx);
                        max_y = std::max(max_y, cy);

                        for (int d = 0; d < 8; ++d) {
                            int nx = cx + dx[d];
                            int ny = cy + dy[d];

                            if (nx >= 0 && nx < binary.width && ny >= 0 && ny < binary.height &&
                                binary.at(nx, ny) > 0 && !visited[ny][nx]) {
                                queue.push(std::make_pair(nx, ny));
                                visited[ny][nx] = true;
                            }
                        }
                    }

                    components.push_back(BoundingBox(min_x, min_y, max_x + 1, max_y + 1));
                }
            }
        }

        return components;
    }

    // 취소선 후보 영역 추출
    Image extractStrokeComponents(const Image& binary, const TextProperties& text_props) {
        Image stroke_region(binary.width, binary.height, 1);

        // 텍스트 중심 영역 마스크 생성
        int center_y = text_props.center_y;
        int height = text_props.height;
        int y1 = std::max(0, static_cast<int>(center_y - height * 0.3));
        int y2 = std::min(binary.height, static_cast<int>(center_y + height * 0.3));

        // 중심 영역 내 선 성분 추출
        for (int y = y1; y < y2; ++y) {
            for (int x = 0; x < binary.width; ++x) {
                stroke_region.at(x, y) = binary.at(x, y);
            }
        }

        // 모폴로지 연산으로 연결성 강화 (수평 방향 팽창)
        Image connected = dilateHorizontal(stroke_region, 3);

        return connected;
    }

    // 수평 방향 팽창 연산
    Image dilateHorizontal(const Image& src, int kernel_width) {
        Image dst(src.width, src.height, src.channels);

        for (int y = 0; y < src.height; ++y) {
            for (int x = 0; x < src.width; ++x) {
                uint8_t max_val = 0;

                for (int kx = -kernel_width / 2; kx <= kernel_width / 2; ++kx) {
                    int nx = x + kx;
                    if (nx >= 0 && nx < src.width) {
                        max_val = std::max(max_val, src.at(nx, y));
                    }
                }

                dst.at(x, y) = max_val;
            }
        }

        return dst;
    }

    // 수평 투영 계산 및 분석
    std::pair<bool, std::vector<int>> analyzeStrokePattern(const Image& binary, const TextProperties& text_props) {
        if (text_props.height == 0 || text_props.width == 0) {
            return std::make_pair(false, std::vector<int>());
        }

        const BoundingBox& bbox = text_props.bbox;
        std::vector<int> h_proj(bbox.height(), 0);

        // 수평 프로젝션 계산
        for (int y = bbox.top; y < bbox.bottom; ++y) {
            int sum = 0;
            for (int x = bbox.left; x < bbox.right; ++x) {
                sum += (binary.at(x, y) > 0) ? 1 : 0;
            }
            h_proj[y - bbox.top] = sum;
        }

        // 피크 검출
        std::vector<int> peaks = findPeaks(h_proj, text_props.height / 10);

        // 중심선 주변 피크 필터링
        int center_y_local = text_props.height / 2;
        std::vector<int> valid_peaks;

        for (int peak : peaks) {
            if (std::abs(peak - center_y_local) < text_props.height * 0.3) {
                valid_peaks.push_back(peak);
            }
        }

        return std::make_pair(!valid_peaks.empty(), valid_peaks);
    }

    // 피크 검출 함수
    std::vector<int> findPeaks(const std::vector<int>& data, int min_distance) {
        std::vector<int> peaks;

        for (int i = 1; i < static_cast<int>(data.size()) - 1; ++i) {
            if (data[i] > data[i - 1] && data[i] > data[i + 1]) {
                // 로컬 피크 발견
                peaks.push_back(i);
            }
        }

        // 최소 거리 필터링
        if (min_distance > 1 && peaks.size() > 1) {
            std::vector<int> filtered_peaks;
            filtered_peaks.push_back(peaks[0]);

            for (size_t i = 1; i < peaks.size(); ++i) {
                if (peaks[i] - filtered_peaks.back() >= min_distance) {
                    filtered_peaks.push_back(peaks[i]);
                }
            }

            peaks = filtered_peaks;
        }

        return peaks;
    }

    // 레이블링 (연결 컴포넌트 분석)
    std::vector<std::vector<bool>> labelComponents(const Image& binary) {
        int width = binary.width;
        int height = binary.height;

        // 첫 번째 패스: 이미지를 스캔하여 레이블 할당
        int next_label = 1;
        std::vector<std::vector<int>> labels(height, std::vector<int>(width, 0));
        std::vector<int> parent(1, 0);  // 레이블 0은 사용하지 않음

        const int dx4[4] = {-1, 0, 0, 1};
        const int dy4[4] = {0, -1, 1, 0};

        // 첫 번째 패스
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                if (binary.at(x, y) > 0) {  // 전경 픽셀인 경우
                    // 이웃 픽셀 확인
                    std::vector<int> neighbors;
                    for (int d = 0; d < 4; ++d) {
                        int nx = x + dx4[d];
                        int ny = y + dy4[d];

                        if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                            if (labels[ny][nx] > 0) {
                                neighbors.push_back(labels[ny][nx]);
                            }
                        }
                    }

                    if (neighbors.empty()) {
                        // 새 레이블 생성
                        labels[y][x] = next_label;
                        parent.push_back(next_label);
                        next_label++;
                    } else {
                        // 가장 작은 이웃 레이블 사용
                        int min_label = *std::min_element(neighbors.begin(), neighbors.end());
                        labels[y][x] = min_label;

                        // 레이블 합치기
                        for (int neighbor : neighbors) {
                            if (neighbor != min_label) {
                                // Union-Find 알고리즘
                                int root1 = neighbor;
                                while (parent[root1] != root1) root1 = parent[root1];

                                int root2 = min_label;
                                while (parent[root2] != root2) root2 = parent[root2];

                                if (root1 != root2) {
                                    parent[root1] = root2;
                                }
                            }
                        }
                    }
                }
            }
        }

        // 레이블 통합
        for (int i = 1; i < next_label; ++i) {
            int j = i;
            while (parent[j] != j) j = parent[j];
            parent[i] = j;
        }

        // 레이블 재배치 (인덱스 압축)
        std::vector<int> new_labels(next_label, 0);
        int count = 0;

        for (int i = 1; i < next_label; ++i) {
            if (parent[i] == i) {  // 루트 레이블
                new_labels[i] = count++;
            }
        }

        for (int i = 1; i < next_label; ++i) {
            if (parent[i] != i) {
                new_labels[i] = new_labels[parent[i]];
            }
        }

        // 두 번째 패스: 레이블 재할당
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                if (labels[y][x] > 0) {
                    labels[y][x] = new_labels[labels[y][x]];
                }
            }
        }

        // 컴포넌트 마스크 생성
        std::vector<std::vector<bool>> components(count, std::vector<bool>(width * height, false));

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int label = labels[y][x];
                if (label >= 0 && label < count) {  // 유효한 레이블 범위 확인
                    components[label][y * width + x] = true;
                }
            }
        }

        return components;
    }

    // 취소선 검출 함수
    bool detectStrikethrough(const Image& image) {
        // 전처리
        std::pair<Image, TextProperties> prep_result = preprocess(image);
        Image binary = prep_result.first;
        TextProperties text_props = prep_result.second;

        if (text_props.height == 0) {
            return false;
        }

        // 취소선 패턴 분석
        std::pair<bool, std::vector<int>> pattern_result = analyzeStrokePattern(binary, text_props);
        bool has_pattern = pattern_result.first;

        if (!has_pattern) {
            return false;
        }

        // 취소선 성분 추출
        Image stroke_components = extractStrokeComponents(binary, text_props);

        // 연속성 검사
        const BoundingBox& bbox = text_props.bbox;
        int roi_width = bbox.width();
        int min_length = static_cast<int>(roi_width * min_length_ratio);

        // 레이블링
        std::vector<std::vector<bool>> components = labelComponents(stroke_components);

        // 컴포넌트 검사
        for (const auto& component : components) {
            // 컴포넌트 속성 계산
            int x_min = stroke_components.width;
            int x_max = 0;

            for (int y = 0; y < stroke_components.height; ++y) {
                for (int x = 0; x < stroke_components.width; ++x) {
                    if (component[y * stroke_components.width + x]) {
                        x_min = std::min(x_min, x);
                        x_max = std::max(x_max, x);
                    }
                }
            }

            int stroke_length = x_max - x_min;

            // 길이 및 연속성 검증
            if (stroke_length >= min_length) {
                return true;  // 취소선 발견
            }
        }

        return false;  // 취소선 없음
    }
};

// DLL 인터페이스 함수
extern "C" {
    // 취소선 검출기 생성
    DLL_EXPORT void* CreateDetector() {
        return new WavyStrikethroughDetector();
    }

    // 취소선 검출기 해제
    DLL_EXPORT void DestroyDetector(void* detector) {
        delete static_cast<WavyStrikethroughDetector*>(detector);
    }

    // 취소선 검출 실행
    DLL_EXPORT int DetectStrikethrough(void* detector, const uint8_t* image_data, int width, int height, int channels) {
        if (!detector || !image_data || width <= 0 || height <= 0 || (channels != 1 && channels != 3)) {
            return -1;  // 오류: 잘못된 매개변수
        }

        try {
            // 이미지 데이터 복사
            Image img(width, height, channels);
            for (int y = 0; y < height; ++y) {
                for (int x = 0; x < width; ++x) {
                    for (int c = 0; c < channels; ++c) {
                        img.at(x, y, c) = image_data[(y * width + x) * channels + c];
                    }
                }
            }

            // 취소선 검출 수행
            WavyStrikethroughDetector* det = static_cast<WavyStrikethroughDetector*>(detector);
            bool has_strikethrough = det->detectStrikethrough(img);

            return has_strikethrough ? 1 : 0;
        }
        catch (const std::exception& e) {
            std::cerr << "Exception in DetectStrikethrough: " << e.what() << std::endl;
            return -1;
        }
        catch (...) {
            std::cerr << "Unknown exception in DetectStrikethrough" << std::endl;
            return -1;
        }
    }
}
