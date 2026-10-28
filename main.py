from parser import Parser
import heapq
from itertools import count


class Drone:
    _id = 1
    def __init__(self, start_zone, end_zone, path):
        self.id = Drone._id
        self.name = f'D{self.id}'
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.curr_zone = start_zone
        self.path = path
        self.pos_idx = 0

        Drone._id += 1

    @property
    def delivered(self):
        return self.curr_zone == self.end_zone


class Connection:
    def __init__(self, name, metadata):
        self.name = name
        self.metadata = metadata


class Zone:
    def __init__(self, name, type, x, y, metadata):
        self.name = name
        self.type = type
        self.x = x
        self.y = y
        self.metadata = metadata
        self.neighbors = []
        self.drones = []
        self.zone = ''
        self.cost = 0
        self.max_drones = 1

        if 'zone' in metadata: self.zone = metadata['zone']
        else: self.zone = 'normal'

        if 'max_drones' in metadata:
            self.max_drones = metadata['max_drones']

        if   self.zone == 'priority':     self.cost = 0.99
        elif self.zone == 'normal':       self.cost = 1
        elif self.zone == 'restricted':   self.cost = 2
        elif self.zone == 'blocked':      self.cost = 999


    def add_neighbor(self, zone):
        if zone not in self.neighbors:
            self.neighbors.append(zone)


class Flyin:
    def __init__(self, parser):
        self.parser = parser
        self.zones = []
        self.connections = []
        self.drones = []

        self.start_zone = None
        self.end_zone   = None


    def create_zones(self):
        for z in self.parser.zones:
            zone_type = z['hub_type']
            zone_name = z['name']
            zone_x = z['x']
            zone_y = z['y']
            zone_metadata = z['metadata']

            z_obj = Zone(zone_name, zone_type, zone_x, zone_y, zone_metadata)

            self.zones.append(z_obj)

            if zone_type == 'start_hub': self.start_zone = z_obj
            if zone_type == 'end_hub': self.end_zone = z_obj

    
    
    def create_connections(self):
        for c in self.parser.connections:
            c_name = c['name']
            c_metadata = c['metadata']

            self.connections.append(
                Connection(c_name, c_metadata)
            )

    def _get_zone_by_name(self, name):
        for z in self.zones:
            if z.name == name:
                return z
        return None


    def _get_conn_by_name(self, name):
        for c in self.connections:
            if c.name == name:
                return c
        return None


    def create_graph(self):
        for c in self.connections:
            z1, z2 = c.name.split('-')

            z1 = self._get_zone_by_name(z1)
            z2 = self._get_zone_by_name(z2)

            z1.add_neighbor(z2)
            z2.add_neighbor(z1)


    def create_drones(self):
        paths = self._find_paths()

        for i in range(self.parser.nb_drones):
            d = Drone(self.start_zone, self.end_zone, paths[i % len(paths)][1])
            self.drones.append(d)
            self.start_zone.drones.append(d)


    def _find_paths(self):
        paths = []
        counter = count()

        queue = [(0, next(counter), [self.start_zone])]


        while queue:
            current_cost, _, current_path = heapq.heappop(queue)
            current_zone = current_path[-1]

            if current_zone == self.end_zone:
                paths.append((current_cost, current_path))
                continue

            neighbors = current_zone.neighbors

            for n in neighbors:
                if n.zone == 'blocked':
                    continue

                if n in current_path:
                    continue

                new_path = current_path + [n]
                new_cost = current_cost + n.cost

                heapq.heappush(queue, (new_cost, next(counter), new_path))

        return paths


    def _all_delivered(self):
        for d in self.drones:
            if d.curr_zone != self.end_zone:
                return False
        return True



    def simulate(self):
        turns = ''
        while not self._all_delivered():
            move = ''

            for d in self.drones:
                if d.delivered:
                    continue

                curr_zone = d.curr_zone
                next_zone = d.path[d.pos_idx + 1]


                if next_zone not in [self.start_zone, self.end_zone]:
                    if len(next_zone.drones) == next_zone.max_drones:
                        continue

                # moving the drone
                curr_zone.drones.remove(d)
                next_zone.drones.append(d)
                d.curr_zone = next_zone
                d.pos_idx += 1
                move += f'{d.name}-{next_zone.name} '

            turns += move.strip() + '\n'

        turns = turns.strip()

        print(turns)





def main():
    parser = Parser('./map.txt')
    parser.parse()


    # print(parser.nb_drones)
    # print(parser.zones)
    # print(parser.connections)
    # print(parser.start_zone)
    # print(parser.end_zone)


    flyin = Flyin(parser)
    flyin.create_zones()
    flyin.create_connections()
    flyin.create_graph()
    flyin.create_drones()
    flyin.simulate()






if __name__ == "__main__":
    main()
