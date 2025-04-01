# AI-Powered-Route-Optimization-and-Dynamic-Traffic-Management

i) Generic Function that'll create the adjacency matrix based on inputs provided in this format [Out_Node, Cost, In_Node].
ii) Make Two functions that'll work on the basic algos. that we intend to work on. That is the Djikstra's and A* along with whatever else we are working on. That is the essence of the program.
iii) Work on the selection of Start Point, End point on a map.
iv) Creation of the inputs and send to matrix.
v) It will work based on the Algorithms written.
vi) overlap the output on the map.

To present the Generic Graph, we can make use of the Graph-simulating libraries and work on that. 
Map things and all, I believe OSM is used, but the extent of it's viability & utility is unknown to me.

Date : 1/4/25

Code Explanation :

osmnx → Fetches map data (like roads) from OpenStreetMap (OSM) and performs route calculations.
networkx → Represents the road network as a graph (nodes = intersections, edges = roads).
import requests -> used to request data from the source
from dotenv import load_dotenv & import os -> used to load data/variables present in .env

.env File : File where we store important information like API Keys
.gitignore File : File names written inside this are ingnored by git while pushing into the repo

main.py :

-> Obtain Coordinates: Takes the Names of the Start Point & End Point respectively. It uses osmnx's geocode function which takes the Provided information and provided the Latitude & Longitude values of the points in the form of a 2 Tuple (Lat, Long). It returns the two 2-Tuple.
Avoids the error of Start and ending location being the same point

-> Graphing: Takes the Area that we are working with (provided in main by the user), as well as the 2-Tuple of the Start & End points. It takes the Area Label and using the osnmx's graph_from_place, provides us the graph taht consists of nodes which are intersections and edges which are roads.
The Graphing Function also returns the nearest node to the Start and End points. It's important to know that the approximation function, osmnx's distance.nearest_nodes Takes Longitude and Then Latitude. Returns the Graph, Start and End which are node IDs.

-> Mapping: It is where the Path on the Map is represented visually. It takes in the Graph, Path, Start and End, sets the sizes and colours of the Start & End Nodes as well as the Path. And using the osmnx's plot_graph_route (and it's various attribute values), we're able to obtain the visual represenatation of the map.

AlgoFile.py :

-> get_traffic_data : takes latitude and longitude as input and fetch real-time traffic flow data

-> `Dijkstra_with_traffic` algorithm extends the traditional Dijkstra’s approach by incorporating real-time traffic data to determine the fastest route between a start and destination point. Instead of relying solely on distance, it dynamically adjusts travel times based on live traffic speeds retrieved from the TomTom Traffic API.  

The algorithm maintains a priority queue to process nodes in order of increasing travel time, ensuring efficiency. As each node is explored, its neighboring edges are evaluated using real-time speed data. Travel time is calculated by dividing the road segment length by the current speed, with a default of 50 km/h used when live data is unavailable. If a newly computed travel time is shorter than a previously recorded one, updates are made, and the node is added to the queue for further processing.  

The process continues until the shortest-time path is found. The algorithm then reconstructs the optimal route using a predecessor dictionary, ensuring an adaptive and traffic-aware navigation solution.

-> `A*_with_traffic` algorithm is an optimized version of the classic A* search that incorporates real-time traffic data to determine the fastest route. Unlike traditional A*, which minimizes distance using a heuristic function, this implementation adjusts travel times dynamically based on live traffic speeds from the TomTom Traffic API.  

The algorithm maintains a priority queue where nodes are processed based on their total estimated cost (`F = G + H`). `G(n)` represents the actual travel time from the start node, while `H(n)` is a heuristic estimate of the remaining travel time, calculated using the Euclidean distance between the current node and the destination.  

As nodes are explored, live traffic data is fetched for the corresponding road segments, and travel time is computed by dividing the segment length by the current speed. If real-time data is unavailable, a default speed of 50 km/h is used. If the newly computed travel time to a neighboring node is shorter than previously recorded, the `G` value is updated, and the node is reinserted into the queue with an updated `F(n)`.  

The process continues until the destination node is reached, at which point the shortest-time path is reconstructed using the predecessor dictionary. By incorporating live traffic conditions, this approach ensures that routing decisions prioritize travel efficiency rather than just physical distance.

-> reconstruct_path: using the predecessor dictionary, we're able to track the nodes that we have traversed backwards, i.e., From End to start. The nodes are appended to a List and returned after reversal
