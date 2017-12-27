import thulac
import os
stop_words_path = os.path.join(os.path.abspath('.'), 'stopwords.txt')
path1 = os.path.join(os.path.abspath('.'), 'neg.txt')
path2 = os.path.join(os.path.abspath('.'), 'pos.txt')
def get_stop_words():
    with open(stop_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]

def get_word2vec_words():
    with open(path1, 'rt', encoding='utf-8') as f:
        raw_list1 = [line.replace('\n', '') for line in f]
    with open(path2, 'rt', encoding='utf-8') as f:
        raw_list2 = [line.replace('\n', '') for line in f]
    return raw_list1, raw_list2

def token(sequence):
    stop_words = get_stop_words()
    thu1 = thulac.thulac(seg_only=True, filt=True)
    #thulac直接返回str，使用split切分为数组，然后去除停用词
    seq = thu1.cut(sequence, text=True).split(' ')
    seq_no_stop_words = [value for value in seq if value not in stop_words]
    return seq_no_stop_words

def generate_train_data():
    _, raw_text1= get_word2vec_words()
    raw_text1.extend(_)
    # 对每一个句子进行分词后添加到总的语料集中
    with open('train_datasets', 'at', encoding='utf-8') as f:
        for index, line in enumerate(raw_text1):
            corpus = ' '.join(token(line))
            corpus += '\n'
            f.write(corpus)

            if index %100 == 0: print(index)

generate_train_data()