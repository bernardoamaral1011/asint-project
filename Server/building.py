class Building:
    def __init__(self, b_id, name, latitude, longitude, range):
        self.id = b_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.range = range

    def __str__(self):
        return "%d - %s - %s - %s - %d" % (self.id, self.name, self.latitude, self.longitude, self.range)