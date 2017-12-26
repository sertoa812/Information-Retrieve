def get_stop_words():
    stop_words_path = "DataSets/stopwords.txt"
    with open(stop_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]

#程度副词
def get_sentiment_score_words():
    adv_words_path = "DataSets/sentiment/adv.txt"
    with open(adv_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]
#情感词
def get_bosonNLP_words():
    bosonNLP_path = "DataSets/bosonNLP/BosonNLP_sentiment_score.txt"
    with open(bosonNLP_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]

#否定词
def get_not_words():
    not_words_path = "DataSets/nolist.txt"
    with open(not_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]