import os
import time
import hashlib
from datetime import datetime
from tqdm import tqdm
#import praw
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import re
from collections import Counter


MYSQL_URL = "mysql+pymysql://root:@localhost:3306/redditdb"


#REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
#REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
#REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "DSCI560/0.1")

# Mask usernames with salted sha256
SALT = os.getenv("USERNAME_SALT", "change_this_salt")

#anonymize username
def mask_username(u):
    if u is None:
        return "deleted"
    h = hashlib.sha256((SALT + u).encode("utf-8")).hexdigest()
    return f"user_{h[:12]}"


#api object. temp workaround
#def init_reddit():
#    #using praw api
#    return praw.Reddit(
#        client_id=REDDIT_CLIENT_ID,
#        client_secret=REDDIT_CLIENT_SECRET,
#        user_agent=REDDIT_USER_AGENT,
#        check_for_async=False
#    )


def clean_text(text):
    if not text:
        return ""

    # Remove markdown links [text](url)
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)

    # Remove any http/https links
    text = re.sub(r"https?://\S+", "", text)

    # Remove markdown formatting
    text = re.sub(r"[*_`]", "", text)

    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# keyword extraction for preprocessing stage
def extract_keywords(text, top_n=5):
    words = text.lower().split()

    stopwords = {
        "the","and","is","in","to","of","for","on","a","an",
        "with","this","that","it","be","are","as","at","by",
        "or","from","was","were","will","can","would"
    }

    words = [w for w in words if w not in stopwords and len(w) > 3]

    freq = Counter(words)
    return ",".join([w for w, _ in freq.most_common(top_n)])


def save_post_to_db(conn, post):
    # post is dict with expected keys
    #dont duplicate
    sql = text("""
    INSERT INTO posts 
    (id, subreddit, author_masked, created_utc, title, selftext, image_text, keywords, cleaned_text, embedding, cluster, url)
    VALUES 
    (:id, :subreddit, :author_masked, :created_utc, :title, :selftext, :image_text, :keywords, :cleaned_text, :embedding, :cluster, :url)
    ON DUPLICATE KEY UPDATE fetched_at = CURRENT_TIMESTAMP
    """)
    try:
        conn.execute(sql, post)
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


def scrape_subreddit(subreddit_name, num_posts, engine, chunk_size=500, sleep_between=2):
    conn = engine.connect()
    fetched = 0
    after = None

    headers = {
        "User-Agent": "DSCI560_lab5 academic project"
    }

    pbar = tqdm(total=num_posts, desc=f"Fetching r/{subreddit_name}")

    while fetched < num_posts:
        url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit=100"
        if after:
            url += f"&after={after}"

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print("Request failed:", response.status_code)
            break

        data = response.json()
        posts = data["data"]["children"]

        if not posts:
            break

        for item in posts:
            if fetched >= num_posts:
                break

            submission = item["data"]

            # skip stickied / promoted posts
            if submission.get("stickied") or submission.get("promoted"):
                continue

            raw_title = submission.get("title")
            raw_body = submission.get("selftext")

            combined_text = (raw_title or "") + " " + (raw_body or "")
            cleaned = clean_text(combined_text)
            keywords = extract_keywords(cleaned)

            post = {
                "id": submission["id"],
                "subreddit": subreddit_name,
                "author_masked": mask_username(submission.get("author")),
                "created_utc": datetime.fromtimestamp(
                    submission["created_utc"], timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),

                "title": raw_title,
                "selftext": raw_body,
                "cleaned_text": cleaned,
                "keywords": keywords,

                "image_text": None,
                "embedding": None,
                "cluster": None,
                "url": submission.get("url")
            }

            save_post_to_db(conn, post)
            fetched += 1
            pbar.update(1)

        after = data["data"].get("after")

        # Rate limit protection
        time.sleep(1)

        if not after:
            break

    conn.close()
    pbar.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int, help="Number of posts to fetch")
    args = parser.parse_args()

    engine = create_engine(MYSQL_URL, pool_pre_ping=True)

    scrape_subreddit("hardwareswap", args.n, engine)
