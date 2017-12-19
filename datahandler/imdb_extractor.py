import re
import sys
import string
from time import sleep
from imdb import IMDb as IMDBPy
from imdbpie import Imdb as IMDBPie
from imdb._exceptions import IMDbDataAccessError
from io import open


class ImdbExtractor(object):

    def __init__(self, data_path=None):
        super(ImdbExtractor, self).__init__()
        self.search_api = IMDBPy()
        self.info_api = IMDBPie(anonymize=True)
        self.movie_lens = MovieLens(data_path)
        # self.data_path = "data/movies_data"
        self.data_path = data_path + ".out" if data_path \
            else "data/movies_data"
        self.errors = []

    def retrieve_objects(self):
        movies = self.movie_lens.movies()
        with open(self.data_path, "w", 1, encoding="utf-8") as file:
            for movie in movies:
                print("\n")
                print(movie.id)
                print(movie.data["name"])
                while True:
                    try:
                        m = self.find_movie(movie.data["name"])
                    except IMDbDataAccessError as e:
                        print("========== CONNECTION ERROR ==========")
                        print(e)
                        sleep(5)
                    else:
                        break

                data = str(movie.id)
                if m:
                    plots, genres = self.movie_info(m.movieID)
                    reviews = self.movie_reviews(m.movieID)
                    if plots or genres or reviews:
                        movie.data["genres"].extend(genres)
                        data += u'::' + movie.data["name"]
                        data += u'::' + u' '.join(filter(None, plots))
                        data += u'::' + u' '.join(filter(None,
                                                         movie.data["genres"]))
                        data += u'::' + u' '.join(filter(None, reviews))
                        data = data.replace('\r', ' ').replace('\n', ' ')
                    else:
                        data += u"::ERROR"
                else:
                    data += u"::ERROR"
                file.write(data + u"\n")

    def movie_reviews(self, movie_id):
        try:
            reviews = self.info_api.get_title_reviews("tt" + movie_id,
                                                      max_results=20)
        except ValueError as e:
            return []

        reviews_arr = []
        if reviews:
            for r in reviews:
                review = r.summary if r.summary else ""
                review += " " + r.text if r.text else ""
                reviews_arr.append(review)
        return reviews_arr

    def movie_info(self, movie_id):
        try:
            movie = self.info_api.get_title_by_id("tt" + movie_id)
        except ValueError as e:
            return [], []
        plots = movie.plots if movie.plots else []
        genres = movie.genres if movie.genres else []
        return plots, genres

    def find_movie(self, name):
        movies = self.search_api.search_movie(name)
        if not movies:
            name = re.sub("\((\D*)\)", "", name)
            print("---------- SEARCHING AGAIN: ----------")
            print(name)
            movies = self.search_api.search_movie(name)
            print(movies)
            if not movies:
                print("########## NO MOVIE FOUND ##########")
                return None

        def sanitize_name(_str):
            new_str = _str.strip().lower()
            for char in string.punctuation:
                new_str = new_str.replace(char, "")
            return new_str

        name_split = name.split("(")
        title = sanitize_name(name_split[0])
        year = int(name_split[-1][:-1].strip())

        movie = None
        for i in movies:
            if "year" in i.keys() and int(i["year"]) == year:
                movie = i
                break
        if not movie:
            print("########## NO MOVIE FROM SAME YEAR ##########")
            return None

        self.search_api.update(movie)

        eng_title = ""
        if "akas" in movie.keys():
            print("tem akas")
            for aka in movie["akas"]:
                aka_split = aka.split("::")
                if len(aka_split) > 1                                   \
                        and (aka_split[1].find("(English title)") != -1 \
                             or aka_split[1].find("USA") != -1):
                    eng_title = aka_split[0].strip().lower()
                    break

        imdb_title = sanitize_name(movie["title"])
        original_title = name_split[1].strip()[:-1].lower()
        print("imdb title: " + imdb_title)
        print("english title: " + eng_title)
        print("year: " + str(movie["year"]))
        if imdb_title == title or eng_title == title                    \
                or (len(name_split) == 3                                \
                    and imdb_title == original_title):
            return movie
        else:
            print("########## FOUND DIFFERENT MOVIE ##########")
            print(movie["title"] + " (" + str(movie["year"]) + ")")
            return None


if __name__ == "__main__":
    if __package__ is None:
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from movie_lens import MovieLens
    else:
        from .movie_lens import MovieLens
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    extractor = ImdbExtractor(data_path)
    extractor.retrieve_objects()
else:
    from .movie_lens import MovieLens
