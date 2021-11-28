import datetime

import pandas as pd


class AnalyticsDatabase:
    def __init__(self, simulation, number_of_vehicles, sensor_ratio):
        self.data_list = []
        self.number_of_vehicles = number_of_vehicles
        self.simulation = simulation
        self.name = f'{number_of_vehicles}-{sensor_ratio}'

    def report_parking(self, has_sensor, steps_before_parked, destination_node, parking_spot):
        self.data_list.append({
            'cycle': self.simulation.cycle,
            'has_sensor': has_sensor,
            'steps_before_parked': steps_before_parked,
            'destination_node': destination_node,
            'parking_segment': parking_spot
        })

    def save(self):
        print(f'Saving {len(self.data_list)} items')
        df = pd.DataFrame(self.data_list)
        df.to_pickle(f'./exports/{self.name}-{len(self.data_list)}-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.pkl')