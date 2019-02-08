from os.path import join
import pandas as pd
from fuzzywuzzy import fuzz
from nltk.tokenize import TweetTokenizer

sample = pd.read_json(join('..', 'data', 'ner', 'sample_100_pages_names_tokens.json'))
sample = sample.reset_index(drop=True)
columns_for_index = ['matched_name', 'matched_title_str', 'matched_title_2_str', 'location']

tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)

sample[columns_for_index] = sample[columns_for_index].fillna("")

for col in columns_for_index:
    sample[col + '_tokens'] = sample[col].apply(tokenizer.tokenize)

sample['tokens'] = (sample['matched_name_tokens'] +
                sample['matched_title_str_tokens'] +
                sample['matched_title_2_str_tokens'] +
                sample['location_tokens'])


def ids_to_rows(ids):
    return sample[sample.apply(lambda x: x.id in ids, axis=1)]