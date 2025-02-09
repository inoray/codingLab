from xml_graph import *
# ===============================================
# NiceGUI를 이용한 GUI 생성
# ===============================================

from nicegui import ui


def on_file_upload(files):
    """
    업로드된 파일의 내용을 읽어 JSON 데이터를 파싱한 후,
    networkx 그래프를 생성하고, pyvis로 HTML을 생성하여 iframe의 src를 갱신합니다.
    """
    if not files:
        return
    file = files[0]

    html, _ = gen_pyvis_html(file)


    # iframe의 src 속성을 업데이트합니다.
    # ui.element('iframe')로 생성한 요소는 props()를 이용하여 속성을 설정할 수 있습니다.
    graph_iframe.props(f'src="{html}" sandbox')
    ui.notify("그래프가 업데이트되었습니다.")

# 파일 업로드 위젯 생성 (JSON 파일만 허용)
upload_component = ui.upload(on_upload=on_file_upload, label="form xml 파일 선택", multiple=False).props("accept=.xml")
# 별도의 버튼을 눌러 파일 선택 창을 띄웁니다.
ui.button("파일 열기", on_click=lambda: upload_component.run_method("pickFiles"))


# ui.iframe 대신 ui.element('iframe')를 사용하여 iframe 요소를 생성합니다.
# classes()와 style()을 이용해 크기를 지정합니다.
graph_iframe = ui.element('iframe').props('src="" sandbox').classes('w-full').style('height: 800px;')

ui.run(title="NiceGUI Graph", dark=True, reload=False, native=True)  # 브라우저 자동 실행 비활성화
