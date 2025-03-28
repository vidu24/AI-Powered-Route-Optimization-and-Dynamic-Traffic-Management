# AI-Powered-Route-Optimization-and-Dynamic-Traffic-Management

i) Generic Function that'll create the adjacency matrix based on inputs provided in this format [Out_Node, Cost, In_Node].
ii) Make Two functions that'll work on the basic algos. that we intend to work on. That is the Djikstra's and A* along with whatever else we are working on. That is the essence of the program.
iii) Work on the selection of Start Point, End point on a map.
iv) Creation of the inputs and send to matrix.
v) It will work based on the Algorithms written.
vi) overlap the output on the map.

To present the Generic Graph, we can make use of the Graph-simulating libraries and work on that. 
Map things and all, I believe OSM is used, but the extent of it's viability & utility is unknown to me.

Date : 24/3/25

Code Explanation :

osmnx → Fetches map data (like roads) from OpenStreetMap (OSM) and performs route calculations.
networkx → Represents the road network as a graph (nodes = intersections, edges = roads).

Obtain Coordinates: Takes the Names of the Start Point & End Point respectively. It uses osmnx's geocode function which takes the Provided information and provided the Latitude & Longitude values of the points in the form of a 2 Tuple (Lat, Long). It returns the two 2-Tuple.
Avoids the error of Start and ending location being the same point

Graphing: Takes the Area that we are working with (provided in main by the user), as well as the 2-Tuple of the Start & End points. It takes the Area Label and using the osnmx's graph_from_place, provides us the graph taht consists of nodes which are intersections and edges which are roads.
The Graphing Function also returns the nearest node to the Start and End points. It's important to know that the approximation function, osmnx's distance.nearest_nodes Takes Longitude and Then Latitude. Returns the Graph, Start and End which are node IDs.

Djikstra: It is the classic Djikstra's Algorithm implemented and fitted according to the needs of this particular program.It has within it, initialized Queue, holding updating distances from Start, and the Node itself, predecessor dictionary, helping us trace the path that we have traversed, distances Dictionary, that keeps track of our Distances, initialized with all values set to infinity, and Start's to 0.

It runs as long as Queue has some contituents within it and/or End not found. It pops an item, and if End is found, ends the program.Else, produces the neighbouring nodes (graph[Curr].items()) and their respective distances (attributes["length"]) from the start, by adding the (Current_Node -> Child_Node) Distance and distance traversed thus far.If the new distance to the Child_node is lesser compared to its original computed distance.The value is updated in the distance dictionary. As it is updated, it is also appended to the Queue.It is important to mention that the Queue used is a Priority Queue, thus, as is the process of Djikstra, the lowest distance is popped out first for computation.It uses the reconstruct_path function to produce path by sending in the Start, End and Predecessor Dictionary

A*: Similar to Djikstra, this is the Classic A* Algorithm that has been implemented to fit the needs of the current program. It, as Djikstra, takes a Queue, prodecessor & distance (relabled to G) dictionaries. The distances are all intiialized to infinity, and distance from Start -> Start is set to 0.

The Program runs as long as Queue has some constituents within it and/or End not found. It pops an item, and if End is found, ends the program.
Else, it produces neighbouring nodes (graph.neighbors(current)), finds distance using [graph.get_edge_data(current, neighbor, default={})] and the attribute "length".The distance data is then used to calculate the G(n) value by adding the length of the edge along with the G[current].
If the calculated value is lesser than the value in G dictionary, it is updated, and obtaining (Lat, Long) tuples of node in focus and End, we're able to calculate the H(n) using distance.euclidean.This is then added to the Calculated G(n) value to produce the heurisitic, which along with the node is added to the Queue.It is important to mention that the Queue used is a Priority Queue, thus, as is the process of A*, the lowest F(n) is popped out first for computation.It uses the reconstruct_path function to produce path by sending in the Start, End and Predecessor Dictionary.

reconstruct_path: using the predecessor dictionary, we're able to track the nodes that we have traversed backwards, i.e., From End to start. The nodes are appended to a List and returned after reversal

Mapping: It is where the Path on the Map is represented visually. It takes in the Graph, Path, Start and End, sets the sizes and colours of the Start & End Nodes as well as the Path. And using the osmnx's plot_graph_route (and it's various attribute values), we're able to obtain the visual represenatation of the map.