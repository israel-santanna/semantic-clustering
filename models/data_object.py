from statistics import mean


class DataObject(object):

    def __init__(self, _id=None):
        self._id = _id
        self._data = {}
        self._ratings = []
        self.mean = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def ratings(self):
        return self._ratings

    @ratings.setter
    def ratings(self, value):
        self._ratings = value

    def ratings_mean(self):
        if not self.mean:
            self.mean = mean(self.ratings)
        return self.mean

    def str_data(self, weights={}):
        str_data = ""
        for key, values in self._data.items():
            repeat = 1 if key not in weights else weights[key]
            for i in range(repeat):
                str_data += values + ' '
        return str_data

    def __repr__(self):
        return "<DataObject id:" + str(self.id)     \
            + ", name:" + self.data["name"]         \
            + " instance at " + str(id(self)) + ">"
