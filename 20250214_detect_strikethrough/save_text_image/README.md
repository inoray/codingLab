# 문자열 이미지 저장

## 설명

문서의 모든 문자열을 이미지로 저장하는 기능입니다.

## 사용법

아래 명령은 입력 폴더내의 모든 문서이미지에서 텍스트 영역을 찾고, 해당 영역을 결과 이미지 폴더에 저장합니다.
텍스트 영역은 전문인식 xml 파일을 통해 찾습니다.

```bash
python formOcr_test_sf.py -i ./samples/ -x ./form/__fullText.xml -r result_image

# -i : 입력 폴더
# -x : xml 파일 경로
# -r : 결과 이미지 저장 폴더
```
