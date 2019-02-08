from . import load_sample
import nltk
from operator import itemgetter
from collections import defaultdict
from functools import reduce
import operator
from fuzzywuzzy import fuzz
from nltk.tokenize import TweetTokenizer

tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)

sample = load_sample.sample
ids_to_rows = load_sample.ids_to_rows

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
    if not words:
        return dict()

    occurences = [{id: freq for id, freq in postings[word]} for word in words]
    common = reduce(
        set.intersection,
        [{id for id, freq in occ.items()} for occ in occurences])
    return {id: sum([occ[id] for occ in occurences]) for id in common}

names_tokens = (sample['matched_name_tokens'] +
                   sample['matched_title_str_tokens'] +
                   sample['matched_title_2_str_tokens'])
matched_title_words = set(sum(list(names_tokens), []))
location_words = set(sum(list(sample['location_tokens']), []))
token_words = set(sum(list(sample['tokens']), []))

def find_closest_word(word, words):
    suggested_word = None
    min_coeff = 70
    for w in words:
        fuzz_coeff = fuzz.ratio(w, word)
        if fuzz_coeff > min_coeff:
            min_coeff = fuzz_coeff
            suggested_word = w
    return suggested_word

def parse_query(query_string):
    words = tokenizer.tokenize(query_string)

    words_to_use = []
    suggestions = []
    for w in words:
        if w in token_words:
            words_to_use.append(w)
            suggestions.append(w)
        else:
            cw = (find_closest_word(w, matched_title_words)
                or find_closest_word(w, location_words))
            if cw: 
                suggestions.append(cw)

    if words_to_use == suggestions:
        return words_to_use, []

    return words_to_use, suggestions
    
def find_matches(words):
    id_dict = and_query(words)
    sorted_by_freq = sorted(id_dict.items(), key=operator.itemgetter(1), reverse=True)
    ids = [id for id, freq in sorted_by_freq]
    return ids_to_rows(ids)

