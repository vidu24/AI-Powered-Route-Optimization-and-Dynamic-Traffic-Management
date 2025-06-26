import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from haversine import haversine
import heapq

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

def Bidirectional_A_Star(start, end, graph):
    """
    Bidirectional A* on a directed graph. Returns a list of node IDs for the route,
    or an empty list if no valid directed path exists.
    """
    rev_graph = graph.reverse(copy=False)

    def heuristic(n1, n2):
        y1, x1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
        y2, x2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']
        return haversine((y1, x1), (y2, x2))

    f_queue = [(0, start)]
    b_queue = [(0, end)]

    f_g = {node: float('inf') for node in graph.nodes}
    b_g = {node: float('inf') for node in graph.nodes}
    f_g[start] = 0
    b_g[end] = 0

    f_pred = {start: None}
    b_pred = {end: None}

    visited_f, visited_b = set(), set()
    meeting_node = None

    while f_queue and b_queue:
        _, current_f = heapq.heappop(f_queue)
        visited_f.add(current_f)
        if current_f in visited_b:
            meeting_node = current_f
            break
        for nbr in graph.neighbors(current_f):
            data = list(graph[current_f][nbr].values())[0]
            length = data.get('length', 1)
            tg = f_g[current_f] + length
            if tg < f_g[nbr]:
                f_g[nbr] = tg
                f_pred[nbr] = current_f
                heapq.heappush(f_queue, (tg + heuristic(nbr, end), nbr))

        _, current_b = heapq.heappop(b_queue)
        visited_b.add(current_b)
        if current_b in visited_f:
            meeting_node = current_b
            break
        for nbr in rev_graph.neighbors(current_b):
            data = list(graph[nbr][current_b].values())[0]
            length = data.get('length', 1)
            tg = b_g[current_b] + length
            if tg < b_g[nbr]:
                b_g[nbr] = tg
                b_pred[nbr] = current_b
                heapq.heappush(b_queue, (tg + heuristic(nbr, start), nbr))

    if meeting_node is None:
        return []

    # Reconstruct forward (start->meeting)
    path_fwd, node = [], meeting_node
    while node is not None:
        path_fwd.append(node)
        node = f_pred.get(node)
    path_fwd.reverse()

    # Reconstruct backward (meeting->end)
    path_bwd, node = [], end
    while node is not None:
        path_bwd.append(node)
        if node == meeting_node:
            break
        node = b_pred.get(node)
    path_bwd.reverse()
    path_bwd = path_bwd[1:]

    full_path = path_fwd + path_bwd

    for u, v in zip(full_path, full_path[1:]):
        if not graph.has_edge(u, v):
            return []

    return full_path

def Mapping(graph, path):
    """
    Plot the full route on the graph using matplotlib, without printing node IDs.
    """
    xs = [graph.nodes[n]['x'] for n in path]
    ys = [graph.nodes[n]['y'] for n in path]

    fig, ax = ox.plot_graph(graph, show=False, close=False, edge_color='lightgrey', node_size=0)

    ax.plot(xs, ys, linewidth=4, color='purple', zorder=2)

    ax.scatter(xs[0], ys[0], c='green', s=100, zorder=3, label='Start')
    ax.scatter(xs[-1], ys[-1], c='red', s=100, zorder=3, label='End')

    ax.legend()
    plt.show()


if __name__ == "__main__":
    Area = input("Enter the City name along with country (e.g. 'Surat, India'): ")
    Start_coords, End_coords = Obtain_Coordinates()
    org, dest, G = Graphing(Start_coords, End_coords, Area)

    path = Bidirectional_A_Star(org, dest, G)
    if path:
        Mapping(G, path)
    else:
        print("No route is present between the specified points.")

# print("Djikstra")
# Path = Djikstra(Org, Dest, graph)
# if not Path:
#     print("No route found using Dijkstra")
# else:
#     Mapping(graph, Path, Org, Dest)

# print("A*")
# Path2 = A_Star(Org, Dest, graph)
# if not Path2:
#     print("No route found using A*")
# else:
#     Mapping(graph, Path2, Org, Dest)

"""

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

"""