from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
import io

def add_text_to_pdf(input_pdf_path, output_pdf_path, text, position):
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"  # 윈도우 맑은 고딕
    font_name = "malgun"
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    # 임시 PDF를 메모리에 생성하여 텍스트 추가
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont(font_name, 12)
    can.setFillColorRGB(0, 0, 0, 0)  # 알파값 0 (완전 투명)
    can.drawString(position[0], position[1], text)
    can.save()

    # 메모리 스트림 위치를 처음으로 이동
    packet.seek(0)
    new_pdf = PdfReader(packet)

    # 원본 PDF 열기
    existing_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()

    # 첫 페이지에 텍스트 추가 (특정 페이지에 추가하려면 인덱스 변경)
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # 나머지 페이지 추가
    for i in range(1, len(existing_pdf.pages)):
        output.add_page(existing_pdf.pages[i])

    # 결과 저장
    with open(output_pdf_path, "wb") as output_stream:
        output.write(output_stream)


def add_text_to_all_pages(input_pdf_path, output_pdf_path, text, position):
    existing_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()

    # 각 페이지마다 처리
    for page_num in range(len(existing_pdf.pages)):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(position[0], position[1], text)
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)

        page = existing_pdf.pages[page_num]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

    # 결과 저장
    with open(output_pdf_path, "wb") as output_stream:
        output.write(output_stream)

def extract_text_with_pypdf2(pdf_path):
    # PDF 파일 열기
    reader = PdfReader(pdf_path)

    # 결과 텍스트를 저장할 변수
    text = ""

    # 모든 페이지의 텍스트 추출
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text() + "\n"

    return text


def get_pdf_page_sizes(pdf_path):
    # PDF 파일 열기
    reader = PdfReader(pdf_path)

    # 결과를 저장할 리스트
    page_sizes = []

    # 모든 페이지의 크기 정보 추출
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]

        # 페이지 크기 정보 얻기
        # mediabox는 PDF 페이지의 물리적 크기를 나타냄
        media_box = page.mediabox
        width = float(media_box.width)
        height = float(media_box.height)

        # 포인트(pt) 단위로 반환됨. 1 pt = 1/72 인치
        page_sizes.append({
            'page_number': page_num + 1,
            'width_pt': width,
            'height_pt': height,
            'width_inch': round(width / 72, 2),
            'height_inch': round(height / 72, 2),
            'width_mm': round(width / 72 * 25.4, 2),
            'height_mm': round(height / 72 * 25.4, 2)
        })

    return page_sizes


# 사용 예시
input_file = "0026.pdf"
output_file = "output_with_text.pdf"
text_to_add = "added text. 한글"
position = (100, 100)  # x, y 좌표 (왼쪽 하단이 원점)

add_text_to_pdf(input_file, output_file, text_to_add, position)

sizes = get_pdf_page_sizes(input_file)

# 결과 출력
for page_size in sizes:
    print(f"페이지 {page_size['page_number']}:")
    print(f"  크기(포인트): {page_size['width_pt']} x {page_size['height_pt']} pt")
    print(f"  크기(인치): {page_size['width_inch']} x {page_size['height_inch']} in")
    print(f"  크기(밀리미터): {page_size['width_mm']} x {page_size['height_mm']} mm")

# 사용 예시
pdf_file = "output_with_text.pdf"
extracted_text = extract_text_with_pypdf2(pdf_file)
print(extracted_text)

# 텍스트를 파일로 저장하는 예시
with open("extracted_text.txt", "w", encoding="utf-8") as text_file:
    text_file.write(extracted_text)
