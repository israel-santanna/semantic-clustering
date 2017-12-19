import argparse
from datahandler.imdb_loader import ImdbLoader
from ml.recommender import Recommender


def parse_args():
    parser = argparse.ArgumentParser(description="Recommender")
    parser.add_argument("-p", "--test_proportion",
                        help="Proportion from training dataset to be used as" +
                        " validation", default="0.2", type=float)
    parser.add_argument("-n", "--topn",
                        help="Number of items to be recommended to one user",
                        default="10", type=int)
    parser.add_argument("-d", "--data_path",
                        help="File containing the objects data to train the" +
                        " Paragraph Vector", default="data/movies_data")
    parser.add_argument("-l", "--load_path",
                        help="File containing the trained Paragraph Vector" +
                        " to be loaded", default="data/dm_concat_1-1-1-1")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    loader = ImdbLoader(args.data_path)
    objs = loader.load_objects()
    if objs is None:
        print("File " + args.data_path + " not found.")
        exit()
    elif not objs:
        print("No objects found.")
        exit()
    users = loader.load_users_ratings(objs)
    print("=============== FINISHED READING ===============")
    weights = {"name": 1, "plots": 1, "genres": 1, "reviews": 1}
    recom = Recommender(args.test_proportion, args.topn, weights)
    recom.fit(objs, args.load_path)
    recom.users_prediction(users)
