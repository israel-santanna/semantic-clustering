import re
from io import open
from models.data_object import DataObject
from models.user import User


class MovieLens(object):

    def __init__(self, movies_path=None):
        self._movies_path = movies_path if movies_path else "data/movies.dat"
        self._ratings_path = "data/ratings1M.dat"

    def movies_path(self):
        return self._movies_path

    def movies(self):
        _movies = []
        with open(self._movies_path, "r", encoding="ISO-8859-1") as file:
            # Line format:
            # id::name, the (original name) (year)::genre1|genre2|...|genreN
            for line in file:
                id_number, name, tags = line.split("::")
                name = self.__fix_name(name)
                movie = DataObject(int(id_number))
                movie.data = {"name": name, "genres": tags.split("|")}
                _movies.append(movie)
        return _movies

    def users_ratings(self, objs):
        _users_ratings = {}
        n_ratings = 0
        with open(self._ratings_path, "r", encoding="ISO-8859-1") as file:
            # Line format:
            # UserID::MovieID::Rating::Timestamp
            for line in file:
                user_id, movie_id, value, timestamp = line.strip().split("::")
                user_id = int(user_id)
                movie_id = int(movie_id)
                if movie_id in objs:
                    n_ratings += 1
                    if user_id in _users_ratings:
                        user = _users_ratings[user_id]
                    else:
                        user = User(user_id)
                        _users_ratings[user_id] = user
                    objs[movie_id].ratings.append(int(value))
                    user.ratings.append({"rating": int(value),
                                         "timestamp": timestamp,
                                         "object": objs[movie_id]})
        print("Number of Ratings: " + str(n_ratings))
        return _users_ratings

    # Changes "Star Maker, The (Uomo delle stelle, L') (1995)"
    #      to "The Star Maker (L'Uomo delle stelle) (1995)"
    def __fix_name(self, name):
        words = ["The", "A", "An", "La", "Le", "Les", "L'", "Il", "El", "Das",
                 "Der", "Det", "Die", "I", "O"]

        match = re.search(", ([\w']+) \(", name)
        if match and match.group(1) in words:
            begin, end = match.span()
            before = match.group(1)
            space = "" if before[-1] == "'" else " "
            name = before + space + name[:begin] + name[end - 2:]

        match = re.search(", ([\w']+)\)", name)
        if match and match.group(1) in words:
            begin, end = match.span()
            op_par = name.rfind("(", 0, begin)
            before = match.group(1)
            space = "" if before[-1] == "'" else " "
            if op_par != -1:
                name = name[:op_par + 1] + before + space \
                    + name[op_par + 1:begin] + name[end - 1:]

        return name
