from pyvis.network import Network
import xml.etree.ElementTree as ET
from xml.dom import minidom
import networkx as nx

# XML 파일 경로 (예: "input.xml")
xml_file = "F0100010101_householdRegister.xml"

# XML 파일 읽기
tree = ET.parse(xml_file)
root = tree.getroot()

# 모든 <Element> 태그를 id 기준으로 저장 (key: id, value: Element 객체)
elements = {}
for elem in root.iter('Element'):
    elem_id = elem.get('id')
    if elem_id:
        elements[elem_id] = elem

# NetworkX DiGraph 구성
G = nx.DiGraph()
for elem_id in elements.keys():
    G.add_node(elem_id)
# 관계 구성: 각 Element 내부의 BasePosition 태그의 baseElementId가 있다면,
# "자식 -> 부모" 방향으로 edge를 추가 (화살표가 부모 방향, 즉 타겟에 표시됨)
for elem in elements.values():
    for bp in elem.findall(".//BasePosition[@baseElementId]"):
        base_id = bp.get('baseElementId')
        if base_id and base_id in elements:
            # 자식에서 부모로 edge 추가
            G.add_edge(elem.get('id'), base_id)

# PyVis Network 객체 생성 (directed=True로 화살표 표시)
net = Network(height="800px", width="100%", directed=True, bgcolor="#222222", font_color="white")

# 물리 시뮬레이션 옵션 설정: force-directed layout을 사용하여 연결된 노드는 가깝게, 비연결 노드는 멀리 배치
net.barnes_hut(gravity=-2500, central_gravity=0.7, spring_length=95, spring_strength=0.04, damping=0.09)

# NetworkX 그래프(G)를 PyVis에 추가하면서, 각 노드의 title 속성에 들여쓰기 적용된 XML 코드를 저장
for node in G.nodes():
    # 해당 노드의 XML 코드를 pretty print
    raw_xml = ET.tostring(elements[node], encoding='unicode')
    # try:
    #     pretty_xml = minidom.parseString(raw_xml).toprettyxml(indent="    ")
    # except Exception:
    pretty_xml = raw_xml
    net.add_node(n_id=node, label=node, title=pretty_xml, color="cornflowerblue")

# PyVis에 edge 추가 (화살표는 'to' 옵션 사용)
for source, target in G.edges():
    net.add_edge(source, target, arrows="to")

net.show_buttons(filter_=['physics'])  # 물리 시뮬레이션 버튼만 표시

# 커스텀 HTML 템플릿 설정:
# - 그래프 영역(div id="mynetwork")와 정보 영역(div id="info")를 별도로 생성하여,
#   노드를 클릭하면 JS 이벤트로 해당 노드의 title(XML 코드)을 표시함.
template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>PyVis Network Graph</title>
  <style type="text/css">
    body { font-family: sans-serif; }
    #mynetwork { width: 100%; height: 600px; border: 1px solid lightgray; }
    #info { width: 100%; height: 200px; border: 1px solid lightgray; white-space: pre-wrap; margin-top: 10px; }
  </style>
  <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
  <link href="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.css" rel="stylesheet" type="text/css" />
</head>
<body>
<div id="mynetwork"></div>
<div id="info">노드를 클릭하면 XML 코드가 표시됩니다.</div>
<script type="text/javascript">
  var nodes = new vis.DataSet({{ nodes }});
  var edges = new vis.DataSet({{ edges }});
  var container = document.getElementById("mynetwork");
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = {{ options }};
  var network = new vis.Network(container, data, options);
  network.on("click", function(params) {
    if (params.nodes.length > 0) {
      var nodeId = params.nodes[0];
      var nodeData = nodes.get(nodeId);
      document.getElementById("info").innerText = nodeData.title;
    }
  });
</script>
</body>
</html>
"""

# net.set_template(template)
# net.set_template_dir("./", "template.html")

# net.path = None  # 템플릿 로딩 시 기본 파일 참조를 막기 위해

# 그래프를 HTML 파일로 생성하고 브라우저에서 열기
net.show("pyvis_graph.html", notebook=False)
