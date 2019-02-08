import pandas as pd
import nltk
from nltk.tokenize import TweetTokenizer
from operator import itemgetter
from collections import defaultdict
import numpy as np
from functools import reduce
import operator

sample = pd.read_json('data/sample_100_pages_names.json')

columns_for_index = ['matched_name', 'matched_title', 'matched_title_2', 'location']

tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)

sample[columns_for_index] = sample[columns_for_index].fillna("")

for col in columns_for_index:
    sample[col + '_tokens'] = sample[col].apply(tokenizer.tokenize)

sample['tokens'] = sample['matched_name_tokens'] + sample['matched_title_tokens'] + sample['matched_title_2_tokens'] + sample['location_tokens']
print(sample['location_tokens'])
def get_report(row):
    return row[1]

def get_token_report_id_pairs(reports):
    pairs = []
    for report in reports:
        pairs += [(token, report.id) for token in report.tokens]
            
    return pairs
    
    
token_id_pairs = get_token_report_id_pairs(map(get_report, sample[['id', 'tokens']].iterrows()))
sorted_token_id = sorted(token_id_pairs, key=itemgetter(0))

def merge_token_in_report(sorted_token_id):
    token_id_freq = []
    for token, id in sorted_token_id:
        if token_id_freq:
            prev_tok, prev_id, prev_freq = token_id_freq[-1]
            if prev_tok == token and prev_id == id:     
                token_id_freq[-1] = (token, id, prev_freq+1)
            else:
                token_id_freq.append((token, id, 1))
        else:
            token_id_freq.append((token, id, 1))
    return token_id_freq

token_id_freq = merge_token_in_report(sorted_token_id)

dictionary = defaultdict(lambda: (0, 0))
postings = defaultdict(lambda: [])

#fill in dictionary
for token, id, freq in token_id_freq:
    dictionary[token] = (dictionary[token][0] + 1, dictionary[token][1] + freq)

#fill in postings
for token, id, freq in token_id_freq:
    postings[token].append((id, freq))

# Sort the postings
for key, values in postings.items():
    postings[key] = sorted(values, key=itemgetter(0))

def and_query(words):
    """
    Finds all the documents that contain all the words with the frequescies summed
    """
    occurences = [{id: freq for id, freq in postings[word]} for word in words]
    common = reduce(
        set.intersection,
        [{id for id, freq in occ.items()} for occ in occurences])
    return {id: sum([occ[id] for occ in occurences]) for id in common}


def parse_query(query_string):
    words = tokenizer.tokenize(query_string)
    print("Searching for: ", words)
    return words
    
def find_matches(words):
    id_dict = and_query(words)
    sorted_by_freq = sorted(id_dict.items(), key=operator.itemgetter(1), reverse=True)
    ids = [id for id, freq in sorted_by_freq]
    return sample[sample.apply(lambda x: x.id in ids, axis=1)]
