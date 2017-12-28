import os
def get_stop_words():
    stop_words_path = os.path.join(os.path.abspath('.'),"stopwords.txt")
    with open(stop_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]