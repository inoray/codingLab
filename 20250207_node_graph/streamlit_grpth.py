import streamlit
from streamlit_agraph import agraph, Node, Edge, Config, TripleStore

nodes = []
edges = []
# node 를 정의하고
nodes.append( Node(id="Spiderman",
                   label="Peter Parker",
                   size=25,
                   shape="circularImage",
                   image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png")
            ) # includes **kwargs
nodes.append( Node(id="Captain_Marvel",
                   size=25,
                   shape="circularImage",
                   image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png")
            )
# edge 를 정의해서
edges.append( Edge(source="Captain_Marvel",
                   label="friend_of",
                   target="Spiderman",
                   # **kwargs
                   )
            )

# config 와 함께
config = Config(width=750,
                height=950,
                directed=True,
                physics=True,
                hierarchical=True,
                # **kwargs
                )

# graph 를 그리면 끝!
return_value = agraph(nodes=nodes,
                      edges=edges,
                      config=config)
