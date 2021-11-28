import pandas as pd
import numpy as np


class ParkingDatabase:
    def __init__(self):
        self.df = pd.read_pickle('parking_spots.pkl').sort_index().assign(reported_empty=None)
        self.randomise()

    def to_json(self):
        return self.df[['parking_vehicle', 'reported_empty', 'lat', 'lon']].to_dict(orient='index')

    def park_with_vehicle(self, parking_spot, vehicle):
        self.df.loc[parking_spot, 'parking_vehicle'] = vehicle

    def leave_with_vehicle(self, parking_spot):
        self.df.loc[parking_spot, 'parking_vehicle'] = None

    def report_parking_spot(self, parking_spot, empty):
        self.df.loc[parking_spot, 'reported_empty'] = empty

    def report_parking_spots_on_segment(self, segment_id):
        self.df.loc[(self.df['segment_id'] == segment_id), 'reported_empty'] = ~self.df[(self.df['segment_id'] == segment_id)]['parking_vehicle'].astype(bool).values

    def is_parking_spot_empty(self, parking_spot):
        return self.df.loc[parking_spot, 'parking_vehicle'] is None

    def get_parking_spaces_for_segment(self, segment_id):
        spaces = self.df[(self.df['segment_id'] == segment_id)]
        return spaces

    def get_empty_parking_spaces_for_segment(self, segment_id):
        spaces = self.df[(self.df['segment_id'] == segment_id) & self.df['parking_vehicle'].isnull()]
        return spaces.index.values.tolist()

    def is_any_parking_spot_empty(self):
        return len(self.df[self.df.parking_vehicle.isnull()].index) != 0

    def get_empty_spots_from_ways_around_nodes(self, nodes):
        try:
            spots = self.df[((self.df.route_starting_node.isin(nodes)) | (self.df.route_ending_node.isin(nodes))) & (
            self.df.parking_vehicle.isnull())] # add reported
            return spots  # this is a dataframe
        except Exception:
            return []

    def get_random_empty_spot(self):
        return self.df[self.df['parking_vehicle'].isnull()].sample(n=1).iloc[0]

    def get_random_spot(self):
        return self.df.sample(n=1).iloc[0]

    def randomise(self):
        # values = np.random.choice(a=[None, 'static-vehicle'], size=(len(self.df.index, )))
        p = 0.95
        values = np.random.choice(a=['static-vehicle', None], size=(len(self.df.index, )), p=[p, 1 - p])
        self.df['parking_vehicle'] = values

    def get_number_of_empty_and_occupied_spots(self):
        empty = len(self.df[self.df.parking_vehicle.isnull()].index)
        not_empty = len(self.df) - empty
        return {
            'empty': empty,
            'not_empty': not_empty
        }

