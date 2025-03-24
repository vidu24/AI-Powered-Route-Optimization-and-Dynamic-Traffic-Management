import osmnx as ox
from AlgoFile import *

ox.settings.overpass_max_query_area_size = 1000000000  # Increase limit

def Obtain_Coordinates():
    while True:
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
        graph = ox.graph_from_place(Area, network_type="drive")
        Start = ox.distance.nearest_nodes(graph, Start[1], Start[0])
        End = ox.distance.nearest_nodes(graph, End[1], End[0])
        return Start, End, graph
    except Exception as e:
        print(f"Error in Graphing: {e}")
        exit(1)

def Mapping(graph, Path, Start, End):
    """Plots the graph with the route and distinguishes Start and End nodes."""

    node_colors = ["blue" if node not in [Start, End] else "green" if node == Start else "red" for node in graph.nodes]
    node_sizes = [0 if node not in [Start, End] else 200 for node in graph.nodes]  # Larger size for Start/End

    fig, ax = ox.plot_graph_route(
        graph, Path,
        route_linewidth=4,
        node_size=node_sizes,
        node_color=node_colors,
        bgcolor="white",
        route_color="purple",
        node_zorder=3
    )

# Get user input interactively
Area = input("Enter the City name along with country (Example: Dubai, UAE): ")
Org, Dest = Obtain_Coordinates()

# If start and end are the same, exit the program
if Org is None or Dest is None:
    exit(0)

print(f"Coordinates obtained: {Org} -> {Dest}")

# Create graph
Org, Dest, graph = Graphing(Org, Dest, Area)

# Run Dijkstra Algorithm
print("\nDijkstra Path:")
Path = Djikstra(Org, Dest, graph)
Mapping(graph, Path, Org, Dest)

# Run A* Algorithm
print("\nA* Path:")
Path2 = A_Star(Org, Dest, graph)
Mapping(graph, Path2, Org, Dest)