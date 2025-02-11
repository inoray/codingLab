# ===============================================
# GUI 생성
# ===============================================

import sys
import os
from xml_graph import *
import file_graph

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, QFrame,
                            QMessageBox, QSplitter, QTreeView, QFileSystemModel, QSizePolicy,
                            QTextEdit, QDockWidget)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, QDir
from PySide6.QtGui import QIcon, QColor, QAction

from qt_material import apply_stylesheet

__version__ = "0.1.0"

class FormXmlViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.win_title = f"Form Xml Relation Viewer v{QApplication.applicationVersion()}"
        self.work_dir = QDir.currentPath()
        self.file_path = None

        self.setWindowTitle(self.win_title)
        self.setWindowIcon(QIcon('./icon/title_icon.svg'))
        self.setGeometry(100, 100, 1200, 800)

        # 상태바에 버전 정보 표시
        self.statusBar().showMessage(f"Version: {__version__}")

        # QSplitter 생성 (수평 방향)
        self.layout = QSplitter(Qt.Horizontal)

        # QSplitter를 메인 윈도우의 중심 위젯으로 설정
        self.setCentralWidget(self.layout)

        # 왼쪽 사이드바 생성
        self.create_sidebar()

        # 오른쪽 웹뷰 생성
        self.create_webview()

        # 도킹 웹뷰 생성
        self.create_dock_webview()

        # 메뉴 생성
        self.create_menu()

        # 스타일 설정
        self.apply_styles()

        self.view_only_graph()


    def load_folder(self):
        # QFileDialog를 사용하여 폴더 선택
        folder_path = QFileDialog.getExistingDirectory(self, "폴더 선택", self.work_dir)
        if folder_path:
            self.tree_view.setRootIndex(self.model.index(folder_path))
            self.dir_label.setText(folder_path)
            self.work_dir = folder_path
            self.view_only_graph()


    def on_item_clicked(self, index):
        # 선택된 항목의 파일 경로 가져오기
        self.file_path = self.model.filePath(index)
        if self.model.isDir(index):
            # 디렉토리인 경우: 하위 항목을 확장
            if not self.tree_view.isExpanded(index):
                self.tree_view.expand(index)
            else:
                self.tree_view.collapse(index)
        else:
            self.view_graph()


    def show_about_dialog(self):
        # About 다이얼로그에 버전 정보와 추가 설명을 포함
        about_text = (
            f"<h3>Form Xml Relation Viewer</h3>"
            f"<p>Version: {__version__}</p>"
            "<p>서식xml의 연결 관계정보를 보여주는 프로그램입니다.</p>"
            "<p>개발자: shkim</p>"
        )
        QMessageBox.about(self, "About Form Xml Relation Viewer", about_text)


    def create_menu(self):

        # 메뉴바에 Help 메뉴 및 About 액션 추가
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        view_menu = menubar.addMenu("&View")
        help_menu = menubar.addMenu("&Help")

        # file
        open_xml_action = QAction("Open Xml", self)
        open_xml_action.triggered.connect(self.select_xml_file)
        file_menu.addAction(open_xml_action)

        load_folder_action = file_menu.addAction("Open Folder")
        load_folder_action.triggered.connect(self.load_folder)

        # view
        view_menu.addAction(self.dock.toggleViewAction())

        # help
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)


    def create_sidebar(self):
        # 사이드바 프레임
        sidebar = QFrame()
        sidebar.setMaximumWidth(400)
        sidebar.setMinimumWidth(200)
        self.sidebar_layout = QVBoxLayout(sidebar)

        # 파일 정보 레이블
        self.dir_label = QLabel(self.work_dir)
        self.dir_label.setWordWrap(True)
        self.sidebar_layout.addWidget(self.dir_label)

        # 사이드 바로 사용할 QTreeView 생성
        self.create_treeview()

        # 여백을 위한 스트레치
        # self.sidebar_layout.addStretch()

        self.form_info = QTextEdit()
        self.form_info.setReadOnly(True)
        self.sidebar_layout.addWidget(self.form_info)

        self.layout.addWidget(sidebar)


    def create_treeview(self):

        # 사이드 바로 사용할 QTreeView 생성
        self.tree_view = QTreeView()
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sidebar_layout.addWidget(self.tree_view)

        # QFileSystemModel 설정
        self.model = QFileSystemModel()
        self.model.setRootPath(self.work_dir)
        self.model.setNameFilters(["*.xml"])
        self.model.setNameFilterDisables(False)
        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.work_dir))

        # QTreeView에서 이름 열만 표시하고 나머지 열 숨기기
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)  # Size 열 숨기기
        self.tree_view.setColumnHidden(2, True)  # Type 열 숨기기
        self.tree_view.setColumnHidden(3, True)  # Date Modified 열 숨기기

        self.tree_view.setAnimated(True)

        # QTreeView의 시그널에 슬롯 연결
        self.tree_view.clicked.connect(self.on_item_clicked)


    def create_webview(self):
        # 웹뷰 생성
        webview_frame = QFrame()
        webview_layout = QVBoxLayout(webview_frame)

        self.web_view = QWebEngineView()
        self.web_view.setMinimumWidth(400)
        webview_layout.addWidget(self.web_view)

        self.layout.addWidget(webview_frame)
        self.web_view.page().setBackgroundColor(QColor("#282c34"))


    def create_dock_webview(self):

        self.dock = QDockWidget("File Graph", self)

        # 웹뷰 생성
        webview_frame = QFrame()
        webview_layout = QVBoxLayout(webview_frame)

        self.web_view_file_relation = QWebEngineView()
        self.web_view_file_relation.setMinimumWidth(400)
        self.web_view_file_relation.page().setBackgroundColor(QColor("#282c34"))
        webview_layout.addWidget(self.web_view_file_relation)

        self.dock.setWidget(webview_frame)

        # 도킹 가능한 영역을 좌우로 제한
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # 도킹 위젯의 기능 설정 (닫기, 이동, 부동 상태 가능)
        self.dock.setFeatures(QDockWidget.DockWidgetClosable |
                              QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetFloatable)

        # 도킹 위젯을 floating 상태로 설정
        # self.dock.setFloating(True)

        # 도킹 위젯을 메인 윈도우의 왼쪽에 추가
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        # self.dock.hide()


    def view_graph(self):

        if self.file_path:
            try:
                html, _, info = gen_pyvis_html(self.file_path)
                self.form_info.setText(f"{info}")
            except Exception as e:
                self.web_view.setHtml ("")
                # 에러 메시지 표시
                QMessageBox.critical(self, "Error", str(e))
                return

            self.setWindowTitle(f'{self.win_title} - {os.path.basename(self.file_path)}')
            self.web_view.setHtml (html)

            # with open("./pyvis_graph.html", mode='w', encoding='utf-8') as fp:
            #     fp.write(html)

            # # html 파일을 절대경로로 변경
            # abs_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyvis_graph.html")
            # HTML 파일을 웹뷰에 로드
            # self.web_view.setUrl(QUrl.fromLocalFile(abs_html))


    def view_only_graph(self):

        if self.work_dir:
            try:
                html_only_graph, _, _ = file_graph.gen_pyvis_html(self.work_dir, "./template_only_graph.html")
            except Exception as e:
                self.web_view_file_relation.setHtml("")
                # 에러 메시지 표시
                QMessageBox.critical(self, "Error", str(e))
                return

            self.web_view_file_relation.setHtml (html_only_graph)


    def select_xml_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "XML 파일 선택",
            "",
            "XML files (*.xml);;All files (*.*)"
        )

        self.view_graph()


    def apply_styles(self):
        # # 다크 테마 스타일 적용
        # self.setStyleSheet("""
        #     QMainWindow {
        #         background-color: #2b2b2b;
        #     }
        #     QFrame {
        #         background-color: #282c34;
        #         border-radius: 5px;
        #         padding: 10px;
        #         margin: 5px;
        #     }
        #     QWebEngineView {
        #         background-color: #282c34;
        #     }
        #     QPushButton {
        #         background-color: #0d6efd;
        #         color: white;
        #         border: none;
        #         padding: 8px;
        #         border-radius: 4px;
        #     }
        #     QPushButton:hover {
        #         background-color: #0b5ed7;
        #     }
        #     QLabel {
        #         color: #abb2bf;
        #         padding: 5px;
        #     }
        # """)
        pass


def main():
    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationVersion(__version__)

    # 메인 윈도우 생성 및 표시
    viewer = FormXmlViewerApp()
    viewer.showMaximized()
    apply_stylesheet(app, theme='dark_teal.xml')

    # 애플리케이션 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
