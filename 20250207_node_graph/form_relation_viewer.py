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
                            QTextEdit, QDockWidget, QStatusBar)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, QDir, QSettings
from PySide6.QtGui import QIcon, QColor, QAction

from qt_material import apply_stylesheet

__version__ = "0.1.0"

class FormXmlViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.win_title = f"Form Xml Relation Viewer v{QApplication.applicationVersion()}"
        # 기본 webview html 파일 경로. 표시데이터가 없을 때 보여주는 화면
        self.template_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_dummy.html")
        self.info_file_graph = ""

        # QSettings 초기화: 첫번째 인자는 조직 이름, 두번째는 애플리케이션 이름입니다.
        self.settings = QSettings("Inzisoft", "FormRelationViewer")
        # 이전에 저장된 작업 디렉토리와 파일 경로 불러오기 (기본값 지정 가능)
        self.work_dir = self.settings.value("workDir", QDir.currentPath())
        self.file_path = self.settings.value("lastFile", None)

        self.setWindowTitle(self.win_title)
        self.setWindowIcon(QIcon('./icon/title_icon.svg'))
        self.setGeometry(100, 100, 1200, 800)

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

        # 상태바 생성
        self.create_status_bar()

        # 스타일 설정
        self.apply_styles()

        self.view_graph()
        self.view_only_graph()


    def load_folder(self):
        # QFileDialog를 사용하여 폴더 선택
        folder_path = QFileDialog.getExistingDirectory(self, "폴더 선택", self.work_dir)
        if folder_path:
            self.tree_view.setRootIndex(self.model.index(folder_path))
            self.dir_label.setText(folder_path)
            self.work_dir = folder_path
            # self.web_view.setHtml ("")
            self.web_view.setUrl(QUrl.fromLocalFile(self.template_html))
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
            f"<p>Copyright © 2025 Inzisoft</p>"
            f"<p>All rights reserved.</p>"
            f"<p>서식xml의 연결 관계정보를 보여주는 프로그램입니다.</p>"
            f"<p>Version: {__version__}</p>"
            f"<p>개발자: shkim</p>"
        )
        QMessageBox.about(self, "About Form Xml Relation Viewer", about_text)


    def create_status_bar(self):

        # 상태바에 버전 정보 표시
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


        # 컨테이너 위젯 생성 (progress_label과 margin을 담을 컨테이너)
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # 컨테이너의 내부 여백 제거
        container_layout.setSpacing(0)  # 위젯 간 간격 제거

        # 상태바 우측에 진행률 표시를 위한 레이블 생성
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignRight)

        # 여백을 위한 빈 레이블 생성
        self.margin_label = QLabel()
        self.margin_label.setFixedWidth(20)  # 20픽셀 여백

        # 컨테이너에 위젯 추가
        container_layout.addWidget(self.progress_label)
        container_layout.addWidget(self.margin_label)

        # 상태바에 컨테이너 추가
        self.statusBar().addPermanentWidget(container)


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
        self.dir_label.setFixedHeight(30)
        self.dir_label.setToolTip(self.work_dir)
        self.sidebar_layout.addWidget(self.dir_label)

        # 사이드 바로 사용할 QTreeView 생성
        self.create_treeview()

        # 여백을 위한 스트레치
        # self.sidebar_layout.addStretch()

        self.form_info = QTextEdit()
        self.form_info.setReadOnly(True)
        self.sidebar_layout.addWidget(self.form_info, 3)

        self.layout.addWidget(sidebar)


    def create_treeview(self):

        # 사이드 바로 사용할 QTreeView 생성
        self.tree_view = QTreeView()
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sidebar_layout.addWidget(self.tree_view, 7)

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
        self.dock.hide()

        # 로딩 진행상황 시그널 연결
        self.web_view_file_relation.loadStarted.connect(self.loading_started)
        self.web_view_file_relation.loadProgress.connect(self.loading_progress)
        self.web_view_file_relation.loadFinished.connect(self.loading_finished)


    def loading_started(self):
        self.progress_label.setText("XML 파일 분석 시작...")


    def loading_progress(self, progress):
        self.progress_label.setText(f"XML 파일 분석 중... {progress}%")


    def loading_finished(self, success):
        if success:
            # self.progress_label.setText(f"XML 파일 분석 완료")
            self.progress_label.setText(self.info_file_graph)
        else:
            self.progress_label.setText(f"XML 파일 분석 실패")

    def view_graph(self):

        if self.file_path and os.path.exists(self.file_path):
            try:
                html, _, info = gen_pyvis_html(self.file_path)
                self.form_info.setText(f"{info}")
            except Exception as e:
                # self.web_view.setHtml ("")
                self.web_view.setUrl(QUrl.fromLocalFile(self.template_html))
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
        else:
            # dummy HTML 파일을 웹뷰에 로드
            self.web_view.setUrl(QUrl.fromLocalFile(self.template_html))


    def view_only_graph(self):

        if self.work_dir:
            self.info_file_graph = ""
            try:
                html_only_graph, _, info = file_graph.gen_pyvis_html(self.work_dir, "./template_only_graph.html")
            except Exception as e:
                self.web_view_file_relation.setHtml("")
                QMessageBox.critical(self, "Error", str(e))
                return

            self.web_view_file_relation.setHtml (html_only_graph)
            self.info_file_graph = info


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


    def closeEvent(self, event):
        # 프로그램 종료 전 현재 작업 디렉토리와 파일 경로 저장
        self.settings.setValue("workDir", self.work_dir)
        self.settings.setValue("lastFile", self.file_path)
        event.accept()


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
