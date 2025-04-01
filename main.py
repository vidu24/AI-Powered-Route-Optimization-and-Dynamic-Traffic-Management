import osmnx as ox
from AlgoFile import *

ox.settings.overpass_max_query_area_size = 1000000000  # Increase Area limit

def Obtain_Coordinates():
    while True: # runs until valid coordinates are obtained
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
        graph = ox.graph_from_place(Area, network_type="drive") # Fetch path/road where driving is allowed/possible
        # Convert coordinates to nearest nodes in the graph
        Start = ox.distance.nearest_nodes(graph, Start[1], Start[0])
        End = ox.distance.nearest_nodes(graph, End[1], End[0])
        return Start, End, graph
    except Exception as e:
        print(f"Error in Graphing: {e}")
        exit(1)

# def update_graph_with_traffic(graph):
#     """Update graph edge weights with real-time traffic data."""
#     for u, v, key, data in graph.edges(keys=True, data=True):
#         lat = (graph.nodes[u]["y"] + graph.nodes[v]["y"]) / 2
#         lon = (graph.nodes[u]["x"] + graph.nodes[v]["x"]) / 2

#         # Fetch traffic data from TomTom API
#         current_speed, free_flow_speed = get_traffic_data(lat, lon)

#         # Calculate travel time based on current speed from traffic data
#         if current_speed:
#             travel_time = data["length"] / (current_speed * 1000 / 3600)  # Convert speed from km/h to m/s
#             data["travel_time"] = travel_time
#         else:
#             data["travel_time"] = data["length"] / (50 * 1000 / 3600)  # Default speed: 50 km/h
#     return graph

def Mapping(graph, Path, Start, End):
    """Plots the graph with the route and distinguishes Start and End nodes."""

    node_colors = ["blue" if node not in [Start, End] else "green" if node == Start else "red" for node in graph.nodes] # Color nodes based on their type
    node_sizes = [0 if node not in [Start, End] else 200 for node in graph.nodes]  # Larger size for Start/End

    fig, ax = ox.plot_graph_route( # plotting the graph (map) with the route
        graph, Path,
        route_linewidth=4,
        node_size=node_sizes,
        node_color=node_colors,
        bgcolor="white",
        route_color="purple",
        node_zorder=3
    )

# Get user input interactively
Area = input("Enter the City name along with country (Example: Dubai, UAE): ") # Smaller Area is suggested for faster response
Org, Dest = Obtain_Coordinates()

# If start and end are the same, exit the program
if Org is None or Dest is None:
    exit(0)

print(f"Coordinates obtained: {Org} -> {Dest}")

# Create graph
Org, Dest, graph = Graphing(Org, Dest, Area)

# Algorithms:
# print("\nDijkstra Path with Traffic:")
# Path = Djikstra_with_traffic(Org, Dest, graph)
# Mapping(graph, Path, Org, Dest)

print("\nA* Path with Traffic:")
Path2 = A_Star_with_traffic(Org, Dest, graph)
Mapping(graph, Path2, Org, Dest)