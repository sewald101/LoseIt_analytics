

"""
Utilities to facilitate pipeline for Lose It! forum data

CLASSES:
-- URLGenerator

FUNCTIONS:
-- process_collections
-- insert_posts_to_sql
-- insert_query
-- tuplefy_posts
-- write_topic_urls
"""

from pymongo import MongoClient
import psycopg2
from psycopg2.extensions import AsIs
import psycopg2.extras
from loseit_parser import LoseItPostParser, LoseItCatalogParser


def process_collections(coll, table):
    """Iterates over Mongodb collections of Lose It forum pages to
    parse and insert messages into sql
    ARGUMENTS:
     -- coll: Mongodb cursor in form coll = coll.find({})
     -- table: table in sql db for insertion of records (string)
    """
    psy2_conn = psycopg2.connect(dbname='loseit', host='localhost')
    psy2_cur = psy2_conn.cursor()
    insert_q = insert_query('table')
    counter = 0
    for doc in coll:
        insert_posts_to_sql(doc, psy2_cur, insert_q)
        counter += 1
        print 'Documents processed: {}'.format(counter)
        if counter % 50 == 0:
            psy2_conn.commit()
    psy2_conn.commit()
    print "\nCOLLECTION PROCESSED\n"
    psy2_conn.close()


def insert_posts_to_sql(doc, cursor, query):
    """
    ARGUMENTS:
     -- doc: A single Mongodb document corresponding to unique Lose It forum url
     -- cursor: pyschopg2 cursor of form cur = conn.cursor
     -- query: insert query for psycopg2 cursor (str, use insert_query function)
    """
    pipe = LoseItPostParser(doc['html'], doc['url'])
    pipe.parse_page()
    posts = pipe.posts_lst
    posts_tup = tuplefy_posts(posts)
    psycopg2.extras.execute_values(cursor, query, posts_tup)
    # psy2_conn.commit()
    print('Added to database: {}'.format(doc['url']))

# Query to insert tuplefied posts into SQL
def insert_query(sql_table):
    """Returns an query string for inserting records into specified sql_table
    ARGUMENT: sql_table: (string)
    """
    query = """
    INSERT INTO {} (
      topic,
      topic_id,
      page_idx,
      post_idx,
      post_id,
      date_posted,
      name,
      author_id,
      joined,
      ttl_posts,
      post_body,
      cited,
      quotation,
      library,
      page_url
      )
    VALUES
      %s
    ;
    """.format(sql_table)
    return query

def tuplefy_posts(posts_lst):
    """Converts parsed dictionaries to a list of tuples for consumption by
    psycopg2.extras.execute_values method
    """
    return [(
      post['topic'],
      post['topic_id'],
      post['page_idx'],
      post['post_idx'],
      post['post_id'],
      post['date_posted'],
      post['name'],
      post['author_id'],
      post['joined'],
      post['ttl_posts'],
      post['post_body'],
      post['cited'],
      post['quotation'],
      post['library'],
      post['page_url']
    ) for post in posts_lst]


class URLGenerator(object):
    """
    Takes in Lose It! landing page url. Increments new urls and writes all to file.

    Returns and writes landing page plus a series of urls incremented by
    message-per-page in the following format, per Lose It! convention:

    Landing page URL format:
        'https://forums.loseit.com/posts/list/18808.page'

    Incremented URL format:
        'https://forums.loseit.com/posts/list/<page increment>/18808.page'

    PARAMETERS:
        - landing_page_url: (string) format:
              'https://forums.loseit.com/posts/list/18808.page'
        - output_file (string): path/output_file
        - increment: (int), message-per-page intervals by which urls are
               incremented (default 15)
        - incl_landing: (bool) writes landing page url to file before writing
               incremented urls (default=True)

    NOTE: MUST TAKE EITHER OF THE FOLLOWING PARAMETERS; NOT BOTH.

        - end_page_url: (string), if provided, page element used to specify upper
            page limit to which intermediate pages are incremented (default None)
        - iterations: (int), if end_page not provided, specifies number of
            incremented pages to be added beyond landing page (default None)

    USE AND METHODS:
        - All parameters are defined at instantiation.
        _ Run object.url_writer() to execute and write to output_file.
    """

    def __init__(self, landing_page_url, output_file, increment=15,
        end_page_url=None, iterations=None, incl_landing=True):

        self.landing_page_url = landing_page_url
        self.output_file = output_file
        self.increment = increment
        self.end_page_url = end_page_url
        self.iterations = iterations
        self.incl_landing = incl_landing

    def url_writer(self):
        """Constructs and writes URLs to output file."""
        if self.incl_landing:
            with open(self.output_file, 'w') as f:
                f.write(self.landing_page_url + '\n')

        if self.iterations:
            with open(self.output_file, 'a') as f:
                for num in range(self.increment,
                                 self.increment*(self.iterations+1),
                                 self.increment):
                    page_url = (self.insert_curly_bracket()).format(num)
                    f.write(page_url + '\n')
                f.write('\n')

        if self.end_page_url:
            if self.end_page_url[-4:] == 'page': # BANDAID -- ANOMOUS DOCUMENT BREAKS HERE
                with open(self.output_file, 'a') as f:
                    for num in range(self.increment,
                                     self.extract_end_page_idx(),
                                     self.increment):
                        page_url = (self.insert_curly_bracket()).format(num)
                        f.write(page_url + '\n')
                    f.write(self.end_page_url)
                    f.write('\n')

    def insert_curly_bracket(self):
        """Takes in landing_page_url (str) and inserts '{}' for incrementing"""
        _q = self.landing_page_url.split('/')
        _q.insert(-1, '{}')
        _q = '/'.join(_q)
        return _q

    def extract_end_page_idx(self):
        print self.end_page_url
        _r = self.end_page_url.split('/')
        return int(_r[-2])


def write_sub_urls(coll, output_f, initialize_mc=False):
    """
    INPUTS:
    -- coll: specifies mongo_db collection from wh/ urls will be parsed (string)
    -- output_f: path/file to which urls are written (string)
    -- (optional) initialize_mc: initializes MongoClient (default=False)

    OUTPUT: urls of multi-page threads written to output file
    """
    if initialize_mc:
        mc = MongoClient()
    db = mc['lose_it']
    coll = db[coll]
    docs = coll.find({})

    with open(output_f, 'a') as f:
        for doc in docs:
            print "Parsing: {}".format(doc['url'])
            parsed = LoseItPostParser(doc['html'], doc['url'])
            parsed.parse_page()
            if parsed.last_pg_url != None:
                q = URLGenerator(
                    doc['url'],
                    output_f,
                    end_page_url=parsed.last_pg_url,
                    incl_landing=False
                )
                q.url_writer()

            else: continue

    print "\nPROCESSING COMPLETE"



def write_topic_urls(library, mongo_db, collection, write_file):
    """From LoseItCatalogParser.topics_lst, writes topic landing_pg urls
    to file

    PARAMETERS:
    -- library: name of library from which documents scraped (string)
    -- mongo_db: mongo database name (string)
    -- collection: mongo db collection containing library documents (string)
    -- write_file: path/file.txt to which topic urls are written (string)
    """
    mc = MongoClient()
    db = mc[mongo_db]
    coll = db[collection]

    with open(write_file, 'w') as f:
        for doc in coll.find({}):
            libr_pg_parsed = LoseItCatalogParser(library, doc['html'], doc['url'])
            libr_pg_parsed.parse_page()
            for topic in libr_pg_parsed.topic_lst[:10]:
                f.write(topic['landing_url'] + '\n')


if __name__=='__main__':

    test_landing_page_url = 'https://forums.loseit.com/posts/list/18808.page'
    test_end_page = 'https://forums.loseit.com/posts/list/1965/18808.page'
    test_output_file = '../data/test_url_compiled.txt'

    kit_sink_landing = 'https://forums.loseit.com/forums/show/6.page'
    kit_sink_end_page = 'https://forums.loseit.com/forums/show/9350/6.page'

    diet_nut_landing = 'https://forums.loseit.com/forums/show/4.page'
    diet_nut_end_page = 'https://forums.loseit.com/forums/show/10650/4.page'

    fit_ex_landing = 'https://forums.loseit.com/forums/show/3.page'
    fit_ex_end_page = 'https://forums.loseit.com/forums/show/8175/3.page'

    test_writer = URLGenerator(test_landing_page_url,
                               test_output_file,
                               end_page_url=test_end_page)
    test_writer.url_writer()
