import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

def Obtain_Coordinates():
    start = input("Enter the full name of location that you intend to start from: ")
    end = input("Enter the full name of your destination location: ")

    Start = ox.geocode(start)
    End = ox.geocode(end)  # Lat and Long
    return Start, End

def Graphing(Start, End, Area):
    graph = ox.graph_from_place(Area, network_type="drive")
    Start = ox.distance.nearest_nodes(graph, Start[1], Start[0])
    End = ox.distance.nearest_nodes(graph, End[1], End[0])

    return Start, End, graph

def Djikstra(Start, End, graph):
    distances = {node: float('inf') for node in graph.nodes}
    predecessors = {node: None for node in graph.nodes}
    distances[Start] = 0
    Queue = [(Start, 0)]

    while Queue:
        Curr, Curr_Distance = Queue.pop(0)

        if Curr == End:
            break

        neighbours = sorted(graph[Curr].items(), key=lambda item: item[0])

        for neighbor, edge_data in neighbours:
            for _, attributes in edge_data.items():
                length = attributes["length"] + Curr_Distance

                if distances[neighbor] > length:
                    distances[neighbor] = length
                    predecessors[neighbor] = Curr
                    Queue.append((neighbor, length))

    path = []
    node = End
    while node is not None:
        path.append(node)
        node = predecessors[node]

    path.reverse()
    return path if path[0] == Start else []  # Ensure a valid path

def A_Star(Start, End, graph):

    Queue = [(Start, 0)]
    predecessors = {Start: None}
    G = {node: float('inf') for node in graph.nodes}
    G[Start] = 0

    while Queue:
        Queue.sort(key=lambda x: x[1])
        current, _ = Queue.pop(0)

        if current == End:
            break

        for neighbor in graph.neighbors(current):
            edge_length = graph[current][neighbor][0]["length"]
            temp_G = G[current] + edge_length

            if temp_G < G[neighbor]:
                G[neighbor] = temp_G

                y1, x1 = graph.nodes[neighbor]['y'], graph.nodes[neighbor]['x']
                y2, x2 = graph.nodes[End]['y'], graph.nodes[End]['x']
                heuristic = ox.distance.euclidean(y1, x1, y2, x2)

                Val = temp_G + heuristic

                for i, (node, _) in enumerate(Queue):
                    if node == neighbor:
                        Queue[i] = (neighbor, Val)
                        break
                else:
                    Queue.append((neighbor, Val))

                predecessors[neighbor] = current

    path = []
    node = End
    while node is not None:
        path.append(node)
        node = predecessors.get(node)

    if path[-1] != Start:
        return []

    path.reverse()
    return path


def Mapping(graph, Path, Start, End):
    node_colors = ["blue" if node not in [Start, End] else "red" for node in graph.nodes]
    fig, ax = ox.plot_graph_route(graph, Path, route_linewidth=4, node_size=1,node_color=node_colors, bgcolor="white", route_color="purple")

Area = input("Enter the City name along with country (Example: Dubai, UAE): ")
Org, Dest = Obtain_Coordinates()
print(Org, Dest)

Org, Dest, graph = Graphing(Org, Dest, Area)
print("Djikstra")
Path = Djikstra(Org, Dest, graph)
Mapping(graph, Path, Org, Dest)
print("A*")
Path2 = A_Star(Org, Dest, graph)
Mapping(graph, Path2, Org, Dest)
