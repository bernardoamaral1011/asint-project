from Server.building import Building
import pickle


class BuildingDB:
    def __init__(self):
        # TODO: verification and error handling
        try:
            f = open('buildings_dump', 'rb')
            self.bib = pickle.load(f)
            f.close()
        except IOError:
            self.bib = {}

    def add_building(self, b_id, name, latitude, longitude):
        idd = len(self.bib)
        self.bib[idd] = Building(b_id, name, latitude, longitude)
        f = open('buildings_dump', 'wb')
        pickle.dump(self.bib, f)
        f.close()

    def list_buildings(self):
        return list(self.bib.values())

    def list_id(self, b_id):
        ret_value = []
        for b in self.bib.values():
            if b.id == b_id:
                ret_value.append(b)
        return ret_value

    def list_name(self, name):
        ret_value = []
        for b in self.bib.values():
            if b.namelatitude == name:
                ret_value.append(b)
        return ret_value

    def list_latitude(self, latitude):
        ret_value = []
        for b in self.bib.values():
            if b.latitude == latitude:
                ret_value.append(b)
        return ret_value

    def list_longitude(self, longitude):
        ret_value = []
        for b in self.bib.values():
            if b.longitude == longitude:
                ret_value.append(b)
        return ret_value
