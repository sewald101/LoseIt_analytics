
# Create SQL table for receiving topic records


# Grab samples for NLP
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
  

CREATE TABLE topics (
    topic varchar(150),
    topic_id int,
    landing_url varchar(150),
    library varchar(50),
    cat_url varchar(150)
    );

# Quick look at a record
SELECT topic,
  topic_id,
  post_idx,
  date_posted,
  name,
  author_id,
  LENGTH(post_body) AS post_len,
  library,
  page_url
FROM posts_test
ORDER BY post_idx;




SELECT
  DISTINCT(post_id),
  topic_id,
  post_idx,
  topic,
  library,
  name,
  author_id,
  LENGTH(post_body) AS post_len,
  SUBSTRING(page_url,30,150)
FROM posts
WHERE topic LIKE ('%Wagon%')
ORDER BY post_len DESC
LIMIT 50;


SELECT
  post_id,
  topic_id,
  post_idx,
  SUBSTRING(topic,0,25),
  library,
  name,
  author_id,
  LENGTH(post_body) AS post_len,
  SUBSTRING(page_url,30,150)
FROM posts
WHERE library = "FAQ"
ORDER BY topic_id, post_idx
LIMIT 50;


SELECT post_id
  , topic
  , library
  , name
  , LENGTH(post_body) AS post_len
  , cited
  , page_url
FROM posts
WHERE topic_id=36492
ORDER BY post_idx;

SELECT post_id
  , substring(topic,0,25) as topic
  , library
  , name
  , substring(post_body,0,25) as body
FROM posts
WHERE library = 'FAQ'
LIMIT 10;


# Number of posts per library
SELECT library
  , COUNT(DISTINCT(post_id)) as num_posts
FROM posts
GROUP BY library
ORDER BY num_posts DESC;




#Create posts table
CREATE TABLE posts (
    topic TEXT,
    topic_id INT,
    page_idx INT,
    post_idx INT,
    post_id VARCHAR(12),
    date_posted VARCHAR(12),
    name TEXT,
    author_id INT,
    joined VARCHAR(12),
    ttl_posts INT,
    post_body TEXT,
    cited TEXT,
    quotation TEXT,
    library VARCHAR(50),
    page_url VARCHAR(150)
    );



# Buggy
INSERT INTO posts_test (
  topic,
  topic_id,
  page_idx,
  post_idx,
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
VALUES (
  post['topic'],
  post['topic_id'],
  post['page_idx'],
  post['post_idx'],
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
);
