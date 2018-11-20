class building:
    def __init__(self, b_id, name, latitude, longitude):
        self.id = b_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "%d - %s - %s - %s" % (self.id, self.name, self.latitude, self.longitude)