import sklearn
import GetDataSets
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import thulac
import os
import multiprocessing
import numpy as np
from sklearn import svm
from sklearn.decomposition import PCA
from sklearn.externals import joblib

global_train_num = 2000
global_test_num = 2000

# word2vector model using the news content to train
# svm model still using the hotel comments content to train
def token(sequence):
    stop_words = GetDataSets.get_stop_words()
    thu1 = thulac.thulac(seg_only=True, filt=True)
    seq = thu1.cut(sequence, text=True).split(' ')
    seq_no_stop_words = [value for value in seq if value not in stop_words]
    return seq_no_stop_words

# gather news_tokend_datasets and train_datasets2 together to news_tokend_datasets
def gather_train_data():
    with open('../train_datasets2', 'rt', encoding='utf-8') as f:
        lines = f.readlines()
    with open('../news_tokend_datasets', 'at', encoding='utf-8') as f:
        f.writelines(lines)

def word2vector():
    outp1 = 'Models/word2vector.model'
    if not os.path.isfile(outp1):
        model = Word2Vec(LineSentence('../news_tokend_datasets'), size = 128, window=5, min_count=10, workers=multiprocessing.cpu_count())
        model.save(outp1)
    else:
        model = Word2Vec.load(outp1)
    return model

# neg datasets max 5000
# pos datasets 5000 15000
def get_train_test_data(train_num, test_num):
    file = 'hotel_tokend_datasets'
    with open(file, 'rt', encoding='utf-8') as f:
        lines = f.readlines()
        neg_train_list = lines[0:3500]
        neg_test_list = lines[3500:4900]
        pos_train_list = lines[5000:8500]
        pos_test_list = lines[12000:13900]
    return pos_train_list, pos_test_list, neg_train_list, neg_test_list

def getWordVecs(sentence, model):
    vecs = []
    sen = sentence.replace('\n','')
    for word in sen.split(' '):
        try:
            vecs.append(model[word])
        except KeyError:
            continue
            # vecs = np.concatenate(vecs)
    return np.array(vecs, dtype='float')

# for svm training
def generate_sentence_vector(train_num, test_num):
    #对每一个词进行分词，计算句子向量
    pos_train, pos_test, neg_train, neg_test = get_train_test_data(train_num, test_num)
    pos_train_vector = []
    pos_test_vector = []
    neg_train_vector = []
    neg_test_vector = []
    #import word2vector model
    model = word2vector()

    input = [pos_train, pos_test, neg_train, neg_test]
    output = [pos_train_vector, pos_test_vector, neg_train_vector, neg_test_vector]
    print(input)

    for index in range(0,4):
        for sentence in input[index]:
            resultList = getWordVecs(sentence, model)
            # for each sentence, the mean vector of all its vectors is used to represent this sentence
            if len(resultList) != 0:
                resultArray = sum(np.array(resultList)) / len(resultList)
                output[index].append(resultArray.tolist())
    del input
    input_train = [pos_train_vector, neg_train_vector]
    input_test = [pos_test_vector, neg_test_vector]

    train_vector_x = []
    train_vector_y = []
    test_vector_x = []
    test_vector_y = []
    # generate train_vector
    for index,data in enumerate(input_train):
        if index == 0:
            for line in data :
                train_vector_x.append(line)
                train_vector_y.append('1')
        else:
            for line in data :
                train_vector_x.append(line)
                train_vector_y.append('-1')

    #generate test_vector
    for index,data in enumerate(input_test):
        if index == 0:
            for line in data :
                test_vector_x.append(line)
                test_vector_y.append('1')
        else:
            for line in data :
                test_vector_x.append(line)
                test_vector_y.append('-1')

    return train_vector_x, train_vector_y, test_vector_x, test_vector_y

def generate_svm():
    model_name = 'Models/svm.model'
    if not os.path.isfile(model_name):
        train_vector_x, train_vector_y, test_vector_x, test_vector_y = generate_sentence_vector(train_num=global_train_num, test_num=global_test_num)
        clf = svm.SVC(kernel='rbf', C=1.0, gamma=1.25, cache_size=1000)
        clf.fit(train_vector_x, train_vector_y)
        right_count = 0
        for index, value in enumerate(test_vector_x):
            value_wrapper = [value]
            result = clf.predict(value_wrapper)
            if test_vector_y[index] == result:
                right_count += 1
        print(right_count, ' ', len(test_vector_x))
        svm_model = joblib.dump(clf,model_name)
    else:
        svm_model = joblib.load(model_name)
    return svm_model

generate_svm()