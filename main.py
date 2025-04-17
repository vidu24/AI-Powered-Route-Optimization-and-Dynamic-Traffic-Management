# main file:

import osmnx as ox
from AlgoFile import *
import time

ox.settings.overpass_max_query_area_size = 1000000000  # Increase Area limit

def Obtain_Coordinates():
    while True:  # runs until valid coordinates are obtained
        try:
            start = input("Enter the full name of the location you intend to start from: ")
            end = input("Enter the full name of your destination location: ")

            if start.lower() == end.lower():
                print("Start and End locations are the same.")
                return None, None

            Start = ox.geocode(start)
            End = ox.geocode(end)  # Convert to (latitude, longitude)
            return Start, End
        except Exception as e:
            print(f"Error: {e}. Please enter a valid location.")

def Graphing(Start, End, Area):
    """Fetches road network graph and finds the nearest nodes for start & end locations."""
    try:
        graph = ox.graph_from_place(Area, network_type="drive")  # Fetch path/road where driving is allowed/possible
        # Convert coordinates to nearest nodes in the graph
        start_node = ox.distance.nearest_nodes(graph, Start[1], Start[0])
        end_node = ox.distance.nearest_nodes(graph, End[1], End[0])
        return start_node, end_node, graph
    except Exception as e:
        print(f"Error in Graphing: {e}")
        exit(1)

def Mapping(graph, paths, start_node, end_node, colors):
    """Plots the graph with multiple routes and distinguishes Start and End nodes."""
    node_colors = ["blue" if node not in [start_node, end_node] else "green" if node == start_node else "red" for node in graph.nodes]  # Color nodes based on their type
    node_sizes = [0 if node not in [start_node, end_node] else 200 for node in graph.nodes]   # Larger size for Start/End

    fig, ax = ox.plot_graph_routes(  # plotting multiple routes
        graph, paths,
        route_linewidth=4,
        node_size=node_sizes,
        node_color=node_colors,
        bgcolor="white",
        route_colors=colors,
        node_zorder=3,
        show=False,
        close=False,
        save=False,
        filepath="route_map.png",
        dpi=300
    )
    plt.title("Top 3 Routes")
    plt.legend(["Rank 1", "Rank 2", "Rank 3", "Start", "End"])
    plt.show()


# Get user input interactively
Area = input("Enter the City name along with country (Example: Surat, India): ")  # Smaller Area is suggested for faster response
Org, Dest = Obtain_Coordinates()

# If start and end are the same, exit the program
if Org is None or Dest is None:
    exit(0)

print(f"Coordinates obtained: {Org} -> {Dest}")

# Create graph
Start_node, End_node, graph = Graphing(Org, Dest, Area)

# Algorithms:
print("\nDijkstra Path with Traffic:")
start_time = time.time()
dijkstra_path = Djikstra_with_traffic(Start_node, End_node, graph)
end_time = time.time()
dijkstra_time = end_time - start_time
print(f"Dijkstra Path: {dijkstra_path}, Time: {dijkstra_time:.4f} seconds")

print("\nA* Path with Traffic:")
start_time = time.time()
astar_path = A_Star_with_traffic(Start_node, End_node, graph)
end_time = time.time()
astar_time = end_time - start_time
print(f"A* Path: {astar_path}, Time: {astar_time:.4f} seconds")

print("\nReinforcement Learning - Finding Top 3 Routes (This might take time):")
start_time = time.time()
top_3_rl_paths = reinforcement_learning_top_k(Start_node, End_node, graph, k=3)
end_time = time.time()
rl_time = end_time - start_time
print(f"Top 3 RL Paths: {top_3_rl_paths}, Time: {rl_time:.4f} seconds")

if top_3_rl_paths:
    all_paths = [dijkstra_path, astar_path] + [path for cost, path in top_3_rl_paths]
    costs = [dijkstra_time, astar_time] + [cost for cost, path in top_3_rl_paths]
    sorted_paths_with_costs = sorted(zip(costs, all_paths), key=lambda item: item[0])
    top_3_display_paths = [path for cost, path in sorted_paths_with_costs[:3]]
    path_colors = ["red", "green", "blue"]  # Rank 1, 2, 3
    Mapping(graph, top_3_display_paths, Start_node, End_node, path_colors)
    print("\nRoute Ranking (based on estimated travel time):")
    for i, (cost, path) in enumerate(sorted_paths_with_costs[:3]):
        color_name = ["Red", "Green", "Blue"][i]
        algorithm_source = ""
        if path == dijkstra_path:
            algorithm_source = "(Dijkstra)"
        elif path == astar_path:
            algorithm_source = "(A*)"
        else:
            algorithm_source = "(RL - Rank {})".format(top_3_rl_paths.index((cost, path)) + 1)
        print(f"Rank {i+1} (Color: {color_name}): {algorithm_source} - Estimated Time: {cost:.4f} seconds")
else:
    Mapping(graph, [dijkstra_path, astar_path], Start_node, End_node, ["red", "green"])
    print("\nRoute Ranking (Dijkstra - Red, A* - Green):")
    print(f"Dijkstra Estimated Time: {dijkstra_time:.4f} seconds (Red)")
    print(f"A* Estimated Time: {astar_time:.4f} seconds (Green)")