import numpy as np

import GetDataSets
import thulac
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import multiprocessing
from sklearn import svm
from sklearn.externals import joblib
import os

class SentimentAnalyzerBase:

    def __init__(self):
        pass

    def token(self, sequence):
        stop_words = GetDataSets.get_stop_words()
        thu1 = thulac.thulac(seg_only=True, filt=True)
        seq = thu1.cut(sequence, text=True).split(' ')
        seq_no_stop_words = [value for value in seq if value not in stop_words]
        return seq_no_stop_words

class SentimentAnalyzerSVM(SentimentAnalyzerBase):
    def __init__(self):
        super().__init__()

    def generate_sentence_vector(self, sentence, word2vec_model):
        vecs = []
        for word in sentence:
            try:
                vecs.append(word2vec_model[word])
            except KeyError:
                continue
                # vecs = np.concatenate(vecs)
        resultList = np.array(vecs, dtype='float')
        if len(resultList) != 0:
            resultArray = sum(np.array(resultList)) / len(resultList)
            return resultArray.tolist()

    def analyze(self, sentence):
        # 1. token and filter stop words
        # 2. generate sentence vector by the mean of each word vector
        vector_path = os.path.join(os.path.abspath('.'), 'Models', 'word2vector.model')
        svm_path = os.path.join(os.path.abspath('.'), 'Models', 'svm.model')
        # load the model
        word2vec_model = Word2Vec.load(vector_path)
        svm_model = joblib.load(svm_path)
        # token
        sentence_nostopwords_list= self.token(sentence)
        # generate vector
        sentence_vector = self.generate_sentence_vector(sentence_nostopwords_list, word2vec_model)
        return svm_model.predict([sentence_vector])

sas = SentimentAnalyzerSVM()
print(sas.analyze('张云剑bageyalu'))