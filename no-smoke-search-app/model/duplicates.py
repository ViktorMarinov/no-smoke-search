from . import load_sample
import pandas as pd
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from os.path import join
from copy import deepcopy
import time
import datetime
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

def find_group(df_ix):
    group = cosine_similarity(train_corpus_vectors[df_ix], train_corpus_vectors)[0]
    
    dup_tuples = []
    dub_ids = []

    for j in range(len(group)):
        if group[j] >= 0.9:
            dup_tuples.append(j)
            
    for ix in dup_tuples:
        dub_ids.append(sample.loc[ix]['id'])
            
    return dub_ids

def find_similar(id):
    ix = id_to_index(id)
    ids = find_group(ix)
    return ids_to_rows(ids)

def id_to_index(id):
    return sample[sample.id == id].index[0]

## Soft duplicates

def time_now():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

print(time_now(), "Loading corpus similarity")

with open(join('data', 'dup_groups.p'), 'rb') as fp:
    all_grs = pickle.load(fp)

print(time_now(), "Done...")

def find_similar_2(id):
    ix = id_to_index(id)
    print("Index of ", id, " is ", ix)
    ixs = set()
    for group in all_grs:
        if ix in group:
            ixs = group
            break
            
    return ixs_to_rows(list(ixs))


# for group in all_grs:
#     if 6184 in group:
#         print(ixs_to_rows(list(group))[['id', 'tokens', 'title', 'location']])


# def find_groups_with_n_plus(groups, n):
#     return set(filter(lambda x: len(x) >= n, groups)) # can be changes to ==

# def find_if_in_groups_with_n_plus(groups, n, ix):
#     return any(filter(lambda x: len(x) >= n and ix in x, groups))