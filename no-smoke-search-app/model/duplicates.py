from . import load_sample
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from os.path import join

sample = load_sample.sample
ids_to_rows = load_sample.ids_to_rows

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