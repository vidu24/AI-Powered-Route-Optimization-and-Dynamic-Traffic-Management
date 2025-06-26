import heapq
import networkx as nx
from folium.plugins import BeautifyIcon, MiniMap, Fullscreen
import matplotlib.pyplot as plt
from scipy.spatial import distance  # Correct Euclidean distance function
import requests
from math import radians, cos, sin, asin, sqrt
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

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1 
    dlon = lon2 - lon1 

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    a = max(0, min(1, a))  # Clamp value to avoid domain error
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of Earth in km
    return c * r

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
    def heuristic(node):
        coord1 = (graph.nodes[node]['y'], graph.nodes[node]['x'])
        coord2 = (graph.nodes[End]['y'], graph.nodes[End]['x'])
        return haversine(coord1, coord2)

    open_set = [(heuristic(Start), 0, Start)]
    g_score = {Start: 0}
    f_score = {Start: heuristic(Start)}
    came_from = {}
    visited = set()

    while open_set:
        _, curr_cost, curr = heapq.heappop(open_set)
        if curr in visited:
            continue
        visited.add(curr)

        if curr == End:
            break

        for neighbor, edge_data in graph[curr].items():
            lat = (graph.nodes[curr]["y"] + graph.nodes[neighbor]["y"]) / 2
            lon = (graph.nodes[curr]["x"] + graph.nodes[neighbor]["x"]) / 2
            current_speed, _ = get_traffic_data(lat, lon)

            # Use best travel time across parallel edges
            best_time = float('inf')
            for _, attr in edge_data.items():
                if current_speed:
                    travel_time = attr["length"] / (current_speed * 1000 / 3600)
                else:
                    travel_time = attr["length"] / (50 * 1000 / 3600)
                best_time = min(best_time, travel_time)

            temp_g = g_score[curr] + best_time
            if temp_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = temp_g
                f = temp_g + heuristic(neighbor)
                f_score[neighbor] = f
                came_from[neighbor] = curr
                heapq.heappush(open_set, (f, temp_g, neighbor))

    return reconstruct_path(End, came_from, Start)


def Bidirectional_A_Star_with_Traffic(start, end, graph):
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
            lat = (graph.nodes[current_f]['y'] + graph.nodes[nbr]['y']) / 2
            lon = (graph.nodes[current_f]['x'] + graph.nodes[nbr]['x']) / 2
            current_speed, _ = get_traffic_data(lat, lon)

            edge_data = list(graph[current_f][nbr].values())[0]
            length = edge_data.get('length', 1)
            speed = current_speed if current_speed else 50
            travel_time = length / (speed * 1000 / 3600)

            tg = f_g[current_f] + travel_time
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
            lat = (graph.nodes[nbr]['y'] + graph.nodes[current_b]['y']) / 2
            lon = (graph.nodes[nbr]['x'] + graph.nodes[current_b]['x']) / 2
            current_speed, _ = get_traffic_data(lat, lon)

            edge_data = list(graph[nbr][current_b].values())[0]
            length = edge_data.get('length', 1)
            speed = current_speed if current_speed else 50
            travel_time = length / (speed * 1000 / 3600)

            tg = b_g[current_b] + travel_time
            if tg < b_g[nbr]:
                b_g[nbr] = tg
                b_pred[nbr] = current_b
                heapq.heappush(b_queue, (tg + heuristic(nbr, start), nbr))

    if meeting_node is None:
        return []

    # Reconstruct path from start to end via meeting_node
    path_forward = []
    node = meeting_node
    while node is not None:
        path_forward.append(node)
        node = f_pred[node]
    path_forward.reverse()

    path_backward = []
    node = b_pred[meeting_node]
    while node is not None:
        path_backward.append(node)
        node = b_pred[node]

    full_path = path_forward + path_backward
    return full_path


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

    return path[::-1]  # Reverse for correct order