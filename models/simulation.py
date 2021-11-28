import time
import numpy as np
from uuid import uuid4

from models.analyticsDatabase import AnalyticsDatabase
from models.citymap import CityMap
from models.parkingDatabase import ParkingDatabase
from models.routing import Routing
from models.vehicle import Vehicle
from collections import ChainMap


class Simulation:
    vehicles = []
    parking_spots = {}  # this might be a df

    def __init__(self, number_of_vehicles):
        self.cycle = 0
        self.sensor_ratio = 0.35
        self.map = CityMap(target_area='V. kerület')
        self.parking_database = ParkingDatabase()
        self.routing = Routing(parking_database=self.parking_database, city_map=self.map)
        self.analytics = AnalyticsDatabase(simulation=self, number_of_vehicles=number_of_vehicles,
                                           sensor_ratio=self.sensor_ratio)

        for _ in range(number_of_vehicles):
            try:
                self.vehicles.append(Vehicle(uuid=uuid4(),
                                             parking_database=self.parking_database,
                                             city_map=self.map,
                                             routing=self.routing, analytics=self.analytics,
                                             sensor_ratio=self.sensor_ratio))
            except Exception:
                pass

        print(f'Created {len(self.vehicles)} vehicle')

    def to_json(self):
        parking_spots = self.parking_database.to_json()
        segments = [vehicle.to_json() for vehicle in self.vehicles]
        segments = [s for s in segments if s is not None]
        segments_as_dict = {k: v for element in segments for k, v in element.items()}

        searching_vehicles = {k: v for k, v in segments_as_dict.items() if v['state'] == 'SEARCHING_FOR_PARKING'}
        searching_vehicles_with_sensor = len({k: v for k, v in searching_vehicles.items() if v['has_sensor'] == True})

        return {
            'vehicles_on_segments': segments_as_dict,
            'parking_spots': parking_spots,
            'statistics': {
                'searching': {'has_sensor': searching_vehicles_with_sensor,
                              'no_sensor': len(searching_vehicles) - searching_vehicles_with_sensor},
                'number_of_spots': self.parking_database.get_number_of_empty_and_occupied_spots()
            }
        }

    def step(self):
        print(f'Simulating cycle {self.cycle}')
        for vehicle in self.vehicles:
            vehicle.step()

        if self.cycle % 100 == 0:
            self.analytics.save()

        self.cycle += 1

    def run(self):
        while True:
            self.step()
            # time.sleep(1)
