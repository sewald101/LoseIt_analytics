
import numpy as np
import pandas as pd

import psycopg2
import spacy
from spacy.en import English

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import corpus_vec

"""
CLASS:
-- MatchPosts(corpus_df, model, j_entry, N=3): executes matching of journal
    entry to archived, vectorized posts via match_posts() method.

REFERENCES: SQL queries with results formatted for above-listed functions
"""

class MatchPosts(object):
    """
    Returns a pandas dataframe of N-closest matches (post_ids) between archived
    posts and user's journal entry.

    ARGUMENTS:
    -- post_ids: (list)
    -- corpus_vec: (numpyp sparse arr) array of corpus tfidf signatures
    -- model: sklearn TfidfVectorizer pre-trained on archive
    -- N: (int) number of closest matches to return (default = 3)
    -- j_entry: (str) user journal entry via raw_input

    ATTRIBUTES:
    -- rows, cols: (int) dimesions of archive arrays
    -- j_tfidf: (1-D numpy arr) tfidf vector for journal entry
    -- result_df: (pandas df) cosine_similarities between corpus and journal
    -- closest_matches: selection of N-top results from result_df

    METHODS:
    -- match_posts(): run with no arguments to return list of N closest match post ids
    """
    def __init__(self, post_ids, corpus_vec, model, j_entry, N=3):
        self.post_ids = post_ids
        self.corpus_vec = corpus_vec
        self.model = model
        self.j_entry = j_entry
        self.N = N
        self.rows, self.cols = corpus_vec.shape
        self.corpus_df = None
        self.j_tfidf = None
        self.j_M = None
        self.results_df = None
        self.closest_matches = None

    def match_posts(self):
        """Script to execute all methods of the class"""
        self.corpus_to_df()
        self.journal_tfidf()
        self.tile_j_M()
        self.cos_sim_vector()
        self.generate_results()
        return self.closest_matches

    def generate_results(self):
        """Constructs pandas df of cos_similaries, indexed by post_id,
        and returns top N closest matches
        """
        cols = ['cos_sim']
        self.results_df = pd.DataFrame(
                                self.similarities,
                                index=self.corpus_df.index,
                                columns=cols
            ).sort_values(by='cos_sim', ascending=False)
        self.closest_matches = self.results_df[:self.N]        #print self.closest_matches

    def cos_sim_vector(self):
        """
        Calcuates cosign_sim between journal entry signature and each archived message.
        Outputs a vector of results.
        """
        sim_M = cosine_similarity(self.corpus_df, self.j_M)
        self.similarities = sim_M[:,0]

    def tile_j_M(self):
        """Takes in 1_D array; tiles to length of archive for cosign_sim calculation"""
        self.j_M = np.tile(self.j_tfidf, self.rows).reshape(self.rows, self.cols)

    def journal_tfidf(self):
        """Vectorizes journal entry w model pre-fit to archive
        """
        j_vec = self.model.transform([self.groom_journal(self.j_entry)])
        self.j_tfidf = np.array(j_vec.todense())

    def groom_journal(self, text):
        """Preps journal entry for tfidf vectorization"""
        # get rid of newlines
        text = text.strip().replace("\n", " ")\
            .replace("\r", " ")\
            .replace("\'ll", " will")\
            .replace("\'ve", " have")
        text = text.lower()
        return text

    def corpus_to_df(self):
        """Constructs pandas df for indexing results by post_id
        """
        cols = self.model.vocabulary_
        self.corpus_df = pd.DataFrame(
            self.corpus_vec.todense(),
            index=self.post_ids,
            columns=cols
            )

"""
REFERENCE DEFINITIONS
"""

query_archive = """
    SELECT post_id
      , topic_id
      , topic
      , name
      , author_id
      , date_posted
      , post_body
      , library
      , page_url
    FROM posts
    WHERE topic_id=36492
    ORDER BY post_idx;
"""

query_main = """
    SELECT DISTINCT(post_id) as post_id,
      , topic_id
      , topic
      , name
      , author_id
      , date_posted
      , post_body
      , library
      , page_url
    FROM posts
    GROUP BY post_id
    ORDER BY post_idx;
"""
