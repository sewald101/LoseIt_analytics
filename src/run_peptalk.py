"""
Script for running Pep Talk
"""
from loseit_nlp import MatchPosts
from post_retriever import OutputResults
from sklearn.feature_extraction.text import TfidfVectorizer
from corpus_vec import tokenizeText
import cPickle as pickle

ids_10K = '../pickle_pantry/post_ids_10K.pickle'
corpus_vec_10K = '../pickle_pantry/corpus_vec_10K.pickle'
model_10K = '../pickle_pantry/model_10K.pickle'

ids_20K = '../pickle_pantry/post_ids_20K.pickle'
corpus_vec_20K = '../pickle_pantry/corpus_vec_20K.pickle'
model_20K = '../pickle_pantry/model_20K.pickle'

ids_master = '../pickle_pantry/post_ids.pickle'
corpus_master = '../pickle_pantry/corpus_vec.pickle'
model_master = '../pickle_pantry/model.pickle'

ids_10K_normed = '../pickle_pantry/post_ids_10K_n.pickle'
corpus_vec_10K_normed = '../pickle_pantry/corpus_vec_10K_n.pickle'
model_10K_normed = '../pickle_pantry/model_10K_n.pickle'

ids_100_normed = '../pickle_pantry/post_ids_100_n.pickle'
corpus_vec_100_normed = '../pickle_pantry/corpus_vec_100_n.pickle'
model_100_normed = '../pickle_pantry/model_100_n.pickle'

def run_peptalk():
        with open (ids_10K, 'rb') as f:
            ids = pickle.load(f)
        with open (corpus_vec_10K, 'rb') as f:
            arr = pickle.load(f)
        with open (model_10K, 'rb') as f:
            model = pickle.load(f)

        # User inputs journal entry and number of desired results
        j_entry = raw_input("What's going on? (type journal entry): >>\n")
        N = int(raw_input("How many results would you care to view?: >>" ))

        # Corpus is searched, results are printed
        search = MatchPosts(ids, arr, model, j_entry, N=N)
        results_df = search.match_posts()
        output = OutputResults(results_df)
        output.print_results()

if __name__=='__main__':
    # Loading corpus post_ids, tfidf array and pre-fitted model
    with open (ids_100_normed, 'rb') as f:
        ids = pickle.load(f)
    with open (corpus_vec_100_normed, 'rb') as f:
        arr = pickle.load(f)
    with open (model_100_normed, 'rb') as f:
        model = pickle.load(f)

    # User inputs journal entry and number of desired results
    j_entry = raw_input("What's going on? (type journal entry): >>\n")
    N = int(raw_input("How many results would you care to view?: >>" ))

    # Corpus is searched, results are printed
    search = MatchPosts(ids, arr, model, j_entry, N=N)
    results_df = search.match_posts()
    output = OutputResults(results_df)
    output.print_results()
