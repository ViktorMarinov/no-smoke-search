import load_sample
import pandas as pd
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from os.path import join
from copy import deepcopy
import time
import datetime
from queue import LifoQueue
import pickle

sample = load_sample.sample
ids_to_rows = load_sample.ids_to_rows
ixs_to_rows = load_sample.ixs_to_rows

stopwords_sample = pd.read_json(join('..', 'data', 'index', 'stopwords-bg.json'))[259:]
short_stop_word = stopwords_sample[stopwords_sample[0].apply(lambda x: len(x) <= 3)][0]

search_tokens_text = sample['tokens'].apply(lambda x: ' '.join(x))

tfidf_vectorizer = TfidfVectorizer(stop_words=short_stop_word.tolist())
tfidf_vectorizer.fit_transform(search_tokens_text)

train_corpus_vectors = tfidf_vectorizer.transform(search_tokens_text)

def time_now():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

print(time_now(), "Loading corpus similarity")

try:
    dup_pairs_df = pd.read_json(join('data', 'dup_pairs.json'), orient='split')
    dup_pairs = [tuple(x) for x in dup_pairs_df.values]
except:
    print(time_now(), "Count not read 'data/dup_pairs.json'. Creating...")
    duplicates = cosine_similarity(train_corpus_vectors, train_corpus_vectors)
    dup_pairs = []

    for i in range(len(sample)):
        for j in range(len(sample)):
            if duplicates[i, j] >= 0.9 and i < j:
                dup_pairs.append((i, j))

    DataFrame(data=dup_pairs).to_json(join('data', 'dup_pairs.json'), orient='split')
    dup_pairs_df = pd.read_json(join('data', 'dup_pairs.json'), orient='split')

print(time_now(), "Loading ready:", len(dup_pairs), " pairs loaded.")


def has_more(tuples, ix):
    return any(filter(lambda x: x[0] == ix or x[1] == ix, tuples))

def find_first(tuples, ix):
    return next((x[0] for x in tuples if x[1] == ix), None)

def get_dups_group_iter(tuples, ix):
    group = set()
    queue = LifoQueue()
    queue.put(ix)
    visited = set()
    while not queue.empty():
        current = queue.get()
        group.add(current)
        for i, (ix1, ix2) in enumerate(tuples):
            if i in visited:
                continue

            if ix1 == current:
                visited.add(i)
                queue.put(ix2)
            elif ix2 == current:
                visited.add(i)
                queue.put(ix1)

    return group


starters = set(map(lambda x: x[0], dup_pairs))

def find_all_groups(tuples, ixs):
    all_groups = list()
    l = len(starters)
    for i, ix in enumerate(starters):
        print("{0:0.2f}".format(float(i) * 100/ l) , " %")
        if not any(map(lambda group: ix in group, all_groups)):
            all_groups.append(get_dups_group_iter(dup_pairs, ix))
        
    return all_groups

print(time_now(), "Groups loading...")
all_grs = find_all_groups(dup_pairs, starters)

with open(join('data', 'dup_groups.p'), 'wb') as fp:
    pickle.dump(all_grs, fp, protocol=pickle.HIGHEST_PROTOCOL)


# with open(join('data', 'dup_groups.p'), 'rb') as fp:
#     data = pickle.load(fp)
#     if data ==


print(time_now(), "Done...")
