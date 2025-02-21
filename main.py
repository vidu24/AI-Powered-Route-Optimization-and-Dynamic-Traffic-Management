import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

def find_optimal_route(place_name, orig_coords, dest_coords):
   

    # 1️⃣ Download the street network (drivable roads)
    print(f"Fetching road network for {place_name}...")
    graph = ox.graph_from_place(place_name, network_type="drive")

    # 2️⃣ Find nearest nodes to the given coordinates
    print("Finding nearest nodes on the map...")
    orig_node = ox.distance.nearest_nodes(graph, X=orig_coords[1], Y=orig_coords[0])
    dest_node = ox.distance.nearest_nodes(graph, X=dest_coords[1], Y=dest_coords[0])

    # 3️⃣ Compute shortest path using Dijkstra's algorithm (based on distance)
    print("Computing shortest path using Dijkstra's algorithm...")
    shortest_path = nx.shortest_path(graph, source=orig_node, target=dest_node, weight="length")

    # 4️⃣ Visualize the route
    print("Plotting the optimal route...")
    fig, ax = ox.plot_graph_route(graph, shortest_path, route_linewidth=4, node_size=0, bgcolor="white")

    print("Route plotted successfully!")

# Example usage
place = "New York, USA"  # Change this to your desired location
start_coordinates = (40.748817, -73.985428)  # Empire State Building (lat, lon)
end_coordinates = (40.730610, -73.935242)  # Destination in NYC

find_optimal_route(place, start_coordinates, end_coordinates)
