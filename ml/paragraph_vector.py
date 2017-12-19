import sys
import multiprocessing
import gensim.models.doc2vec
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from gensim.utils import simple_preprocess
from scipy.stats import pearsonr
from os.path import isfile

assert gensim.models.doc2vec.FAST_VERSION > -1


class ParagraphVector(object):
    def __init__(self, model_path=None):
        super(ParagraphVector, self).__init__()
        cores = multiprocessing.cpu_count()
        # PV-DBOW
        # self.model = Doc2Vec(dm=0, size=100, window=10, negative=5, hs=0,
        #                      min_count=1, workers=cores,
        #                      sample=1e-4, iter=20)

        # PV-DM w/ concatenation
        self.model = Doc2Vec(dm=1, dm_concat=1, size=100, window=10,
                             negative=5, hs=0, min_count=1, workers=cores,
                             sample=1e-4, iter=20)

        # PV-DM w/ average
        # self.model = Doc2Vec(dm=1, dm_mean=1, size=100, window=10,
        #                      negative=5, hs=0, min_count=1, workers=cores,
        #                      sample=1e-4, iter=20)
        self.model_path = model_path if model_path else "data/trained_model"
        self.trained = False

    def corpus(self, objs, weights={}):
        docs = []
        for obj in objs:
            doc = TaggedDocument(simple_preprocess(obj.str_data(weights)),
                                 [str(obj.id)])
            docs.append(doc)
        return docs

    def train(self, objs, weights={}, load=False):
        if load and isfile(self.model_path):
            print("=============== LOADING PV ===============")
            self.model = Doc2Vec.load(self.model_path)
            print("=============== FINISHED PV LOADING ===============")
        else:
            print("=============== TRAINING PV ===============")
            train_corpus = self.corpus(objs, weights)
            self.model.build_vocab(train_corpus)
            self.model.train(train_corpus,
                             total_examples=self.model.corpus_count,
                             epochs=self.model.iter)
            self.model.save(self.model_path)
            print("=============== FINISHED PV TRAINING ===============")
        self.trained = True

    def similars(self, obj, n=10):
        if not self.trained:
            raise Exception("You must train the ParagraphVector first.")
        sims = self.model.docvecs.most_similar(positive=[str(obj.id)], topn=n)
        return sims

    def distance(self, obj1, obj2, method='pearson'):
        if method == 'pearson':
            return pearsonr(self.model.docvecs[str(obj1.id)],
                            self.model.docvecs[str(obj2.id)])[0]
        elif method == 'cos':
            return self.model.docvecs.similarity(str(obj1.id), str(obj2.id))
        else:
            raise Exception("Distance method type inexistent.")

    def distances(self, objs):
        _distances = {}
        min_dis, max_dis, max_id = sys.float_info.max, 0.0, 0
        max_id = len(objs) - 1

        for i, obj1 in enumerate(objs):
            for j, obj2 in enumerate(objs):
                if (i == j):
                    _distances[(i, j)] = 0.0
                else:
                    _distances[(i, j)] = self.distance(obj1, obj2)

                    max_dis = max(max_dis, _distances[(i, j)])
                    min_dis = min(min_dis, _distances[(i, j)])
        return _distances, max_dis, min_dis, max_id

    def vectors(self, objs):
        return [self.model.docvecs[str(obj.id)] for obj in objs]
