"""
2017-10-08
Customized from Alex Sanchez (github.com/exchez/thread_scrape.py)
"""

from multiprocessing import dummy
import requests
import pymongo
import time

# install mongo db via url below
# https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
mc = pymongo.MongoClient()
db = mc['lose_it']
collection = db['test_pages']

# gather a list of urls to scrape and give them some index number e.g. (234, 'http://www.site.com')
all_index_url_tuples = urls_with_indexes

# make a set of ids that you already have in your mongo db
existing_url_ids = db.collection.find({}, {'id': 1})
existing_url_ids = set([i['id'] for i in existing_url_ids])

# make a set of remaining ids left to scrape
all_ids = set([int(item[0]) for item in all_index_url_tuples])
remaining_ids = all_ids.difference(existing_url_ids)

remaining_id_url_tuples = [item for item in all_index_urls_tuples if int(item[0]) in remaining_ids]

def scrape_site(index_url_tuple):
    try:
        index, url = index_url_tuple
        res  = requests.get(url)
        collection.insert_one({'id': index, 'html': res.content.decode(), 'status': res.status_code})
        print("Item:", index, res.status_code) # print to console to monitor in real time and see if you're getting a code other than 200
        time.sleep(1) # this will depend on what you think you can get away with
    except:
        print("ERROR") # this, is if the connection gets refused
        time.sleep(5)

def concurrent_scrape(remaining_id_url_tuples):
    pool = dummy.Pool(processes=8) # usually 6-10 is a good amount to thread, but you may need to experiement
    pool.map(scrape_site, remaining_id_url_tuples)

concurrent_scrape(remaining_id_url_tuples)
