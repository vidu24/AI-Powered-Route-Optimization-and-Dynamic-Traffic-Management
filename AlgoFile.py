import heapq
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance  # Correct Euclidean distance function
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

def get_traffic_data(lat, lon):
    """Fetch real-time traffic flow data from TomTom API."""
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={TOMTOM_API_KEY}&point={lat},{lon}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data["flowSegmentData"]["currentSpeed"], data["flowSegmentData"]["freeFlowSpeed"]
    else:
        return None, None  # Return None if no traffic data is available

def Djikstra_with_traffic(Start, End, graph):
    """Finds the shortest time-based path using Dijkstra’s Algorithm with on-demand traffic data."""
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
                # Fetch traffic data only when the edge is explored
                lat = (graph.nodes[Curr]["y"] + graph.nodes[neighbor]["y"]) / 2
                lon = (graph.nodes[Curr]["x"] + graph.nodes[neighbor]["x"]) / 2

                current_speed, _ = get_traffic_data(lat, lon)
                
                # Use traffic data for the edge's travel time
                if current_speed:
                    travel_time = attributes["length"] / (current_speed * 1000 / 3600)  # Convert speed from km/h to m/s
                else:
                    travel_time = attributes["length"] / (50 * 1000 / 3600)  # Default speed: 50 km/h

                time_cost = travel_time + Curr_Distance

                if distances[neighbor] > time_cost:
                    distances[neighbor] = time_cost
                    predecessors[neighbor] = Curr
                    heapq.heappush(Queue, (time_cost, neighbor))

    return reconstruct_path(End, predecessors, Start)

def A_Star_with_traffic(Start, End, graph):
    """Finds the shortest time-based path using A* Search Algorithm with on-demand traffic data."""
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

            # Fetch traffic data for the edge being considered
            lat = (graph.nodes[current]["y"] + graph.nodes[neighbor]["y"]) / 2
            lon = (graph.nodes[current]["x"] + graph.nodes[neighbor]["x"]) / 2
            current_speed, _ = get_traffic_data(lat, lon)

            # Use traffic data to calculate travel time
            if current_speed:
                edge_length = edge_length / (current_speed * 1000 / 3600)  # Convert speed from km/h to m/s

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