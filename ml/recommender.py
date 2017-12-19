from operator import itemgetter
from itertools import combinations
from ml.paragraph_vector import ParagraphVector
from lib.densitypeakcluster.cluster import DensityPeakCluster
# from lib.densitypeakcluster.plot import plot_rho_delta
# from lib.densitypeakcluster.plot import plot_cluster
from math import log


class Recommender(object):
    def __init__(self, proportion, topn=10, weights={}):
        super(Recommender, self).__init__()
        self.proportion = proportion
        self.weights = weights
        self.topn = topn
        self.pv = None

    def fit(self, objs, model_path=None):
        self.objs = objs
        self.pv = ParagraphVector(model_path)
        self.pv.train(objs.values(), self.weights, load=True)
        print("=============== FINISHED PV TRAINING ===============")

    def predict(self, dataset):
        if not self.pv:
            print("You must call fit() before predict().")
            exit()
        recoms = {}
        for obj in dataset:
            similars = self.pv.similars(obj, self.topn)
            for sim in similars:
                if self.objs[int(sim[0])] not in dataset:
                    recoms[self.objs[int(sim[0])]] = sim[1]
        return recoms

    def user_clusters(self, objs):
        dpcluster = DensityPeakCluster()
        rho, delta, nneigh = dpcluster.cluster(self.pv.distances, objs,
                                               0.3, 0.3, auto_select_dc=True)
        clusters = {}
        for c in dpcluster.ccenter.values():
            if c != -1:
                max_dist = 0
                for i in dpcluster.cluster.values():
                    if c != -1:
                        dist = self.pv.distance(objs[c], objs[i])
                        if dist > max_dist:
                            max_dist = dist
                clusters[objs[c]] = max_dist
                clusters[objs[c]] = \
                    {"distance": max_dist,
                     "objects": [objs[j] for j in dpcluster.cluster.values()]}

        # Uncomment for Debug
        # for i, c in dpcluster.cluster.items():
        #     print("i: "+str(i)+" Movie: "+str(objs[i].id)+" Cluster: "+str(c))
        # plot_rho_delta(rho, delta)
        # plot_cluster(dpcluster)
        return clusters

    def recommend(self, user, exclude_set, objects):
        rec = {obj: obj.ratings_mean()
               for obj in objects if obj not in exclude_set}
        user.recommendations.update(rec)

    def users_prediction(self, users_ratings):
        users_size = len(users_ratings.values())

        n_clusters = 0
        n_user_clusters = 0
        for user in users_ratings.values():
            training, validation = self.split_ratings(user.high_ratings())
            train_objs = [rating["object"] for rating in training]
            val_objs = [rating["object"] for rating in validation]
            user.dataset = (train_objs, val_objs)
            user.clusters = self.user_clusters(train_objs)
            if user.clusters:
                n_user_clusters += 1
                n_clusters += len(user.clusters)
        print("=============== FINISHED CLUSTERS CREATION ===============")
        print("Number of clusters: " + str(n_clusters))
        print("Number of users with clusters: " + str(n_user_clusters))

        n_intersections = 0
        for users in combinations(users_ratings.values(), 2):
            if users[0].clusters and users[1].clusters:
                exclude_set0 = set(users[0].dataset[0])
                exclude_set0.update([rating["object"]
                                    for rating in users[0].low_ratings()])
                exclude_set1 = set(users[1].dataset[0])
                exclude_set1.update([rating["object"]
                                    for rating in users[1].low_ratings()])
                intersection = False
                for center0, cluster0 in users[0].clusters.items():
                    for center1, cluster1 in users[1].clusters.items():
                        dist = self.pv.distance(center0, center1)
                        if dist < cluster0["distance"] + cluster1["distance"]:
                            n_intersections += 1
                            intersection = True
                            break
                    if intersection:
                        break
                if intersection:
                    self.recommend(users[0],
                                   exclude_set0,
                                   users[1].clusters_union())

                    self.recommend(users[1],
                                   exclude_set1,
                                   users[0].clusters_union())
        print("=============== FINISHED CLUSTERS INTERSECTION ===============")
        print("Number of clusters intersections: " + str(n_intersections))

        p_total, r_total, f_total = 0, 0, 0
        ild_total, unexp_total, iuf_total = 0, 0, 0
        s_unexp_total, s_iuf_total = 0, 0
        for user in users_ratings.values():
            if not user.recommendations:
                user.recommendations = self.predict(user.dataset[0])

            rec = sorted(user.recommendations.items(),
                         key=itemgetter(1), reverse=True)[:self.topn]
            rec = [x[0] for x in rec]
            precision, recall, f1_score = self.accuracy(rec, user.dataset[1])

            p_total += precision
            r_total += recall
            f_total += f1_score

            ild_total += self.diversity(rec)

            unexp, iuf = self.novelty(rec, user, users_size)
            unexp_total += unexp
            iuf_total += iuf

            s_unexp, s_iuf = self.serendipity(rec, user, users_size)
            s_unexp_total += s_unexp
            s_iuf_total += s_iuf
        print("=============== FINISHED METRICS CALCULATION ===============")
        p_total = p_total / users_size
        r_total = r_total / users_size
        f_total = f_total / users_size
        ild_total = ild_total / users_size
        unexp_total = unexp_total / users_size
        s_unexp_total = s_unexp_total / users_size
        iuf_total = iuf_total / users_size
        s_iuf_total = s_iuf_total / users_size
        print("p_mean")
        print(p_total)
        print("r_mean")
        print(r_total)
        print("f_mean")
        print(f_total)
        print("ild_mean")
        print(ild_total)
        print("unexp_mean")
        print(unexp_total)
        print("iuf_mean")
        print(iuf_total)
        print("s_unexp_mean")
        print(s_unexp_total)
        print("s_iuf_mean")
        print(s_iuf_total)

    def accuracy(self, predicted, validation):
        correct_predictions = 0
        for obj in predicted:
            if obj in validation:
                correct_predictions += 1
        if correct_predictions == 0:
            return 0, 0, 0

        precision = correct_predictions / len(predicted)
        recall = correct_predictions / len(validation)
        f1_score = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1_score

    def diversity(self, predicted):
        _sum = 0
        for obj1, obj2 in combinations(predicted, 2):
            _sum += self.pv.distance(obj1, obj2)
        return _sum / (len(predicted) * (len(predicted) - 1))

    def novelty(self, predicted, user, users_size):
        sum_unexp = 0
        sum_iuf = 0
        for obj1 in predicted:
            if len(obj1.ratings) == 0:
                user_freq = users_size
            else:
                user_freq = users_size / len(obj1.ratings)
            sum_iuf += log(user_freq, 2)
            for rating in user.ratings:
                sum_unexp += self.pv.distance(obj1, rating["object"])
        unexp = sum_unexp / (len(predicted) * len(user.ratings))
        iuf = sum_iuf / len(predicted)
        return unexp, iuf

    def serendipity(self, predicted, user, users_size):
        sum_unexp = 0
        sum_iuf = 0
        for obj1 in predicted:
            if obj1 in user.dataset[1]:
                if len(obj1.ratings) == 0:
                    user_freq = users_size
                else:
                    user_freq = users_size / len(obj1.ratings)
                sum_iuf += log(user_freq, 2)
                for rating in user.ratings:
                    sum_unexp += self.pv.distance(obj1, rating["object"])
        unexp = sum_unexp / (len(predicted) * len(user.ratings))
        iuf = sum_iuf / len(predicted)
        return unexp, iuf

    def split_ratings(self, ratings):
        n_validation = int(self.proportion * len(ratings))
        ratings = sorted(ratings, key=itemgetter('timestamp'), reverse=True)
        # training = from 0 to n
        # validation = from n to end
        return ratings[n_validation:], ratings[:n_validation]
