import random
import networkx as nx
import pickle

with open('./segments.pkl', mode='rb') as file:
    segments = pickle.load(file).sort_index()

with open('./node_segments.pkl', mode='rb') as file:
    node_segments = pickle.load(file).sort_index()


class Routing:
    def __init__(self, parking_database, city_map):
        self.parking_database = parking_database
        self.city_map = city_map

    def get_segment_from_id(self, segment_id):
        return segments.loc[segment_id]

    def get_route_from_start_to_end(self, start_node, end_node):
        try:
            route = nx.shortest_path(self.city_map.G, start_node, end_node, 'length')
            return route
        except nx.exception.NetworkXNoPath:
            return []

    def get_random_segment(self):
        return segments.sample(n=1).iloc[0]

    def create_nodes_for_random_parking_spot_searching(self, start_node, random_turns=3):
        current_node = start_node
        random_nodes = [start_node]

        for turn in range(random_turns):
            neighbors = self.city_map.get_neighbors_of_node(current_node)
            valid_neighbors = [node for node in neighbors if node not in self.city_map.get_dead_end_nodes()]
            if current_node in valid_neighbors:
                valid_neighbors.remove(current_node)

            if len(valid_neighbors) == 0:
                continue

            selected_node = random.sample(valid_neighbors, 1)[0]
            # TODO: check for empty

            random_nodes.append(selected_node)
            current_node = selected_node

        going_back_route = self.get_route_from_start_to_end(current_node, start_node)

        all_nodes = random_nodes + going_back_route

        return all_nodes

    def get_all_segments_for_nodes(self, nodes):
        all_segments_in_route = []

        for start_node, end_node in zip(nodes, nodes[1:]):
            try:
                # TODO: when not existent routes are selected
                current_segments = node_segments.loc[start_node, end_node].values
                all_segments_in_route += current_segments[0][0]
            except Exception:
                pass

        return all_segments_in_route

    def get_next_node_to_segment(self, segment_id):
        return segments.loc[segment_id]['route_ending_node']

    def find_empty_parking_spot_recursively(self, nodes, checked_nodes, depth = 0):
        if not self.parking_database.is_any_parking_spot_empty() or depth > 15:
            return self.parking_database.get_random_spot()  # FIXME

        spots = self.parking_database.get_empty_spots_from_ways_around_nodes(nodes)

        if len(spots.index) == 0:
            new_nodes = []
            for node in nodes:
                new_nodes += self.city_map.get_neighbors_of_node(node)

            not_checked_new_nodes = [node for node in new_nodes if node not in checked_nodes]
            return self.find_empty_parking_spot_recursively(not_checked_new_nodes,
                                                            checked_nodes + not_checked_new_nodes, depth=depth+1)

        # TODO now we randomly select a parking spot in a nearby road, could be improved to find by distance
        return spots.sample(n=1).iloc[0]

    def get_segments_between_segment_and_end_node(self, segment_id):
        current_segment = self.get_segment_from_id(segment_id)
        segments_in_current_road = \
        node_segments.loc[current_segment['route_starting_node'], current_segment['route_ending_node']].values[0][0]

        if segment_id not in segments_in_current_road:
            return []

        return segments_in_current_road[:segments_in_current_road.index(segment_id) + 1]

    def get_segments_in_route_to_parking_spot(self, current_segment_id, parking_spot):
        current_segment = self.get_segment_from_id(current_segment_id)
        start_node = current_segment['route_starting_node']
        current_end_node = current_segment['route_ending_node']
        end_node = parking_spot['route_starting_node']
        route = self.get_route_from_start_to_end(current_end_node, end_node)
        middle_segments = self.get_all_segments_for_nodes(route)

        segments_in_current_road = node_segments.loc[start_node, current_end_node].values[0][0]

        # TODO: debug this part, current segment should be always in the list
        if current_segment.name not in segments_in_current_road:
            return middle_segments

        segments_to_start_node = segments_in_current_road[segments_in_current_road.index(current_segment.name):]

        segments_in_end_node = \
            node_segments.loc[parking_spot['route_starting_node'], parking_spot['route_ending_node']].values[0][0]

        if parking_spot['segment_id'] not in segments_in_end_node:
            return middle_segments

        segments_to_end_node = segments_in_end_node[:segments_in_end_node.index(parking_spot['segment_id']) + 1]

        return segments_to_start_node + middle_segments + segments_to_end_node

    def get_segments_in_route_to_node(self, current_segment_id, destination_node):
        start_node = self.get_next_node_to_segment(current_segment_id)
        route = self.get_route_from_start_to_end(start_node, destination_node)
        route_segments = self.get_all_segments_for_nodes(route)

        segments_until_start_node = self.get_segments_between_segment_and_end_node(current_segment_id)

        return segments_until_start_node + route_segments
