
import os
import time
import hashlib
from datetime import datetime
#from dotenv import load_dotenv populate with reddit later
from tqdm import tqdm
import praw
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

#load_dotenv()
#connect to the env
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "DSCI560/0.1")
MYSQL_URL = os.getenv("MYSQL_URL")

# Mask usernames with salted sha256
SALT = os.getenv("USERNAME_SALT", "change_this_salt")

#anonymize username
def mask_username(u):
    if u is None:
        return "deleted"
    h = hashlib.sha256((SALT + u).encode("utf-8")).hexdigest()
    return f"user_{h[:12]}"

#api object
def init_reddit():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        check_for_async=False
    )

def save_post_to_db(conn, post):
    # post is dict with expected keys
    #dont duplicate
    sql = text("""
    INSERT INTO posts (id, subreddit, author_masked, created_utc, title, selftext, image_text, keywords, cleaned_text, embedding, cluster, url)
    VALUES (:id, :subreddit, :author_masked, :created_utc, :title, :selftext, :image_text, :keywords, :cleaned_text, :embedding, :cluster, :url)
    ON DUPLICATE KEY UPDATE fetched_at = CURRENT_TIMESTAMP
    """)
    try:
        conn.execute(sql, **post)
        conn.commit()
    except IntegrityError:
        conn.rollback()
    except Exception as e:
        print("DB save error:", e)


#saves image for OCR processing
def download_image(url, dest_folder="/tmp/reddit_images"):
    os.makedirs(dest_folder, exist_ok=True)
    fname = os.path.join(dest_folder, url.split("/")[-1].split("?")[0])
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(fname, "wb") as f:
                f.write(r.content)
            return fname
    except Exception:
        return None
    return None

def fetch_subreddit_posts(subreddit_name, num_posts, engine, chunk_size=500, sleep_between=2):
    reddit = init_reddit()
    sub = reddit.subreddit(subreddit_name)
    conn = engine.connect()
    fetched = 0
    iterator = sub.new(limit=None) 
    pbar = tqdm(total=num_posts, desc=f"Fetching r/{subreddit_name}")
    batch = []
    for submission in iterator:
        # stop if reached requested number
        if fetched >= num_posts:
            break
        post = {
            "id": submission.id,
            "subreddit": subreddit_name,
            "author_masked": mask_username(getattr(submission, "author", None) and getattr(submission.author, "name", None)),
            "created_utc": datetime.utcfromtimestamp(submission.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
            "title": submission.title,
            "selftext": submission.selftext,
            "image_text": None,
            "keywords": None,
            "cleaned_text": None,
            "embedding": None,
            "cluster": None,
            "url": submission.url
        }
        save_post_to_db(conn, post)
        fetched += 1
        pbar.update(1)
        # throttle occasionally to avoid rate limits / timeouts
        if fetched % chunk_size == 0:
            time.sleep(sleep_between)
    conn.close()
    pbar.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit", help="subreddit name (without r/)")
    parser.add_argument("n", type=int, help="number of posts to fetch")
    args = parser.parse_args()

    engine = create_engine(MYSQL_URL, pool_pre_ping=True)
    fetch_subreddit_posts(args.subreddit, args.n, engine)