from Server.user import User


class UserDB:
    def __init__(self):
        self.userList = {}

    def log_in(self, idd, name, latitude, longitude, range, building):
        self.userList.append(User(idd, name, latitude, longitude, range, building))

    def log_out(self, idd):
        for aux in self.userList:
            if aux.idd == idd:
                self.userList.remove(aux)
                break