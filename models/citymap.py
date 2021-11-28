import osmnx as ox


class CityMap:
    def __init__(self, target_area):
        self.G = ox.graph_from_place(target_area, network_type='drive')
        nodes, streets = ox.graph_to_gdfs(self.G)
        self.nodes = nodes
        self.streets = streets

        self.dead_end_nodes = list(nodes[nodes['street_count'] == 1].index)

    def get_neighbors_of_node(self, node):
        neighbors = list(self.G.neighbors(node))
        return neighbors

    def get_dead_end_nodes(self):
        return self.dead_end_nodes

    def get_random_destination_node(self):
        return self.nodes[~self.nodes.index.isin(self.dead_end_nodes)].sample(n=1).index.astype(int)[0]
