from xml_graph import *

pyside = True
__version__ = "0.1.0"

# ===============================================
# GUI 생성
# ===============================================

import sys
import os

if pyside:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog, QFrame, QMessageBox)
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QIcon, QColor, QAction
else:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, QFrame, QMessageBox)
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl
    from PyQt5.QtGui import QIcon, QColor, QAction

class HTMLViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Form Xml Relation Viewer v{QApplication.applicationVersion()}")
        self.setWindowIcon(QIcon('./icon/title_icon.svg'))
        self.setGeometry(100, 100, 1200, 800)

        # 상태바에 버전 정보 표시
        self.statusBar().showMessage(f"Version: {__version__}")

        # 메뉴바에 Help 메뉴 및 About 액션 추가
        menubar = self.menuBar()
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 수평 레이아웃 생성
        self.layout = QHBoxLayout(main_widget)

        # 왼쪽 사이드바 생성
        self.create_sidebar()

        # 오른쪽 웹뷰 생성
        self.create_webview()

        # 스타일 설정
        self.apply_styles()

    def show_about_dialog(self):
        # About 다이얼로그에 버전 정보와 추가 설명을 포함
        about_text = (
            f"<h3>Form Xml Relation Viewer</h3>"
            f"<p>Version: {__version__}</p>"
            "<p>서식xml의 연결 관계정보를 보여주는 프로그램입니다.</p>"
            "<p>개발자: shkim</p>"
        )
        QMessageBox.about(self, "About Form Xml Relation Viewer", about_text)

    def create_sidebar(self):
        # 사이드바 프레임
        sidebar = QFrame()
        sidebar.setMaximumWidth(300)
        sidebar.setMinimumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)

        # 로고 레이블
        # logo = QLabel("Form Xml Relation Viewer")
        # logo.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        # sidebar_layout.addWidget(logo)

        # 파일 선택 버튼
        self.select_button = QPushButton("XML 파일 선택")
        self.select_button.clicked.connect(self.select_html_file)
        sidebar_layout.addWidget(self.select_button)

        # 파일 정보 레이블
        self.file_label = QLabel("선택된 파일 없음")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("color: white;")
        sidebar_layout.addWidget(self.file_label)

        # 여백을 위한 스트레치
        sidebar_layout.addStretch()

        self.layout.addWidget(sidebar)

    def create_webview(self):
        # 웹뷰 생성
        self.web_view = QWebEngineView()
        self.web_view.setMinimumWidth(400)
        self.layout.addWidget(self.web_view)
        self.web_view.page().setBackgroundColor(QColor("#282c34"))

    def select_html_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "XML 파일 선택",
            "",
            "XML files (*.xml);;All files (*.*)"
        )

        if file_path:
            # 파일 레이블 업데이트
            self.file_label.setText(f"선택된 파일:\n{os.path.basename(file_path)}")

            html, _ = gen_pyvis_html(file_path)
            self.web_view.setHtml (html)

            # with open("./pyvis_graph.html", mode='w', encoding='utf-8') as fp:
            #     fp.write(html)

            # # html 파일을 절대경로로 변경
            # abs_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyvis_graph.html")
            # HTML 파일을 웹뷰에 로드
            # self.web_view.setUrl(QUrl.fromLocalFile(abs_html))


    def apply_styles(self):
        # 다크 테마 스타일 적용
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QFrame {
                background-color: #282c34;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QWebEngineView {
                background-color: #282c34;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QLabel {
                color: #abb2bf;
                padding: 5px;
            }
        """)

def main():
    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)

    # 메인 윈도우 생성 및 표시
    viewer = HTMLViewerApp()
    viewer.showMaximized()

    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
