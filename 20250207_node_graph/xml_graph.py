from pyvis.network import Network
import xml.etree.ElementTree as ET
from xml.dom  import minidom
import webview  # Python에서 지원하는 별도 브라우저 창을 위해 사용
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-x', '--xml_path', default="F0100010101_householdRegister.xml", help=' : form xml file path')
parser.add_argument('-t', '--template_path', default="./template.html", help=' : template html file path')
parser.add_argument('--view_browser', action='store_true', help=' : view in browser')
args = parser.parse_args()

node_color = {
    "elem_start": "#d2cb7f",
    "elem": "cornflowerblue",
    "field_enabled": "#e76a83",
    "field_disabled": "#6e3741"
}

node_size = {
    "elem": 10,
    "field": 15
}


def get_out_field_id(form_data, form_data_id):
    out_field_id = []
    if form_data is not None:
        for block in form_data:
            if block.tag != "OutBlock":
                continue

            for field in block:
                field_idnumber = field.get("idNumber")
                if field_idnumber is None:
                    continue

                out_id = f"{form_data_id}_out_{field_idnumber}"
                out_field_id.append(out_id)

    return out_field_id


def add_edge_element(net, form_data, form_data_id):

    region_tag_list = ["SearchRegionInfo", "UnitRegionSet", "FirstCellRegionSet"]

    # edge_inout 초기화. 노드 id를 key로 하고, [in_edge 개수, out_edge 개수]를 value로 함
    edge_inout = {}

    for elem in form_data:
        if elem.tag != "Element":
            continue

        elem_id = elem.get('id')
        if elem_id is None:
            continue

        net_elem_id = f"{form_data_id}_elem_{elem_id}"

        # fromUnit의 OutBlock을 찾아서 OutField로 연결
        form_unit = elem.find("FormUnit")
        if form_unit is not None:
            out_field_id = get_out_field_id(form_unit, net_elem_id)
            for field_id in out_field_id:
                net.add_edge(net_elem_id, field_id, arrows="to")

        if edge_inout.get(net_elem_id) is None:
            edge_inout[net_elem_id] = [0, 0]

        for region_tag in region_tag_list:
            region_info = elem.find(region_tag)
            if region_info is not None:
                break

        if region_info is None:
            continue

        for bp in region_info.findall(".//BasePosition[@baseElementId]"):
            base_id = bp.get('baseElementId')
            if base_id is None:
                continue

            base_id = f"{form_data_id}_elem_{base_id}"
            net.add_edge(net_elem_id, base_id, arrows="to")

            edge_in = edge_inout.get(base_id, [0,0])
            edge_inout[base_id] = [edge_in[0] + 1, edge_in[1]]
            edge_out = edge_inout.get(net_elem_id, [0,0])
            edge_inout[net_elem_id] = [edge_out[0], edge_out[1] + 1]

    # print("add_edge_element")
    # for node_id, inout in edge_inout.items():
    #     print(f'node_id: {node_id}, in: {inout[0]}, out: {inout[1]}')

    return edge_inout


def set_node_attribute(net, edge_inout):

    # print("set_node_attribute")
    # edge 정보를 바탕으로 out_edge와 in_edge 개수를 파악하여 색상과 크기 설정
    for node_id, inout in edge_inout.items():

        if "_out_" in node_id:
            continue

        color = node_color["elem_start"] if inout[1] == 0 else node_color["elem"]
        size = node_size["elem"] + inout[0] * 5

        node = net.get_node(node_id)
        node["color"] = color
        node["size"] = size
        node["origColor"] = color

        # print(f'node_id: {node_id}, in: {inout[0]}, out: {inout[1]}, color: {color}, size: {size}')


def prettyxml(raw_xml):
    raw_xml = raw_xml.replace("\t", "").replace("\n", "").replace("\r", "")

    try:
        pretty_xml = minidom.parseString(raw_xml).toprettyxml(indent="  ", newl="\r", encoding="utf-8").decode('utf-8')
    except Exception:
        pretty_xml = raw_xml

    return pretty_xml


def add_node_as_element(net, form_data, form_data_id):
    """
    PyVis Network 객체에 Element 노드 추가

    Args:
        net (Network): Network 객체
        elem_id (str): Element id
        elem (Element): Element 객체
        elements (dict): 각 Element의 id를 key로 하는 딕셔너리
    """

    edge_inout = {}

    for elem in form_data:
        if elem.tag != "Element":
            continue

        elem_id = elem.get('id')
        if elem_id is None:
            return

        net_elem_id = f"{form_data_id}_elem_{elem_id}"  # FormData id와 Element id를 합침

        form_unit = elem.find("FormUnit")
        if form_unit is not None:
            edge_inout_form_unit = gen_form_data_graph(net, form_unit, net_elem_id)
            edge_inout.update(edge_inout_form_unit)

        # 각 노드의 label에 id와 Name을 함께 표시
        # 만약 <Name> 태그가 존재하면 그 텍스트를 가져오고, 없으면 id만 사용합니다.
        node_label = f"elem {elem_id}"
        name_elem = elem.find("Name")
        if name_elem is not None and name_elem.text is not None:
            node_label = node_label + f": {name_elem.text.strip()}"

        # 해당 노드의 XML 코드를 pretty print
        raw_xml = ET.tostring(elem, encoding='utf-8').decode('utf-8')
        pretty_xml = prettyxml(raw_xml)

        net.add_node(n_id=net_elem_id, label=node_label, title=pretty_xml)

    edge_inout_cur = add_edge_element(net, form_data, form_data_id)
    edge_inout.update(edge_inout_cur)
    return edge_inout


def add_node_as_outfield(net, form_data, form_data_id):

    for block in form_data:
        if block.tag != "OutBlock":
            continue

        for field in block:
            field_idnumber = field.get("idNumber")
            field_name = field.get("name")
            disabled = field.get("disabled", "false").lower()  # "true" 또는 "false"

            # 노드 id는 "out_" 접두어를 붙여 Element 노드와 구분
            out_id = f"{form_data_id}_out_{field_idnumber}"
            label = f"field {field_idnumber}: {field_name}"

            # disabled 여부에 따라 색상 결정
            color = node_color["field_disabled"] if disabled == "true" else node_color["field_enabled"]
            size = node_size["field"]  # 기본 OutField 크기

            # Field 노드의 XML 내용을 title로 사용 (pretty print)
            raw_field_xml = ET.tostring(field, encoding='utf-8').decode('utf-8')
            pretty_field_xml = prettyxml(raw_field_xml)

            net.add_node(n_id=out_id, label=label, title=pretty_field_xml,
                        color=color, size=size, origColor=color)

            # OutField 내의 모든 <ElementId>에 대해 엣지 추가 (OutField → 해당 Element)
            for elem_id_tag in field.findall("ElementId"):
                target_id = elem_id_tag.text.strip()
                target_id = f"{form_data_id}_elem_{target_id}"
                # 엣지를 추가 (화살표는 Element 노드 방향)
                net.add_edge(out_id, target_id, arrows="to")


def gen_form_data_graph(net, form_data, form_data_id):
    """
    Form Data XML을 읽어 PyVis Network 객체를 생성하고 반환

    Args:
        form_data (Element): Form Data XML Element
        form_data_id (str): Form Data id

    Returns:
        PyVis Network 객체
    """
    # Element 노드 추가
    edge_inout = add_node_as_element(net, form_data, form_data_id)

    # OutField 노드 추가
    add_node_as_outfield(net, form_data, form_data_id)

    return edge_inout


def gen_graph_from_xml(xml_file):
    """
    XML 파일을 읽어 PyVis Network 객체를 생성하고 반환

    Args:
        xml_file (str): XML 파일 경로

    Returns:
       PyVis Network 객체
    """

    # XML 파일 읽기
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # PyVis Network 객체 생성 (directed=True로 화살표 표시)
    net = Network(height="800px", width="100%", directed=True, bgcolor="#222222", font_color="white")

    # 물리 시뮬레이션 옵션 설정: force-directed layout을 사용하여 연결된 노드는 가깝게, 비연결 노드는 멀리 배치
    net.barnes_hut(gravity=-3500, central_gravity=0.4, spring_length=95, spring_strength=0.04, damping=0.09)

    # 모든 <Element> 태그를 id 기준으로 저장 (key: id, value: Element 객체)
    edge_inout = {}
    for form_data in root.iter('FormData'):
        form_data_id = form_data.get('id')
        edge_inout_cur = gen_form_data_graph(net, form_data, form_data_id)
        edge_inout.update(edge_inout_cur)

    set_node_attribute(net, edge_inout)
    return net


def gen_pyvis_html(xml_file):
    """
    PyVis Network 객체를 HTML로 변환

    Args:
        net (Network): Network 객체
        template_path (str): HTML 템플릿 파일 경로

    Returns:
        str: HTML 코드
    """
    net = gen_graph_from_xml(xml_file)
    net.set_template(args.template_path)
    # net.show_buttons(filter_=['physics'])  # 물리 시뮬레이션 버튼만 표시
    html = net.generate_html()

    return html, net


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

    html, net = gen_pyvis_html(args.xml_path)

    if args.view_browser:
        show_in_browser(html, net)
    else:
        show_in_webview(html)


if __name__ == "__main__":
    main()
