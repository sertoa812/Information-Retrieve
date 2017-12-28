def get_stop_words():
    stop_words_path = "stopwords.txt"
    with open(stop_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]

def check_contain_chinese(str):
    return '\u4e00' <= str <= '\u9fff'
#程度副词
def get_adv_words():
    adv_words_path = "DataSets/sentiment/adv.txt"
    with open(adv_words_path, 'rt', encoding='utf-8') as f:
        raw_list =  [line.replace('\n', '') for line in f]
    result = {}
    score = 0  # 一系列词的评分
    for line in raw_list:
        if line.isdigit():
            score = line
            continue
        else:
            result[line] = score
    return result
#情感词
def get_bosonNLP_words():
    bosonNLP_path = "DataSets/bosonNLP/BosonNLP_sentiment_score.txt"
    with open(bosonNLP_path, 'rt', encoding='utf-8') as f:
        raw_list =  [line.replace('\n', '') for line in f]
    result = {}
    for line in raw_list:
        str_score = line.split(' ')
        if check_contain_chinese(str_score[0]):
            result[str_score[0]] = str_score[1]
    return result

#否定词
def get_not_words():
    not_words_path = "DataSets/notlist.txt"
    with open(not_words_path, 'rt', encoding='utf-8') as f:
        raw_list = [line.replace('\n', '') for line in f]
    result = {}
    for line in raw_list:
        result[line] = '-1'
    return result

def get_word2vec_words():
    path1 = "DataSets/hotel_judgement/neg.txt"
    path2 = "DataSets/hotel_judgement/pos.txt"
    with open(path1, 'rt', encoding='utf-8') as f:
        raw_list1 = [line.replace('\n', '') for line in f]
    with open(path2, 'rt', encoding='utf-8') as f:
        raw_list2 = [line.replace('\n', '') for line in f]
    return raw_list1, raw_list2



