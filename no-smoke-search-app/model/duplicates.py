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

def get_dups_group(tuples, ix, group=[]):
    group.append(ix)
    for i, (ix1, ix2) in enumerate(tuples):
        if ix1 == ix:
            del tuples[i]
            get_dups_group(tuples, ix2, group)
        elif ix2 == ix:
            del tuples[i]
            get_dups_group(tuples, ix1, group)
            
    return frozenset(group)

from queue import LifoQueue

def get_dups_group_iter(tuples, ix):
    group = []
    queue = LifoQueue()
    queue.put(ix)
    visited = set()
    while not queue.empty():
        current = queue.get()
        group.append(current)
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



def find_number_of_duplicates(tuples, ix):
    tuples_copy = deepcopy(tuples)
    return get_dups_group_iter(tuples_copy, ix)

def find_similar_2(id):
    ix = id_to_index(id)
    print(ix)
    ixs = find_number_of_duplicates(dup_pairs, ix)
    return ixs_to_rows(ixs)


print(time_now(), "Groups loading...")

with open(join('data', 'dup_groups.p'), 'rb') as fp:
    all_grs = pickle.load(fp)

print(len(all_grs))
print(time_now(), "Done...")

# def find_groups_with_n_plus(groups, n):
#     return set(filter(lambda x: len(x) >= n, groups)) # can be changes to ==

# def find_if_in_groups_with_n_plus(groups, n, ix):
#     return any(filter(lambda x: len(x) >= n and ix in x, groups))