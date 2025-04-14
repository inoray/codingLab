# 취소선 검출 파이썬 코드 (v2)

## 설명

C++ 구현한 취소선 검출 코드입니다. 테스트는 python으로 수행합니다.
claude 를 사용해서 기존 v1 코드를 C++로 변환했습니다.

## C++ dll 빌드 방법

### CMake 빌드 방법

CMake가 설치되어 있어야 합니다. 설치 방법은 [CMake 공식 문서](https://cmake.org/install/)를 참고하세요.

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

빌드가 완료되면 `build/Release` 폴더에 `strikethrough_detector.dll` 파일이 생성됩니다.


## 사용법

아래 명령은 입력 폴더내의 모든 텍스트 이미지에 대해 취소선 검출을 수행합니다. 결과는 별도저장되지 않고 화면에 출력됩니다.

```bash
python strikethrough_detector.py --dll ./build/Release/strikethrough_detector.dll ../sample/strikethrough/

# -dll : dll 파일 경로
# 이미지 폴더
```
