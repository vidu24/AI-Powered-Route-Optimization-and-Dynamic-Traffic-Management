import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import heapq

def dijkstra(graph, source, target, weight='length'):
    # Initialize the priority queue
    queue = [(0, source)]
    distances = {node: float('inf') for node in graph.nodes}
    distances[source] = 0
    predecessors = {node: None for node in graph.nodes}

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == target:
            break

        for neighbor, attributes in graph[current_node].items():
            distance = current_distance + attributes.get(weight, 1)
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Reconstruct the shortest path
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()
    return path

def a_star(graph, source, target, weight='length'):
    # Initialize the priority queue
    queue = [(0, source)]
    distances = {node: float('inf') for node in graph.nodes}
    distances[source] = 0
    predecessors = {node: None for node in graph.nodes}
    heuristic = lambda u, v: nx.shortest_path_length(graph, u, v, weight=weight)

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == target:
            break

        for neighbor, attributes in graph[current_node].items():
            distance = current_distance + attributes.get(weight, 1)
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (distance + heuristic(neighbor, target), neighbor))

    # Reconstruct the shortest path
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()
    return path

def find_optimal_route(place_name, orig_coords, dest_coords, algorithm='dijkstra'):
    # 1️⃣ Download the street network (drivable roads)
    print(f"Fetching road network for {place_name}...")
    graph = ox.graph_from_place(place_name, network_type="drive")

    # 2️⃣ Find nearest nodes to the given coordinates
    print("Finding nearest nodes on the map...")
    orig_node = ox.distance.nearest_nodes(graph, X=orig_coords[1], Y=orig_coords[0])
    dest_node = ox.distance.nearest_nodes(graph, X=dest_coords[1], Y=dest_coords[0])

    # 3️⃣ Compute shortest path using the specified algorithm
    print(f"Computing shortest path using {algorithm} algorithm...")
    if algorithm == 'dijkstra':
        shortest_path = dijkstra(graph, orig_node, dest_node, weight="length")
    elif algorithm == 'a_star':
        shortest_path = a_star(graph, orig_node, dest_node, weight="length")
    else:
        raise ValueError("Unsupported algorithm. Use 'dijkstra' or 'a_star'.")

    # 4️⃣ Visualize the route
    print("Plotting the optimal route...")
    fig, ax = ox.plot_graph_route(graph, shortest_path, route_linewidth=4, node_size=0, bgcolor="white")

    print("Route plotted successfully!")

# Example usage
place = "Surat, India"  # Change this to your desired location
start_coordinates = (21.2030, 72.8377)  # Starting coordinates in Surat (lat, lon)
end_coordinates = (21.1173, 72.7405)  # Destination coordinates in Surat (lat, lon)

find_optimal_route(place, start_coordinates, end_coordinates, algorithm='dijkstra')