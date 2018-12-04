class Log:
    def __init__(self, user, building, message):
        self.building = building
        self.user = user
        self.message = message

    def __str__(self):
        return "%d - %s - %s" % (self.user, self.building, self.message)
