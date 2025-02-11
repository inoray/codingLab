from paddleocr import PaddleOCR, draw_ocr
import os

ocr = PaddleOCR(lang="korean") ## 한국어 사용시 korean, 영어사용시 en

# 이미지 경로
img_path ='./IMG_5736_r.JPG'


result = ocr.ocr(img_path)

# 추가
result = result[0]

# Recognition and detection can be performed separately through parameter control
# result = ocr.ocr(img_path, det=False)  Only perform recognition
# result = ocr.ocr(img_path, rec=False)  Only perform detection
# Print detection frame and recognition result
for line in result:
    print(line)

# Visualization
from PIL import Image

image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]

font_path = os.path.join('./NanumGothic.ttf')
im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
im_show = Image.fromarray(im_show)
im_show.save('./test_result.jpg')
