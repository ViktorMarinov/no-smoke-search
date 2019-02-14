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
    ixs = set()
    for group in all_grs:
        if ix in group:
            ixs = group
            break
            
    return ixs_to_rows(list(ixs))

def get_ix_group(ix):
    for group in all_grs:
        if ix in group:
            return group
    
    return None

def find_groups_with_n_plus(n):
    return list(filter(lambda x: len(x) >= n, all_grs))

def find_if_in_groups_with_n_plus(n, ix):
    return any(filter(lambda x: len(x) >= n and ix in x, all_grs))

def get_groups_with_n_plus(rows, n):
    res_groups = []

    for ix in rows.index:
        if not any(map(lambda group: ix in group, res_groups)):
            group = get_ix_group(ix)
            if group and len(group) >= n:
                res_groups.append(group)

    return [ixs_to_rows(list(group)) for group in res_groups]

# groups_10_plus = find_groups_with_n_plus(10)

# for group in groups_10_plus:
#     print(ixs_to_rows(list(group)))