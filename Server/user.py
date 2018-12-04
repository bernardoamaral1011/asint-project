class User:
    def __init__(self, idd, name, latitude, longitude, range, building):
        self.idd = idd
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.range = range
        self.building = building

    def __str__(self):
        return "%d - %s - %s - %s - %d - %s" % \
               (self.idd, self.name, self.latitude, self.longitude, self.range, self.building)