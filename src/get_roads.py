import osmnx as ox

print("Downloading Gangtok road network...")

place = "Gangtok, Sikkim, India"

graph = ox.graph.graph_from_place(
    place,
    network_type="drive"
)

print("Road network downloaded successfully!")
print(f"Number of road intersections: {len(graph.nodes)}")
print(f"Number of road segments: {len(graph.edges)}")

ox.io.save_graphml(graph, "data/gangtok_roads.graphml")

print("Road network saved to data/gangtok_roads.graphml")