import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import heapq
from geopy.distance import geodesic

def dijkstra(graph, source, target, weight='length'):
    queue = [(0, source)]
    distances = {node: float('inf') for node in graph.nodes}
    distances[source] = 0
    predecessors = {node: None for node in graph.nodes}

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node == target:
            break

        for neighbor, edge_data in graph[current_node].items():
            for _, attributes in edge_data.items():
                distance = current_distance + attributes.get(weight, 1)
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

    path = []
    node = target
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()
    return path

def heuristic(node1, node2, graph):
    lat1, lon1 = graph.nodes[node1]['y'], graph.nodes[node1]['x']
    lat2, lon2 = graph.nodes[node2]['y'], graph.nodes[node2]['x']
    return geodesic((lat1, lon1), (lat2, lon2)).meters  # Approximate heuristic

def a_star(graph, source, target, weight='length'):
    queue = [(0, source)]
    distances = {node: float('inf') for node in graph.nodes}
    distances[source] = 0
    predecessors = {node: None for node in graph.nodes}

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node == target:
            break

        for neighbor, edge_data in graph[current_node].items():
            for _, attributes in edge_data.items():
                distance = current_distance + attributes.get(weight, 1)
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(queue, (distance + heuristic(neighbor, target, graph), neighbor))

    path = []
    node = target
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()
    return path

def find_optimal_route(place_name, orig_coords, dest_coords, algorithm='dijkstra'):
    print(f"Fetching road network for {place_name}...")
    graph = ox.graph_from_place(place_name, network_type="drive")

    print("Finding nearest nodes on the map...")
    orig_node = ox.distance.nearest_nodes(graph, X=orig_coords[1], Y=orig_coords[0])
    dest_node = ox.distance.nearest_nodes(graph, X=dest_coords[1], Y=dest_coords[0])

    if orig_node is None or dest_node is None:
        raise ValueError("Start or destination node not found. Try adjusting coordinates.")

    print(f"Computing shortest path using {algorithm} algorithm...")
    if algorithm == 'dijkstra':
        shortest_path = dijkstra(graph, orig_node, dest_node, weight="length")
    elif algorithm == 'a_star':
        shortest_path = a_star(graph, orig_node, dest_node, weight="length")
    else:
        raise ValueError("Unsupported algorithm. Use 'dijkstra' or 'a_star'.")

    print("Plotting the optimal route...")
    fig, ax = ox.plot_graph_route(graph, shortest_path, route_linewidth=4, node_size=0, bgcolor="white")
    print("Route plotted successfully!")

# Example usage
place = "Surat, India"
start_coordinates = (21.2030, 72.8377)
end_coordinates = (21.1173, 72.7405)

find_optimal_route(place, start_coordinates, end_coordinates, algorithm='dijkstra')



"""

In the provided code, `geopy` is specifically used within the `heuristic` function of the A* algorithm. Here's why:

**Purpose of `geopy` in the `heuristic` function:**

* **Estimating Distance:**
    * The A* algorithm requires a heuristic function to estimate the distance between a current node and the target node.
    * The `heuristic` function aims to provide an *underestimation* of the remaining distance, which helps the algorithm efficiently explore the graph.
    * `geopy.distance.geodesic` calculates the geodesic distance (the shortest distance between two points on the Earth's surface) using latitude and longitude coordinates.
    * This provides a reasonable and relatively accurate estimate of the straight-line distance between two nodes, which is then used as the heuristic value.
* **Working with Geographic Coordinates:**
    * OSMnx graphs store node positions as latitude and longitude coordinates.
    * `geopy` is designed to work with these geographic coordinates, making it convenient for calculating distances on the Earth's surface.
* **Improved A* Performance:**
    * By providing a more accurate heuristic (compared to, say, a simple Euclidean distance calculation), `geopy` helps the A* algorithm make better decisions about which nodes to explore first. This can lead to faster convergence to the optimal path.

**Why not just use Euclidean distance?**

* While Euclidean distance could be used, it wouldn't accurately reflect distances on the Earth's curved surface, especially over longer distances.
* Geodesic distance takes the earths curvature into account.
* For shorter distances the difference is minimal, but for longer distances, the geodesic distance is much more accurate.

**In summary:**

`geopy` is used to provide a geographically accurate heuristic estimate in the A* algorithm, improving its performance by guiding it towards the target node more efficiently.


"""
