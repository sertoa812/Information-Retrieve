import thulac
import os
import json
stop_words_path = os.path.join(os.path.abspath('.'), 'stopwords.txt')
root_dir = os.path.join(os.path.abspath('.'), 'result')
def get_stop_words():
    with open(stop_words_path, 'rt', encoding='utf-8') as f:
        return [line.replace('\n', '') for line in f]

def get_data():
    for index, lists in enumerate(os.listdir(root_dir)):
        path = os.path.join(root_dir, lists)
        try:
            deal_one_document(path)
        except:
            continue
        print(index)

def token(sequence):
    stop_words = get_stop_words()
    thu1 = thulac.thulac(seg_only=True, filt=True)
    seq = thu1.cut(sequence, text=True).split(' ')
    seq_no_stop_words = [value for value in seq if value not in stop_words]
    return seq_no_stop_words

def deal_one_document(path):
    with open (path, 'rt', encoding='utf-8') as f:
        data = json.loads(f.read())
        list = [data['text'].replace('\n','').replace('\xa0','')]
        comments = data['comment']
        for comment in comments:
            list.append(comment['content'])
    #list = ['a','b']
    with open('news_tokend_datasets', 'at', encoding='utf-8') as f:
        for index, line in enumerate(list):
            corpus = ' '.join(token(line))
            corpus += '\n'
            f.write(corpus)
    os.remove(path)

get_data()