import heapq
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance  # Correct Euclidean distance function

def Djikstra(Start, End, graph):
    """Finds the shortest path using Dijkstra’s Algorithm."""
    distances = {node: float('inf') for node in graph.nodes}
    predecessors = {node: None for node in graph.nodes}
    distances[Start] = 0
    Queue = [(0, Start)]  # Min-heap priority queue

    while Queue:
        Curr_Distance, Curr = heapq.heappop(Queue)  # Get node with smallest cost

        if Curr == End:
            break

        for neighbor, edge_data in graph[Curr].items():
            for _, attributes in edge_data.items():
                length = attributes.get("length", 1) + Curr_Distance

                if distances[neighbor] > length:
                    distances[neighbor] = length
                    predecessors[neighbor] = Curr
                    heapq.heappush(Queue, (distances[neighbor], neighbor))  # Corrected priority queue

    return reconstruct_path(End, predecessors, Start)

def A_Star(Start, End, graph):
    """Finds the shortest path using A* Search Algorithm."""
    queue = [(0, Start)]
    predecessors = {Start: None}
    G = {node: float('inf') for node in graph.nodes}
    G[Start] = 0

    while queue:
        current_cost, current = heapq.heappop(queue)

        if current == End:
            break

        for neighbor in graph.neighbors(current):
            edge_data = graph.get_edge_data(current, neighbor, default={})
            edge_length = min(edge.get("length", 1) for edge in edge_data.values()) if edge_data else 1

            temp_G = G[current] + edge_length

            if temp_G < G[neighbor]:
                G[neighbor] = temp_G
                x1, y1 = graph.nodes[neighbor]['x'], graph.nodes[neighbor]['y']
                x2, y2 = graph.nodes[End]['x'], graph.nodes[End]['y']
                heuristic = distance.euclidean((y1, x1), (y2, x2))  # Correct function

                total_cost = temp_G + heuristic
                heapq.heappush(queue, (total_cost, neighbor))
                predecessors[neighbor] = current

    return reconstruct_path(End, predecessors, Start)

def reconstruct_path(End, predecessors, Start):
    """Reconstructs the path from Start to End using predecessors."""
    if End not in predecessors or predecessors[End] is None:
        print("No valid path found between the locations.")
        return []

    path = []
    node = End
    while node is not None:
        path.append(node)
        node = predecessors.get(node)

    return path[::-1]  # Reverse for correct order