import heapq
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance  # Correct Euclidean distance function

def Djikstra(Start, End, graph): # Updated according to traffic data
    """Finds the shortest time-based path using Dijkstra’s Algorithm."""
    distances = {node: float('inf') for node in graph.nodes}
    predecessors = {node: None for node in graph.nodes}
    distances[Start] = 0
    Queue = [(0, Start)]

    while Queue:
        Curr_Distance, Curr = heapq.heappop(Queue)

        if Curr == End:
            break

        for neighbor, edge_data in graph[Curr].items():
            for _, attributes in edge_data.items():
                time_cost = attributes.get("travel_time", attributes.get("length", 1)) + Curr_Distance

                if distances[neighbor] > time_cost:
                    distances[neighbor] = time_cost
                    predecessors[neighbor] = Curr
                    heapq.heappush(Queue, (time_cost, neighbor))

    return reconstruct_path(End, predecessors, Start)

def A_Star(Start, End, graph): # Updated according to traffic data
    """Finds the shortest time-based path using A* Search Algorithm."""
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
            edge_length = min(edge.get("travel_time", edge.get("length", 1)) for edge in edge_data.values()) if edge_data else 1

            temp_G = G[current] + edge_length

            if temp_G < G[neighbor]:
                G[neighbor] = temp_G
                x1, y1 = graph.nodes[neighbor]['x'], graph.nodes[neighbor]['y']
                x2, y2 = graph.nodes[End]['x'], graph.nodes[End]['y']
                heuristic = distance.euclidean((y1, x1), (y2, x2))

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