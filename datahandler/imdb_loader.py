from os.path import isfile
from models.data_object import DataObject
from .movie_lens import MovieLens


class ImdbLoader(object):
    def __init__(self, data_path=None):
        super(ImdbLoader, self).__init__()
        self.data_path = data_path if data_path else "data/movies_data"
        self.movie_lens = MovieLens(data_path)

    def load_objects(self):
        movies = {}
        if not isfile(self.data_path):
            return None
        with open(self.data_path, "r", 1, encoding="utf-8") as file:
            for line in file:
                data = line.split("::")
                if len(data) > 2 and data[1] != "ERROR\n":
                    movie = DataObject(int(data[0]))
                    movie.data = {"name": data[1], "plots": data[2],
                                  "genres": data[3], "reviews": data[4]}
                    movies[movie.id] = movie
        print("Number of Movies: " + str(len(movies)))
        return movies

    def load_users_ratings(self, objs):
        users = self.movie_lens.users_ratings(objs)
        print("Number of Users: " + str(len(users)))
        return users
