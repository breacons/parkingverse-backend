
class ParkingSpot:
    uuid = None
    position = None
    segment = None
    vehicle = None
    shared_is_empty = False

    def __init__(self, uuid, position, segment, vehicle):
        self.uuid = uuid
        self.position = position
        self.segment = segment
        self.vehicle = vehicle

    def to_json(self):
        return {}

    def park_with_vehicle(self, vehicle):
        self.vehicle = vehicle
        # TODO: probably need to set on vehicle as well


    def report_empty(self):
        self.shared_is_empty = True

    def report_occupied(self):
        self.shared_is_empty = False

    def is_occupied(self):
        return self.vehicle is not None

    def is_empty(self):
        return self.vehicle is None

    def is_shared_empty(self):
        return self.shared_is_empty

    def is_shared_occupied(self):
        return not self.shared_is_empty


