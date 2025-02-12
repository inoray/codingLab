import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QTextEdit,
                               QMessageBox, QGraphicsView, QGraphicsScene,
                               QSplitter, QToolBar, QGraphicsItem  )
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QPolygonF, QAction
from PySide6.QtCore import Qt, QPointF, QThread, Signal, QSettings
import cv2
import numpy as np
from paddleocr import PaddleOCR
from qt_material import apply_stylesheet

# OCR 작업을 별도 스레드에서 수행하기 위한 워커 클래스
class OCRWorker(QThread):
    progress = Signal(int)  # 진행률 (%)
    finished = Signal(list)  # OCR 결과 리스트

    def __init__(self, images, ocr):
        super().__init__()
        self.images = images
        self.ocr = ocr

    def run(self):
        results = []
        total = len(self.images)
        for i, image in enumerate(self.images):
            result = self.ocr.ocr(image)
            results.append(result[0])
            self.progress.emit(int((i + 1) / total * 100))
        self.finished.emit(results)

# 이미지 뷰어 (이미지 확대/축소 및 오버레이)
class ImageViewer(QGraphicsView):
    zoomChanged = Signal(float)  # 확대/축소 비율 변경 시 전달

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.zoom_factor = 1.0
        self.pixmap_item = None

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor
            old_pos = self.mapToScene(event.position().toPoint())
            if event.angleDelta().y() > 0:
                factor = zoom_in_factor
            else:
                factor = zoom_out_factor
            self.scale(factor, factor)
            self.zoom_factor *= factor
            new_pos = self.mapToScene(event.position().toPoint())
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())
            self.zoomChanged.emit(self.zoom_factor)
        else:
            super().wheelEvent(event)

    def reset_view(self):
        self.resetTransform()
        self.zoom_factor = 1.0
        if self.pixmap_item:
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        self.zoomChanged.emit(self.zoom_factor)

# 메인 윈도우
class OCRWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PaddleOCR Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.settings = QSettings("MyCompany", "PaddleOCRViewer")

        self.current_image_index = 0
        self.images = []
        self.image_paths = []
        self.ocr_results = []
        self.ocr = PaddleOCR(use_angle_cls=True, lang='korean')
        self.ocr_worker = None

        self.setup_ui()

    def setup_ui(self):
        # 툴바 생성 및 네비게이션 액션 추가
        toolbar = QToolBar("Navigation")
        self.addToolBar(toolbar)

        prev_action = QAction("이전", self)
        prev_action.setShortcut("Ctrl+Left")
        prev_action.triggered.connect(self.show_previous_image)
        toolbar.addAction(prev_action)

        next_action = QAction("다음", self)
        next_action.setShortcut("Ctrl+Right")
        next_action.triggered.connect(self.show_next_image)
        toolbar.addAction(next_action)

        original_action = QAction("원본크기 보기", self)
        original_action.setShortcut("Ctrl+O")
        original_action.triggered.connect(self.view_original_size)
        toolbar.addAction(original_action)

        # 메뉴바 설정 (파일 메뉴)
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일")
        open_action = file_menu.addAction("이미지 열기")
        open_action.triggered.connect(self.load_images)

        # 중앙 위젯 및 레이아웃 설정 (사이드바 + 이미지 뷰어)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 좌측 사이드바: OCR 실행 버튼과 결과 텍스트 영역 배치
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)

        self.ocr_button = QPushButton("OCR 실행")
        self.ocr_button.clicked.connect(self.perform_ocr)
        sidebar_layout.addWidget(self.ocr_button)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        sidebar_layout.addWidget(self.text_edit)
        sidebar_layout.addStretch()

        # 이미지 뷰어 생성 및 확대/축소 변경 시 상태바 업데이트 연결
        self.image_viewer = ImageViewer()
        self.image_viewer.zoomChanged.connect(self.update_zoom_status)

        splitter.addWidget(sidebar)
        splitter.addWidget(self.image_viewer)
        splitter.setSizes([200, 800])

        self.update_button_states()

    def update_zoom_status(self, zoom_factor):
        self.statusBar().showMessage(f"Zoom: {zoom_factor * 100:.0f}%")

    def view_original_size(self):
        self.image_viewer.resetTransform()
        self.image_viewer.zoom_factor = 1.0
        self.update_zoom_status(1.0)

    def load_images(self):
        # 마지막 작업 폴더를 기억하여 초기 디렉토리로 지정
        last_folder = self.settings.value("last_folder", "")
        image_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "이미지 파일 선택",
            last_folder,
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if image_paths:
            self.image_paths = image_paths
            self.images = []
            self.ocr_results = []

            for path in image_paths:
                # img = cv2.imread(str(Path(path)))
                # 한글파일명 처리를 위해서 fromfile와 imdecode 사용
                img_array = np.fromfile(path, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
                if img is None:
                    QMessageBox.warning(self, "Error", f"이미지 로드 실패: {path}")
                    continue
                self.images.append(img)

            if self.images:
                # 선택한 이미지의 폴더 경로 저장
                self.settings.setValue("last_folder", str(Path(image_paths[0]).parent))
                self.current_image_index = 0
                self.show_current_image()
                self.update_button_states()

    def show_current_image(self):
        if not self.images:
            return

        image = self.images[self.current_image_index].copy()
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.image_viewer.scene.clear()
        self.image_viewer.pixmap_item = self.image_viewer.scene.addPixmap(pixmap)

        # OCR 결과 오버레이 (텍스트와 박스 모두 다크 블루)
        if self.ocr_results and len(self.ocr_results) > self.current_image_index:
            result = self.ocr_results[self.current_image_index]
            for line in result:
                points = line[0]
                text = line[1][0]

                # 박스 그리기
                self.image_viewer.scene.addPolygon(
                    QPolygonF([QPointF(p[0], p[1]) for p in points]),
                    QPen(QColor(0, 0, 139), 2)
                )
                # 텍스트 추가 및 확대/축소 무시 설정
                text_item = self.image_viewer.scene.addText(text)
                text_item.setDefaultTextColor(QColor(0, 0, 139))
                text_item.setPos(points[0][0], points[0][1] - 20)
                text_item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # 수정된 부분

        if len(self.images) == 1:
            self.image_viewer.fitInView(self.image_viewer.pixmap_item, Qt.KeepAspectRatio)

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_current_image()
            self.update_button_states()
            self.update_text_display()

    def show_next_image(self):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.show_current_image()
            self.update_button_states()
            self.update_text_display()

    def update_button_states(self):
        # OCR 버튼만 사이드바에 남김 (네비게이션은 툴바에 있음)
        self.ocr_button.setEnabled(bool(self.images))

    def perform_ocr(self):
        if not self.images:
            return

        self.ocr_button.setEnabled(False)
        self.text_edit.clear()
        self.statusBar().showMessage("OCR 수행중... 0%")

        self.ocr_worker = OCRWorker(self.images, self.ocr)
        self.ocr_worker.progress.connect(self.update_ocr_progress)
        self.ocr_worker.finished.connect(self.ocr_finished)
        self.ocr_worker.start()

    def update_ocr_progress(self, value):
        self.statusBar().showMessage(f"OCR 수행중... {value}%")

    def ocr_finished(self, results):
        self.ocr_results = results
        self.show_current_image()
        self.update_text_display()
        self.ocr_button.setEnabled(True)
        self.statusBar().showMessage("OCR 완료")

    def update_text_display(self):
        if not self.ocr_results or self.current_image_index >= len(self.ocr_results):
            return
        result = self.ocr_results[self.current_image_index]
        text = "\n".join([line[1][0] for line in result])
        self.text_edit.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = OCRWindow()
    window.show()
    sys.exit(app.exec())
