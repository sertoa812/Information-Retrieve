import numpy as np

import GetDataSets
import thulac
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import multiprocessing
from sklearn import svm
from sklearn.externals import joblib
import linecache

class SentimentAnalyzerBase:

    def __init__(self):
        pass

    def token(self, sequence):
        stop_words = GetDataSets.get_stop_words()
        thu1 = thulac.thulac(seg_only=True, filt=True)
        seq = thu1.cut(sequence, text=True).split(' ')
        seq_no_stop_words = [value for value in seq if value not in stop_words]
        return seq_no_stop_words

#https://www.jianshu.com/p/4cfcf1610a73
class SentimentAnalyzerEasy(SentimentAnalyzerBase):

    def __init__(self):
        super().__init__()

    def get_lists(self):
        # (1) 情感词
        # 词：分数形式
        senDict = GetDataSets.get_bosonNLP_words()
        # (2) 否定词
        # 词列表
        notDict = GetDataSets.get_not_words()
        # (3) 程度副词
        # 词：分数形式
        degreeDict = GetDataSets.get_adv_words()

        return senDict, notDict, degreeDict

    def cal_sentiment(self, sequence):
        sen_list, not_list, degree_list = self.get_lists()
        seq_list = self.token(sequence)

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
        word2vec_model = Word2Vec.load('Models/word2vector.model')
        svm_model = joblib.load('Models/svm.model')
        sentence_nostopwords_list= self.token(sentence)
        sentence_vector = self.generate_sentence_vector(sentence_nostopwords_list, word2vec_model)
        return svm_model.predict([sentence_vector])

sas = SentimentAnalyzerSVM()
print(sas.analyze('张云剑bageyalu'))