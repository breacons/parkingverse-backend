import json
from enum import Enum
import random

from models.analyticsDatabase import AnalyticsDatabase
from models.parkingDatabase import ParkingDatabase
from models.citymap import CityMap
from models.routing import Routing

arriving_distance = 5  # the driver can look for parking spots already before arriving to the destination


class TravellingState(Enum):
    TRAVELLING = 'TRAVELLING'
    SEARCHING_FOR_PARKING = 'SEARCHING_FOR_PARKING'
    PARKING = 'PARKING'


class Vehicle:
    uuid = None
    has_sensor = False  # random prob
    # has_sensor = True  # random prob
    travelling_state = TravellingState.TRAVELLING
    current_destination = None
    current_route = []  # list of segments
    current_segment = None
    parking_spot = None

    steps_looking_for_parking = 0
    remaining_parking_time = None

    def __init__(self, uuid, parking_database: ParkingDatabase, city_map: CityMap, routing: Routing,
                 analytics: AnalyticsDatabase, sensor_ratio):
        self.uuid = uuid
        self.parking_database = parking_database
        self.routing = routing
        self.city_map = city_map
        self.analytics = analytics
        self.has_sensor = random.random() < sensor_ratio

        start_segment = self.routing.get_random_segment()

        self.current_route = self.create_random_destination(start_segment.name)

    def create_random_destination(self, current_segment_id):
        destination_node = self.city_map.get_random_destination_node()
        self.current_destination = destination_node

        if self.has_sensor:
            selected_parking_spot = self.routing.find_empty_parking_spot_recursively([destination_node], [])
            planned_route = self.routing.get_segments_in_route_to_parking_spot(current_segment_id,
                                                                               selected_parking_spot)
            return planned_route
        else:
            planned_route = self.routing.get_segments_in_route_to_node(current_segment_id, destination_node)
            return planned_route

    def to_json(self):
        current_segment = None

        if self.travelling_state != TravellingState.PARKING and len(self.current_route) > 0:
            current_segment = self.current_route[0]

        if not current_segment:
            return None

        return {
            current_segment: {'state': self.travelling_state.value, 'has_sensor': self.has_sensor}
        }

    def step(self):
        # print(self.travelling_state)
        # print(self.current_route)

        # if self.current_segment is None:
        #     raise ValueError(f'Vehicle {self.uuid} is without segment.')

        if self.travelling_state == TravellingState.PARKING:
            self.remaining_parking_time -= 1

            if self.remaining_parking_time == 0:
                self.leave_from_spot()

        elif self.travelling_state == TravellingState.TRAVELLING:
            if len(self.current_route) == 1:
                print('Empty route while travelling')
                # need new route
                pass

            if len(self.current_route) <= arriving_distance:
                self.travelling_state = TravellingState.SEARCHING_FOR_PARKING

            self.check_parking_spots()
            self.current_route = self.current_route[1:]

        elif self.travelling_state == TravellingState.SEARCHING_FOR_PARKING:
            self.steps_looking_for_parking += 1
            if len(self.current_route) == 1:
                self.update_route_for_searching()

            self.check_parking_spots()
            self.current_route = self.current_route[1:]

    def park_to_spot(self, parking_spot):
        self.parking_database.park_with_vehicle(parking_spot, self.uuid)
        self.travelling_state = TravellingState.PARKING
        self.parking_spot = parking_spot
        self.remaining_parking_time = random.randint(3, 30) # cycles to wait at parking spot

        if self.has_sensor:
            self.parking_database.report_parking_spot(parking_spot, False)

        self.analytics.report_parking(has_sensor=self.has_sensor, steps_before_parked=self.steps_looking_for_parking,
                                      destination_node=self.current_destination, parking_spot=parking_spot)

    def leave_from_spot(self):
        self.parking_database.leave_with_vehicle(self.parking_spot)
        self.travelling_state = TravellingState.TRAVELLING

        if self.has_sensor:
            self.parking_database.report_parking_spot(self.parking_spot, True)

        self.parking_spot = None

        if len(self.current_route) > 0:
            current_segment_id = self.current_route[0]
        else:
            current_segment_id = self.routing.get_random_segment().name

        self.current_route = self.create_random_destination(current_segment_id)
        self.steps_looking_for_parking = 0

    def update_route_for_searching(self):
        current_segment_id = self.current_route[0]
        if self.has_sensor:
            selected_parking_spot = self.routing.find_empty_parking_spot_recursively([self.current_destination], [])

            self.current_route += self.routing.get_segments_in_route_to_parking_spot(current_segment_id,
                                                                                     selected_parking_spot.to_dict())

        else:
            start_node = self.routing.get_next_node_to_segment(current_segment_id)
            random_search_nodes = self.routing.create_nodes_for_random_parking_spot_searching(start_node)
            planned_route = self.routing.get_all_segments_for_nodes(random_search_nodes)
            route_to_start_node = self.routing.get_segments_between_segment_and_end_node(current_segment_id)
            self.current_route += route_to_start_node + planned_route

    def check_parking_spots(self):
        if len(self.current_route) == 0:
            return

        current_segment = self.current_route[0]
        empty_spots = self.parking_database.get_empty_parking_spaces_for_segment(current_segment)
        # print('empty spots', current_segment, empty_spots)

        # TODO: reported while going
        if self.travelling_state == TravellingState.SEARCHING_FOR_PARKING and len(empty_spots) > 0:
            self.park_to_spot(empty_spots[0])

        if (
                self.travelling_state == TravellingState.TRAVELLING or self.travelling_state == TravellingState.SEARCHING_FOR_PARKING) and self.has_sensor:
            self.parking_database.report_parking_spots_on_segment(current_segment)
