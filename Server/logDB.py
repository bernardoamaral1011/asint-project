from Server.log import Log
import pickle


class LogDB:
    def __init__(self):
        try:
            f = open('logs_dump', 'rb')
            self.bib = pickle.load(f)
            f.close()
        except IOError:
            self.bib = {}

    def add_log(self, user, building, message):
        idd = len(self.bib)
        self.bib[idd] = Log(user, building, message)
        f = open('logs_dump', 'wb')
        pickle.dump(self.bib, f)
        f.close()

    def logs_by_user(self, user):
        ret_value = []
        for u in self.bib.values():
            if u.user == user:
                ret_value.append(u)
        return ret_value

    def logs_by_building(self, building):
        ret_value = []
        for u in self.bib.values():
            if u.building == building:
                ret_value.append(u)
        return ret_value

    def last_user_movement(self, user):
        ret_value = []
        # TODO
        return ret_value


