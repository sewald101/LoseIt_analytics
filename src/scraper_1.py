"""Scraping utilities for Lose It!
"""

from pymongo import MongoClient
import time
import selenium.webdriver
import pymongo
import json
import random
import os


def scraper(browser, urls, collection):
    """scrapes Lose It! urls to documents in mongo db collection."""
    mc = MongoClient()
    db = mc['lose_it']
    coll = db[collection]
    cursor = coll.find({}, {'url': True}, no_cursor_timeout=True)
    urls_in_collection = set([document['url'] for document in cursor])
    with open(urls, 'r') as f:
        for url in f:
            if url in urls_in_collection:
                print "{} already in collection".format(url)
                continue
            if "errorPageContainer" in [
                elem.get_attribute("id") for elem in browser.find_elements_by_css_selector("body > div") ]:
                raise Exception( "Page returned error" )
            else:
                browser.get(url)
                coll.insert_one({
                    "url": url.strip(),
                    "html": browser.page_source
                })
                print 'document added: {}'.format(url)
                time.sleep(random.random())
                    # random.choice([1, 2]) + random.random()
                    # )
    cursor.close()
    print('Web scrape complete.')


def sign_in(browser, username, password):
    """Use browser to sign in to loseit.com"""
    browser.get('https://www.loseit.com')
    time.sleep(1 + random.random())
    sign_in_button = browser.find_element_by_class_name("button")
    sign_in_button.click()
    time.sleep(2 + random.random())

    sel = 'div.GI3QXTCCNP:nth-child(3) > input:nth-child(2)'
    username_box = browser.find_element_by_css_selector(sel)
    username_box.click()
    username_box.send_keys(username)
    time.sleep(2 + random.random())

    sel = 'div.GI3QXTCCNP:nth-child(4) > input:nth-child(2)'
    password_box = browser.find_element_by_css_selector(sel)
    password_box.click()
    password_box.send_keys(password)
    time.sleep(1 + random.random())

    sel = 'button.GI3QXTCCAM'
    signin_button=browser.find_element_by_css_selector(sel)
    signin_button.click()
    return browser

def get_forum_links(browser):
    """Get the forum links with a logged-in browser."""
    browser.get('https://forums.loseit.com/forums/list.page')
    sel = 'a.forumlink'
    forum_links = browser.find_elements_by_css_selector(sel)
    return [(a.text, a.get_attribute('href')) for a in forum_links]


if __name__=='__main__':
    """Go to the site and get the forum links."""
    browser = selenium.webdriver.Firefox()
    username=os.environ['LOSEIT_USER']
    password=os.environ['LOSEIT_PWD']
    browser.get('https://forums.loseit.com/')
    sign_in(browser, username, password)
