class Station:
    def __init__(self, type, lat, lon, name, colour):
        self.type = type
        self.lat = lat
        self.lon = lon
        self.name = name
        self.colour = colour


def in_list(lat, lon, list):
    for s in list:
        if (s.lat == lat) & (s.lon == lon):
            return True
    return False

def remove_from_list(lat, lon, list):
    for s in list:
        if (s.lat == lat) & (s.lon == lon):
            list.remove(s)
    return list