import re
import os
from pyvis.network import Network
import xml.etree.ElementTree as ET
from xml.dom  import minidom
import webview  # Python에서 지원하는 별도 브라우저 창을 위해 사용
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', default="./", help=' : form xml directory')
parser.add_argument('-t', '--template_path', default="./template_only_graph.html", help=' : template html file path')
parser.add_argument('--view_browser', action='store_true', help=' : view in browser')
args = parser.parse_args()

node_color = {
    "normal": "cornflowerblue",
    "wd": "#d2cb7f",
    "corr": "#008d62",
    "bad": "#e76a83",
    "dead": "#52fff8"
}

node_size = {
    "normal": 10,
    "bad": 15,
    "dead": 20
}


def set_node_attribute(net, edge_inout):
    """
    PyVis Network 객체의 노드 속성 설정

    Args:
        net (Network): Network 객체
        edge_inout (Dictionary): 각노드의 edge in/out 정보를 담은 딕셔너리
    """
    if edge_inout is None:
        return

    # print("set_node_attribute")
    # edge 정보를 바탕으로 out_edge와 in_edge 개수를 파악하여 색상과 크기 설정
    for node_id, inout in edge_inout.items():

        if "_dead_" in node_id:
            # dead node는 눈에 띄게 표시해 줘야 한다.
            color = node_color["bad"]
            size = node_size["dead"]

            node = net.get_node(node_id)
            node["color"] = color
            node["size"] = size
            node["origColor"] = color

        # print(f'node_id: {node_id}, in: {inout[0]}, out: {inout[1]}, color: {color}, size: {size}')


def get_root_tag(filename):
    # "start" 이벤트를 사용하면 첫 번째 시작 태그를 만나면 해당 태그를 얻을 수 있음
    for event, elem in ET.iterparse(filename, events=("start",)):
        # 첫 번째 이벤트에서 루트 태그를 반환하고, 더 이상 읽지 않음
        return elem.tag


def is_form_xml(xml_file):
    form_xml_tag_list = [
        "IzFormOcrXml",
        "CorrectionInfo",
        "IzFormWorkDefine",
        "IzFormInclude",
        "IzFormIdentificationRule"]

    try:
        root_tag = get_root_tag(xml_file)
    except Exception as e:
        # 예외 던지기
        raise Exception(f"XML 파일을 읽을 수 없습니다: {xml_file} : {e}")

    # print(f"root_tag: {root_tag}")
    if root_tag in form_xml_tag_list:
        return True
    else:
        return False


def get_xml_file_list(dir):
    """
    지정된 디렉토리 하위의 모든 xml 파일을 찾아 리스트를 반환한다.
    하위디렉토리를 모두 찾는다.

    Args:
        dir (_type_): _description_
    """
    import os

    xml_file_list = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".xml"):
                # 경로형태를 unix형태로 변경 "\\" -> "/"
                file_path = os.path.join(root, file).replace("\\", "/")
                if is_form_xml(file_path):
                    xml_file_list.append(file_path)

    return xml_file_list


def get_abs_path(root_dir, filename):
    # path의 상대경로 정보를 제거하고 절대경로로 변경
    if not os.path.isabs(filename):
        filename = os.path.abspath(os.path.join(root_dir, filename))
    filename = filename.replace("\\", "/")
    return filename


def get_value_list_from_xml(root, tagname, attrname = ""):
    """
    XML에서 tagname 태그의 attrname 속성값을 리스트로 반환
    """
    ret_list = []
    for elem in root.findall(tagname):
        if attrname == "":
            value = elem.text
        else:
            value = elem.get(attrname)
        if value is not None:
            ret_list.append(value)
    return ret_list


def get_link_list_from_form_ocr_xml(xml_dir, root):
    link_dict = {}

    link_list = get_value_list_from_xml(root, ".//Include", "xmlpath")
    link_list += get_value_list_from_xml(root, ".//IdentificationRule", "ruleXmlPath")

    for link in link_list:
        abs_path = get_abs_path(xml_dir, link)
        link_dict[abs_path] = 1

    return list(link_dict.keys())


def get_link_list_from_work_define_xml(xml_dir, root):
    link_dict = {}

    link_list = get_value_list_from_xml(root, ".//FormClassification//FormClassPath")
    link_list += get_value_list_from_xml(root, ".//FormRecog//FormPath")

    for link in link_list:
        abs_path = get_abs_path(xml_dir, link)
        link_dict[abs_path] = 1

    return list(link_dict.keys())


def get_link_list_from_include_xml(xml_dir, root):
    link_dict = {}

    link_list = get_value_list_from_xml(root, "FormPath")

    for link in link_list:
        abs_path = get_abs_path(xml_dir, link)
        link_dict[abs_path] = 1

    return list(link_dict.keys())


def add_edge_files(net, xml_file_list):
    edge_inout = {}
    for xml_file in xml_file_list:

        # XML 파일 읽기
        try:
            tree = ET.parse(xml_file)
        except Exception as e:
            continue

        link_list = []
        root = tree.getroot()
        xml_dir = os.path.dirname(xml_file)
        if root.tag in ["IzFormOcrXml", "IzFormIdentificationRule"]:
            link_list = get_link_list_from_form_ocr_xml(xml_dir, root)
        elif root.tag == "IzFormWorkDefine":
            link_list = get_link_list_from_work_define_xml(xml_dir, root)
        elif root.tag == "IzFormInclude":
            link_list = get_link_list_from_include_xml(xml_dir, root)

        for path_to in link_list:
            try:
                net.add_edge(xml_file, path_to)
            except Exception as e:
                dead_id = f"_dead_{path_to}"
                label = f"dead, {os.path.basename(path_to)}"
                net.add_node(n_id=dead_id, label=label, title=label)
                net.add_edge(xml_file, dead_id)
                path_to = dead_id

            edge_in = edge_inout.get(path_to, [0,0])
            edge_inout[path_to] = [edge_in[0] + 1, edge_in[1]]
            edge_out = edge_inout.get(xml_file, [0,0])
            edge_inout[xml_file] = [edge_out[0], edge_out[1] + 1]

    # net의 모든 노드 아이디 출력
    # print("add_edge_files")
    # for node_id in net.get_nodes():
    #     print(f'node_id: {node_id}')

    # edge_inout 출력
    # print("add_edge_files")
    # for node_id, inout in edge_inout.items():
    #     print(f'node_id: {node_id}, in: {inout[0]}, out: {inout[1]}')

    return edge_inout


def add_node_files(net, xml_file_list):
    # 파일을 노드로 추가
    xml_file_list_avail = []
    for xml_file in xml_file_list:
        basename = os.path.basename(xml_file)

        # XML 파일이 정상적으로 읽히는지 확인
        try:
            ET.parse(xml_file)
            xml_file_list_avail.append(xml_file)
            size = node_size["normal"]

            root_tag = get_root_tag(xml_file)
            if root_tag in ["IzFormWorkDefine", "IzFormInclude"]:
                color = node_color["wd"]
            elif root_tag == "CorrectionInfo":
                color = node_color["corr"]
            else:
                color = node_color["normal"]

        except Exception as e:
            color = node_color["bad"]
            size = node_size["bad"]

        # title은 xml_file를 사용. 한줄이 40개문자를 넘으면 줄바꿈을 넣어준다.
        if len(xml_file) > 40:
            title = re.sub(r"(.{40})", r"\1\n", xml_file, 0, re.DOTALL)

        net.add_node(n_id=xml_file, label=basename, title=title, color=color, size=size)

    return xml_file_list_avail


def gen_file_graph(dir):
    """
    XML 파일을 읽어 PyVis Network 객체를 생성하고 반환

    Args:
        xml_file (str): XML 파일 경로

    Returns:
       PyVis Network 객체
    """
    info = ""

    xml_file_list = get_xml_file_list(dir)
    # print(f"xml_file_list: {xml_file_list}")

    # PyVis Network 객체 생성 (directed=True로 화살표 표시)
    net = Network(height="800px", width="100%", directed=True, bgcolor="#222222", font_color="white")

    # 물리 시뮬레이션 옵션 설정: force-directed layout을 사용하여 연결된 노드는 가깝게, 비연결 노드는 멀리 배치
    net.barnes_hut(gravity=-3500, central_gravity=0.4, spring_length=95, spring_strength=0.04, damping=0.09)

    # 파일을 노드로 추가
    xml_file_list_avail = add_node_files(net, xml_file_list)

    # edge 추가. xml을 분석해서 edge를 추가한다.
    edge_inout = add_edge_files(net, xml_file_list_avail)

    set_node_attribute(net, edge_inout)
    return net, info


def gen_pyvis_html(dir, template_path = args.template_path):
    """
    PyVis Network 객체를 HTML로 변환

    Args:
        net (Network): Network 객체
        template_path (str): HTML 템플릿 파일 경로

    Returns:
        str: HTML 코드
    """

    net, info = gen_file_graph(dir)
    if template_path is not None and template_path != "":
        net.set_template(template_path)
    html = net.generate_html()

    return html, net, info


def show_in_browser(html, net):
    """
    브라우저에서 PyVis Network 객체를 시각화

    Args:
        net (Network): Network 객체
    """

    # 그래프를 HTML 파일로 생성하고 브라우저에서 열기
    with open("pyvis_graph.html", mode='w', encoding='utf-8') as fp:
        fp.write(html)
    # net.save_graph("pyvis_graph.html")
    net.show("pyvis_graph.html", notebook=False)


def show_in_webview(html):
    """
    웹뷰를 사용하여 PyVis Network 객체를 시각화

    Args:
        net (Network): Network 객체
    """
    webview.create_window("PyVis Network with XML Viewer", html=html, maximized=True)
    webview.start()


def main():

    # dir을 절대 경로로 변경
    abs_dir = os.path.abspath(args.dir)

    html, net, _ = gen_pyvis_html(abs_dir)

    if args.view_browser:
        show_in_browser(html, net)
    else:
        show_in_webview(html)


if __name__ == "__main__":
    main()
