"""
FUNCTIONS to query, clean, tokenize, model-fit, tfidf-vectorize corpus of Lose It!
posts.
-- tokenizeText(archive)
-- cleanText(text)
-- corpus_df(model, q_results)

GLOBAL VARIABLES:
-- PARSER: spaCy English parser
-- STOPLIST: custom list of stopwords (set)
-- SYMBOLS: custom list of punctuation and accent marks (list)

"""

import numpy as np
import pandas as pd

import psycopg2
import spacy
from spacy.en import English

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import string

import cPickle as pickle

"""
GLOBAL VARIABLES
"""
PARSER = English()

# A custom stoplist
STOPLIST = set(
    stopwords.words('english')\
    + ["n't", "'s", "'m", "ca"]\
    + list(ENGLISH_STOP_WORDS)
    )

# List of symbols we don't care about
# Keeping explanation points and questions marks as potential features for matching
SYMBOLS = " ".join(string.punctuation).split(" ")
SYMBOLS.pop(SYMBOLS.index('!'))
SYMBOLS.pop(SYMBOLS.index('?'))

def tokenizeText(archive):
    """ A custom function to tokenize the text using spaCy;
    deploy in TfidfVectorizer model definition: tokenizer=tokenizeText
    """
    tokens = PARSER(archive)
    # lemmatize
    lemmas = []
    for tok in tokens:
        lemmas.append(tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_)
    tokens = lemmas
    tokens = [tok for tok in tokens if tok not in STOPLIST]
    tokens = [tok for tok in tokens if tok not in SYMBOLS]

    # remove large strings of whitespace
    while "" in tokens:
        tokens.remove("")
    while " " in tokens:
        tokens.remove(" ")
    while "\n" in tokens:
        tokens.remove("\n")
    while "\n\n" in tokens:
        tokens.remove("\n\n")
    return tokens


TFIDFER = TfidfVectorizer(tokenizer=tokenizeText,
                          min_df=0.001,
                          stop_words=STOPLIST,
                          decode_error='ignore',
                          norm=None)


def cleanText(text):
    """A custom function to clean the text before sending it into the vectorizer"""
    # get rid of newlines
    text = text.strip().replace("\n", " ")\
        .replace("\r", " ")\
        .replace("\'ll", " will")\
        .replace("\'ve", " have")
    # replace HTML symbols
    text = text.replace("&amp;", "and").replace("&gt;", ">").replace("&lt;", "<")
    text = text.lower()

    return text


def corpus_df(model, q_results):
    """
    Takes in globally-defined TfidfVectorizer object and queried results;
    Returns pandas df and sparse matrix of tfidf matrix, and fitted model
    INPUT:
    -- model: parameterized, unfitted TfidfVectorizer object
    -- q_results: list of tuples resulting from psychopg2 query (see reference
        queries below)

    OUTPUT: (tuple)
    -- post_ids: IDs of each post in the corpus (list)
    -- tfidf_M: matrix of tfidf-vectorized posts (numpy sparse matrix)
    -- model: TfidfVectorizer object fit to corpus
    """
    post_ids = [result[0] for result in q_results]
    raw_texts = [result[6].decode('utf-8') for result in q_results]
    cleaned_texts = [cleanText(text) for text in raw_texts]
    model = TFIDFER.fit(cleaned_texts)
    tfidf_M = TFIDFER.transform(cleaned_texts)

    return post_ids, tfidf_M, model

if __name__=='__main__':
    """Query and vectorize corpus; pickle post_ids, tfidf sparse matrix
    and fitted vectorizer (model)
    """
    conn = psycopg2.connect(dbname='loseit', host='localhost')
    cur = conn.cursor()
    query = """
            SELECT DISTINCT(post_id) AS post_id
              , topic_id
              , topic
              , name
              , author_id
              , date_posted
              , post_body
              , library
              , page_url
              , post_idx
            FROM posts
            ORDER BY topic_id, post_idx
            LIMIT 10000;
            """
    cur.execute(query)
    corpus = cur.fetchall()

    ids, arr, model = corpus_df(TFIDFER, corpus)

    ids_10K = '../pickle_pantry/post_ids_10K.pickle'
    corpus_vec_10K = '../pickle_pantry/corpus_vec_10K.pickle'
    model_10K = '../pickle_pantry/model_10K.pickle'

    ids_20K = '../pickle_pantry/post_ids_20K.pickle'
    corpus_vec_20K = '../pickle_pantry/corpus_vec_20K.pickle'
    model_20K = '../pickle_pantry/model_20K.pickle'

    ids_master = '../pickle_pantry/post_ids.pickle'
    corpus_master = '../pickle_pantry/corpus_vec.pickle'
    model_master = '../pickle_pantry/model.pickle'

    with open (ids_10K, 'wb') as f:
        pickle.dump(ids, f)

    with open (corpus_vec_10K, 'wb') as f:
        pickle.dump(arr, f)

    with open (model_10K, 'wb') as f:
        pickle.dump(model, f)

    conn.close()
    print "Number of posts: {}".format(len(ids))
    print "Type of model object: {}".format(type(model))
