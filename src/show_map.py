import osmnx as ox

print("Loading Gangtok road network...")

graph = ox.load_graphml("data/gangtok_roads.graphml")

print("Creating map...")

ox.plot.plot_graph(
    graph,
    node_size=0,
    edge_color="blue",
    edge_linewidth=0.8,
    show=True,
    close=True
)

print("Map displayed successfully!")