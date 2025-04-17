# algofile:
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance  # Correct Euclidean distance function
import requests
from dotenv import load_dotenv
import os
import random

load_dotenv()  # Load environment variables from .env file
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

def get_traffic_data(lat, lon):
    """Fetch real-time traffic flow data from TomTom API."""
    if not TOMTOM_API_KEY:
        print("TOMTOM_API_KEY not found in environment variables.")
        return None, None

    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={TOMTOM_API_KEY}&point={lat},{lon}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Add error checking for empty or missing flowSegmentData
        if ("flowSegmentData" in data and 
            isinstance(data["flowSegmentData"], list) and 
            len(data["flowSegmentData"]) > 0):
            segment = data["flowSegmentData"][0]
            return segment.get("currentSpeed"), segment.get("freeFlowSpeed")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching traffic data: {e}")
        return None, None
    
def calculate_travel_time(length, speed_kmh):
    """Calculates travel time in seconds given length in meters and speed in km/h."""
    if speed_kmh is not None and speed_kmh > 0:
        return length / (speed_kmh * 1000 / 3600)
    else:
        return length / (50 * 1000 / 3600)  # Default speed: 50 km/h

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
                travel_time = calculate_travel_time(attributes["length"], current_speed)

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
            edge_length_meters = min(edge.get("length", 1) for edge in edge_data.values()) if edge_data else 1

            # Fetch traffic data for the edge being considered
            lat = (graph.nodes[current]["y"] + graph.nodes[neighbor]["y"]) / 2
            lon = (graph.nodes[current]["x"] + graph.nodes[neighbor]["x"]) / 2
            current_speed, _ = get_traffic_data(lat, lon)
            travel_time = calculate_travel_time(edge_length_meters, current_speed)

            temp_G = G[current] + travel_time

            if temp_G < G[neighbor]:
                G[neighbor] = temp_G
                x1, y1 = graph.nodes[neighbor]['x'], graph.nodes[neighbor]['y']
                x2, y2 = graph.nodes[End]['x'], graph.nodes[End]['y']
                heuristic = distance.euclidean((y1, x1), (y2, x2)) / (80 * 1000 / 3600) # Heuristic in time (assuming max speed of 80 km/h)

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

def reinforcement_learning_top_k(Start, End, graph, k=3, episodes=100, alpha=0.1, gamma=0.9, epsilon=0.2):
    """Finds the top k routes using a simple Reinforcement Learning (Q-learning) approach."""
    q_table = {}  # Q-table: (state, action) -> Q-value
    history = []

    def get_q_value(state, action):
        return q_table.get((state, action), 0.0)

    def choose_action(state, possible_actions):
        if random.random() < epsilon:
            return random.choice(list(possible_actions))  # Explore
        else:
            q_values = {action: get_q_value(state, action) for action in possible_actions}
            max_q = max(q_values.values()) if q_values else 0
            best_actions = [action for action, q in q_values.items() if q == max_q]
            return random.choice(best_actions) if best_actions else random.choice(list(possible_actions))

    def get_reward(current_node, next_node):
        edge_data = graph.get_edge_data(current_node, next_node, default={})
        length = min(edge.get("length", 1) for edge in edge_data.values()) if edge_data else 1
        # Fetch traffic data for reward (negative travel time)
        lat = (graph.nodes[current_node]["y"] + graph.nodes[next_node]["y"]) / 2
        lon = (graph.nodes[current_node]["x"] + graph.nodes[next_node]["x"]) / 2
        current_speed, _ = get_traffic_data(lat, lon)
        travel_time = calculate_travel_time(length, current_speed)
        return -travel_time  # Negative reward as we want to minimize time

    for episode in range(episodes):
        current_node = Start
        path = [current_node]
        total_reward = 0
        visited = set()

        while current_node != End and current_node not in visited:
            visited.add(current_node)
            possible_neighbors = list(graph.neighbors(current_node))
            if not possible_neighbors:
                break

            action = choose_action(current_node, possible_neighbors)
            next_node = action
            reward = get_reward(current_node, next_node)
            total_reward += reward
            path.append(next_node)

            # Update Q-value
            old_q = get_q_value(current_node, next_node)
            next_max_q = max([get_q_value(next_node, next_action) for next_action in graph.neighbors(next_node)]) if list(graph.neighbors(next_node)) else 0
            new_q = old_q + alpha * (reward + gamma * next_max_q - old_q)
            q_table[(current_node, next_node)] = new_q
            current_node = next_node

        if current_node == End:
            history.append((total_reward, tuple(path)))

    # Get top k paths based on total reward (higher reward = lower negative travel time = better path)
    sorted_history = sorted(history, key=lambda item: item[0], reverse=True)
    top_k_paths = []
    seen_paths = set()
    for reward, path_tuple in sorted_history:
        if path_tuple not in seen_paths:
            top_k_paths.append((-reward, list(path_tuple))) # Store negative reward as cost (time)
            seen_paths.add(path_tuple)
            if len(top_k_paths) >= k:
                break

    return top_k_paths