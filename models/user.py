from statistics import mean


class User(object):

    def __init__(self, _id=None):
        self._id = _id
        self._ratings = []
        self._recommendations = {}
        self._clusters = {}
        self.mean = None
        self._high_ratings = None
        self._low_ratings = None
        self._union = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def ratings(self):
        return self._ratings

    @ratings.setter
    def ratings(self, value):
        self._ratings = value

    @property
    def clusters(self):
        return self._clusters

    @clusters.setter
    def clusters(self, value):
        self._clusters = value

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        self._dataset = value

    @property
    def recommendations(self):
        return self._recommendations

    @recommendations.setter
    def recommendations(self, value):
        self._recommendations = value

    def clusters_union(self):
        if not self._union:
            self._union = set()
            for center, cluster in self.clusters.items():
                self._union.update(cluster["objects"])
        return self._union

    def ratings_mean(self):
        if not self.mean:
            self.mean = mean([x["rating"] for x in self._ratings])
        return self.mean

    def high_ratings(self):
        if not self._high_ratings:
            self.split_ratings()
        return self._high_ratings

    def low_ratings(self):
        if not self._low_ratings:
            self.split_ratings()
        return self._low_ratings

    def split_ratings(self):
        self._high_ratings = []
        self._low_ratings = []
        for x in self._ratings:
            if x["rating"] >= int(self.ratings_mean()):
                self._high_ratings.append(x)
            else:
                self._low_ratings.append(x)

    def __repr__(self):
        return "<User id:" + str(self.id) \
            + " instance at " + str(id(self)) + ">"
