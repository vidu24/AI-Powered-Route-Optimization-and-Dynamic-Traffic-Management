import os
import hashlib
import osmnx as ox
import folium
import time
from folium.plugins import MiniMap, Fullscreen
from folium.plugins import BeautifyIcon
import matplotlib.pyplot as plt
from AlgoFile import *  # Your custom algorithms (Bidirectional_A_Star, etc.)s

ox.settings.overpass_max_query_area_size = 1000000000  # Increase Area limit

def Obtain_Coordinates():
    start = input("Enter the full name of location that you intend to start from: ")
    end = input("Enter the full name of your destination location: ")

    Start = ox.geocode(start)
    End = ox.geocode(end)  # Lat and Long
    return Start, End


def Graphing(Start, End):
    location_hash = hashlib.md5(f"{Start}".encode()).hexdigest()
    graph_file = f"graph_cache/{location_hash}.graphml"

    if not os.path.exists("graph_cache"):
        os.makedirs("graph_cache")

    if os.path.exists(graph_file):
        print("Loading cached graph...")
        graph = ox.load_graphml(graph_file)
    else:
        try:
            print("Downloading new graph data...")
            graph = ox.graph_from_point(Start, dist=3000, network_type="drive")
            ox.save_graphml(graph, graph_file)
        except Exception as e:
            print(f"Failed to get graph: {e}")
            exit()

    Start = ox.distance.nearest_nodes(graph, Start[1], Start[0])
    End = ox.distance.nearest_nodes(graph, End[1], End[0])

    return Start, End, graph


def Mapping(graph, paths_info, Start, End):
    m = folium.Map(
        location=(graph.nodes[Start]['y'], graph.nodes[Start]['x']),
        zoom_start=14,
        tiles='OpenStreetMap'
    )

    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)

    for path, name, color in paths_info:
        if not path:
            print(f"No path found for {name}.")
            continue

        route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path]
        distance_m = sum(graph.edges[path[i], path[i + 1], 0].get("length", 0) for i in range(len(path) - 1))
        distance_km = round(distance_m / 1000, 2)
        duration_min = round((distance_km / 50) * 60, 1)

        layer = folium.FeatureGroup(name=f"{name} ({distance_km} km / {duration_min} min)")
        folium.PolyLine(
            route_coords,
            color=color,
            weight=6,
            opacity=0.8,
            popup=f"{name} - {distance_km} km, ~{duration_min} min"
        ).add_to(layer)
        layer.add_to(m)

    # Markers
    folium.Marker(
        location=(graph.nodes[Start]['y'], graph.nodes[Start]['x']),
        popup="Start",
        icon=BeautifyIcon(icon_shape='marker', border_color='green', text_color='green', number=1)
    ).add_to(m)

    folium.Marker(
        location=(graph.nodes[End]['y'], graph.nodes[End]['x']),
        popup="End",
        icon=BeautifyIcon(icon_shape='marker', border_color='red', text_color='red', number=2)
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save("detailed_route_map.html")
    print("🗺 Map saved as detailed_route_map.html. Open it in a browser to view.")


def Matplotlib_Mapping(graph, path):
    """
    Plot the full route on the graph using matplotlib, without printing node IDs.
    """
    xs = [graph.nodes[n]['x'] for n in path]
    ys = [graph.nodes[n]['y'] for n in path]

    fig, ax = ox.plot_graph(graph, show=False, close=False, edge_color='lightgrey', node_size=0)

    ax.plot(xs, ys, linewidth=4, color='purple', zorder=2)
    ax.scatter(xs[0], ys[0], c='green', s=100, zorder=3, label='Start')
    ax.scatter(xs[-1], ys[-1], c='red', s=100, zorder=3, label='End')

    ax.legend()
    plt.title("Bidirectional A* Route")
    plt.show()


# --- MAIN SCRIPT ---

Area = input("Enter the City name along with country (Example: Dubai, UAE): ")
Org, Dest = Obtain_Coordinates()

if Org is None or Dest is None:
    exit(0)

print(f"Coordinates obtained: {Org} -> {Dest}")

Org_node, Dest_node, graph = Graphing(Org, Dest)
print("Bidirectional A*")
start_time = time.time()
Path1 = Bidirectional_A_Star_with_Traffic(Org_node, Dest_node, graph)
time_bi_astar = time.time() - start_time
print(f"Time taken: {round(time_bi_astar, 4)} seconds\n")

print("A*")
start_time = time.time()
Path2 = A_Star_with_traffic(Org_node, Dest_node, graph)
time_astar = time.time() - start_time
print(f"Time taken: {round(time_astar, 4)} seconds\n")

print("Dijkstra")
start_time = time.time()
Path3 = Djikstra_with_traffic(Org_node, Dest_node, graph)
time_dijkstra = time.time() - start_time
print(f"Time taken: {round(time_dijkstra, 4)} seconds\n")

paths_info = [
    (Path1, "Bidirectional A*", "blue"),
    (Path2, "A*", "orange"),
    (Path3, " Dijkstra", "purple")
]

Mapping(graph, paths_info, Org_node, Dest_node)
Matplotlib_Mapping(graph, Path3)