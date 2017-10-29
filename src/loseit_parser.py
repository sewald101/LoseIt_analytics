"""
Utilities for parsing Lose It Forum pages

CLASSES:
-- LoseItPostParser(pg_source, url)
-- LoseItCatalogParser(library, pg_source, url)
"""


from bs4 import BeautifulSoup

class LoseItPostParser(object):
    """ Extracts data from page sources of LoseIt forums

    PARAMETERS:
    -- pg_source: LoseIt Forum raw html page-source code (html string)
    -- url: Forum page url (string)

    ATTRIBUTES:
    -- posts_lst: list of forum posts parsed into dictionaries containing these k:v
        * 'page_url': (str)
        * 'library' : library in which the topic cataloged (str)
        * 'topic' : topic of the thread (str)
        * 'topic_id' : (int)
        * 'page_idx' : page number in thread (int)
        * 'post_idx' : post number, chronologically ordered within topic thread (int)
        * 'post_id' : primary key, topic_id-post_idx (str)
        * 'date_posted' : (str)
        * 'name' : author name (str)
        * 'profile_url' : url to author Lose It! profile_url
        * 'author_id' : (int)
        * 'joined' : date joined Lose It! (str)
        * 'ttl_posts' : total forum posts published by author (int)
        * 'post_body' : post body text (str)
        * 'cited' : author cited (str)
        * 'quotation' : block quotation from ealier post (str)

    -- library: library in which page url is cataloged
    -- last_pg_url: final page url of multi-page thread, for use in url generation

    PUBLIC METHODS:
    -- parse_page() -- Master method, populates all attributes
    -- parse_library()
    -- parse_last_pg_url()

    """

    def __init__(self, pg_source, url):
        self.pg_source = pg_source
        self.url = url
        self.soup = BeautifulSoup(pg_source, 'html.parser')
        self.library = None # field for message object
        self.last_pg_url = None # argument for url_generator
        self.topic_header_parent = None # parameter for message object
        self.posts_parent = None
        self.posts_lst = [] # list of messages

    def parse_page(self):
        """Populates LoseItParser instance with all attributes"""
        self._nav_to_header_parent()
        self._nav_to_posts_parent()
        self.parse_library()
        self.parse_last_pg_url()
        self.compile_records()

    def _nav_to_header_parent(self):
        """Navigates into page source to the parent td-tag for header data
        """
        ### soup = BeautifulSoup(self.pg_source, 'html.parser')
        # First stage: Grabs the parent td-tag / header
        self.topic_header_parent = (
            self.soup.find("table").find("table")
            .find("div")
            .find_next_sibling('div')
            .find_next_sibling('div')
            .find('table')
            .find('table')
            .find_next_sibling('table')
            .find('td')
            .find_next_sibling('td') # td containing library name
            )

    def parse_library(self):
        """Extracts library name from header."""
        self.library = (
            self.topic_header_parent.find('a')
            .find_next_sibling('a')
            ).text.strip()

    def parse_last_pg_url(self):
        """Extracts url of last page of multi-page topics"""
        if self.topic_header_parent.find_next_sibling('td').find('div', 'pagination'):
            # conditional; only for threads with subseqent pages...
            pg_anchors = (
                self.topic_header_parent.find_next_sibling('td') # td-tag containing pg urls
                .find_all('a')
                )
            link_names = [url.text.strip() for url in pg_anchors]
            link_name_num_rev_bool = [name.isdigit() for name in link_names[-1::-1]]
            self.last_pg_url = ('https://forums.loseit.com' +
                pg_anchors[link_name_num_rev_bool.index(True)]['href']
                )
        else: pass #print('Note: Thread has only one page.\n')

    def _nav_to_posts_parent(self):
        """Navigates into page source to the parent table-row for message data
        """
        self.posts_parent = (
            self.soup.find("table").find("table")
            .find("div")
            .find_next_sibling('div')
            .find_next_sibling('div')
            .find('table')
            .find('table')
            .find_next_sibling('table')
            .find_next_sibling('table')
            .find('tr')
            )

    def compile_records(self):
        """Compiles individual forum message data as dictionaries stored in a list
        """
        i = 0
        post_counter = 0
        self.posts = self.posts_parent
        topic_id, page_idx = self.parse_url()
        while True:

            if self.posts.find('td', 'borderbottom'):
                break

            elif i % 4 == 1: # hits a subject-line row
                post_counter += 1
                self._post = {}
                self._post['page_url'] = self.url
                self._post['library'] = self.library

                topic = (self.posts.find('div', 'subject')
                        .find('a')).text.strip()
                self._post['topic'] = topic.split('Re:')[-1].strip()
                self._post['topic_id'] = topic_id
                self._post['page_idx'] = page_idx
                self._post['post_idx'] = ((page_idx - 1) * 15) + post_counter
                self._post['post_id'] = str(topic_id) + "-" \
                    + str(self._post['post_idx'])

                date = self.posts.find('div', 'date').text.strip()
                self._post['date_posted'] = date

                author_data = self.parse_author()
                self._post['name'] = author_data[0]
                self._post['profile_url'] = author_data[1]
                self._post['author_id'] = author_data[2]
                self._post['joined'] = author_data[3]
                self._post['ttl_posts'] = author_data[4]

                body, cited, quotation = self.parse_body()
                self._post['post_body'] = body
                self._post['cited'] = cited
                self._post['quotation'] = quotation

                self.posts_lst.append(self._post)
                i += 1
                self.posts = self.posts.find_next_sibling('tr')

            else:
                i += 1
                self.posts = self.posts.find_next_sibling('tr')

    def parse_url(self):
        """Extracts topic index and page_idx (1 to end page) from url
        """
        url_lst = self.url.split('/')
        if len(url_lst) < 7:
            q = url_lst[-1].split('.')
            topic_id = int(q[0])
            page_idx = 1
        else:
            page_idx = 1 + int(url_lst[-2])/15
            q = url_lst[-1].split('.')
            topic_id = int(q[0])

        return topic_id, page_idx


    def parse_author(self):
        """parses post author data: id, name, # messages, joined, url to profile"""
        name = (self.posts.find_next_sibling('tr')
                .find('a')).text.strip()
        profile_url = (self.posts.find_next_sibling('tr')
                .find('a')['href'])
        author_id = int(profile_url.split('=')[1].split('&')[0])

        if (self.posts.find_next_sibling('tr') # Bandaid for anomalous doc
                 .find('span')
                 .find('div')
                 ):
            joined = (self.posts.find_next_sibling('tr')
                     .find('span')
                     .find('div')
                     ).text.split(':')[1].strip()
        else: joined = None

        if (self.posts.find_next_sibling('tr') # Bandaid for another anomalous doc
                 .find('span')
                 .find('div')):

            ttl_posts = int((self.posts.find_next_sibling('tr')
                     .find('span')
                     .find('div')
                     .find_next_sibling('div')
                     ).text.split(':')[1].strip()
                     )
        else: ttl_posts = None

        return (name,
                profile_url,
                author_id,
                joined,
                ttl_posts
                )

    def parse_body(self):
        """parses post body and, if present, cited authors and quotations"""
        cite_tag = (self.posts.find_next_sibling('tr')
                .find('cite')
                )
        if cite_tag:
            """Tests for presence of a citation"""
            quotation_body = (self.posts.find_next_sibling('tr')
                .find('td')
                .find_next_sibling('td')
                .find_next_sibling('td')
                .find('div')
            ).text.strip()
            quotation = quotation_body[(quotation_body.index(':') + 1):]
            # truncates by removing author cited name

            body_tag = (self.posts.find_next_sibling('tr')
                .find('td')
                .find_next_sibling('td')
                .find_next_sibling('td')
                .find('span')
                ).text.strip()

            post_body = body_tag.strip()

            quote_end_handle_len = 15
            """Sets length of end-fragment in quotation for parsing
            post_body from quotation"""
            if len(quotation) > quote_end_handle_len:
                A = -1 * quote_end_handle_len
                quote_end_handle = quotation[A:-1]
                B = post_body.index(quote_end_handle)
                C = B + (-1 * A) + 1
                post_body = body_tag[C:].strip()

            else:
                """In rare cases, leaves small quotation attached to body"""
                pass

            cited_target = cite_tag.text.strip().split(' ')[:-1]
            cited = (' ').join(cited_target)
            # parses cited author name as string

        else:
            cited = None
            quotation = None
            post_body = (self.posts.find_next_sibling('tr')
                    .find('span', 'postbody')).text.strip()

        return (post_body,
                cited,
                quotation
                )


class LoseItCatalogParser(object):
    """ Extracts topic data from page sources of LoseIt Catalogs

    PARAMETERS:
    -- library: library name (string)
    -- pg_source: LoseIt Forum raw html page-source code (html string)
    -- url: Forum page url (string)

    ATTRIBUTES:
    -- topic_lst: list of forum posts parsed into dictionaries containing these k:v
        * 'cat_url': catalog page url (str)
        * 'library' : library in which the topic cataloged (str)
        * 'topic' : topic name (str)
        * 'topic_id' : (int)
        * 'landing_url': topic landing page url (string)

    METHOD:
    -- parse_page() -- Parses topic data and stores in topic_lst
    """

    def __init__(self, library, pg_source, url):
        self.library = library
        self.pg_source = pg_source
        self.url = url
        self.soup = BeautifulSoup(pg_source, 'html.parser')
        self.topic_html_lst = self.soup.find_all('tr', 'bg_small_yellow')
        self.topic_lst = [] # list of topics


    def parse_page(self):
        """Compiles individual topics as dictionaries stored in self.topic_lst
        """
        for topic_html in self.topic_html_lst:
            _topic = {'cat_url': self.url, 'library': self.library}

            _topic_anchor = (topic_html.find('span', 'topictitle')
                                    .find('a')['href']).split(';')[0]
            _trunk = 'https://forums.loseit.com'
            _topic['landing_url'] = _trunk + _topic_anchor
            _topic['topic'] = (topic_html.find('span', 'topictitle')
                                    .find('a').text.strip())
            _topic['topic_id'] = int(_topic['landing_url']
                                    .split('/')[-1]
                                    .split('.')[0]
                                    )
            self.topic_lst.append(_topic)





if __name__=='__main__':
    ## use argv here for command_line operation
    pass
