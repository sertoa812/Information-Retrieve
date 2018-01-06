import GetDataSets
import thulac
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import multiprocessing
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

    def get_train_data(self):
        pass

    def word2vector(self, save_path):
        model = Word2Vec(LineSentence('train_datasets'), size=64, window=5, min_count=5, workers=multiprocessing.cpu_count())
        model.save(save_path)
        model.save_word2vec_format(save_path, binary=False)
        return model
    def analyze(self):
        pass

sas = SentimentAnalyzerSVM()