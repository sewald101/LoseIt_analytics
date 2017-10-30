import loseit_nlp as LNLP
from loseit_nlp import MatchPosts
import psycopg2


class OutputResults(object):
    """Prints results from MatchPosts.closest_matches
    INPUT:
    -- results_df: pandas df of N-highest similarities, indexed by post_id

    METHODS:
    -- print_results(): Prints formatted results of closet matching posts
    """
    def __init__(self, results_df):
        self.results_df = results_df
        self.scores = list(results_df.iloc[:,0])

    def print_results(self):
        for i, key in enumerate(list(self.results_df.index)):
            result = self.query_record(key)[0] # type(query output) = list
            print "\n=========================="
            print "Post_ID: {} -- Topic: {}\n".format(result[0], result[1])
            print "Posted by: {} on {}\n".format(result[2], result[3])
            print self.groom_post_body(result[4]) + '\n'
            print "Cosine_similarity: {}\n".format(self.scores[i])
            print "URL: {}\n".format(result[5])

    def query_record(self, post_id):
        conn = psycopg2.connect(dbname='loseit')
        cur = conn.cursor()
        query = """
                SELECT post_id
                 , topic
                 , name
                 , date_posted
                 , post_body
                 , page_url
                FROM posts
                WHERE post_id = '{}';
                """.format(post_id)
        cur.execute(query)
        self.record = cur.fetchall()
        conn.close()
        return self.record

    def groom_post_body(self, raw_text):
        """A custom function to clean the text before sending it into the vectorizer"""
        # get rid of newlines
        # self.text = raw_text.strip().replace("\n", " ")\
        #     .replace("\r", " ")
        self.text = raw_text.strip().replace("\r", " ")
        # replace HTML symbols
        self.text = self.text.replace("&amp;", "and")\
            .replace("&gt;", ">").replace("&lt;", "<")

        return self.text


# For reference...
query_corpus = """
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
