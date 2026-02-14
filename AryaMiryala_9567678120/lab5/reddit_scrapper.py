import os
import time
import hashlib
import requests
import re
import pytesseract
from PIL import Image
from datetime import datetime, timezone
from tqdm import tqdm
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from collections import Counter

MYSQL_URL = "mysql+pymysql://root:1234@127.0.0.1:3306/lab5_db"

# Salt for anonymization
SALT = "dsci560_salt_2026"

def mask_username(u):
    if u is None:
        return "deleted"
    h = hashlib.sha256((SALT + u).encode("utf-8")).hexdigest()
    return f"user_{h[:12]}"

def clean_text(text):
    if not text: return ""
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_keywords(text, top_n=5):
    words = text.lower().split()
    stopwords = {"the","and","is","in","to","of","for","on","an","with","this","that","it","be"}
    words = [w for w in words if w not in stopwords and len(w) > 3]
    freq = Counter(words)
    return ",".join([w for w, _ in freq.most_common(top_n)])

def download_image(url, dest_folder="/tmp/reddit_images"):
    os.makedirs(dest_folder, exist_ok=True)
    fname = os.path.join(dest_folder, url.split("/")[-1].split("?")[0])
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(fname, "wb") as f:
                f.write(r.content)
            return fname
    except Exception:
        return None
    return None

def save_post_to_db(conn, post):
    sql = text("""
    INSERT INTO posts 
    (id, subreddit, author_masked, created_utc, title, selftext, image_text, keywords, cleaned_text, url)
    VALUES 
    (:id, :subreddit, :author_masked, :created_utc, :title, :selftext, :image_text, :keywords, :cleaned_text, :url)
    ON DUPLICATE KEY UPDATE fetched_at = CURRENT_TIMESTAMP
    """)
    try:
        conn.execute(sql, post)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"DB Error: {e}")

def scrape_subreddit(subreddit_name, num_posts, engine):
    conn = engine.connect()
    fetched = 0
    after = None
    headers = {"User-Agent": "DSCI560_lab5 academic project"}
    pbar = tqdm(total=num_posts, desc=f"Fetching r/{subreddit_name}")

    while fetched < num_posts:
        url = f"https://www.reddit.com/r/{subreddit_name}/new.json?limit=100"
        if after: url += f"&after={after}"
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: break

        data = response.json()
        posts = data["data"]["children"]
        if not posts: break

        for item in posts:
            if fetched >= num_posts: break
            submission = item["data"]
            if submission.get("stickied") or submission.get("promoted"): continue

            raw_title = submission.get("title", "")
            raw_body = submission.get("selftext", "")
            combined_text = raw_title + " " + raw_body
            cleaned = clean_text(combined_text)
            
            post = {
                "id": submission["id"],
                "subreddit": subreddit_name,
                "author_masked": mask_username(submission.get("author")),
                "created_utc": datetime.fromtimestamp(submission["created_utc"], timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "title": raw_title,
                "selftext": raw_body,
                "cleaned_text": cleaned,
                "keywords": extract_keywords(cleaned),
                "image_text": None,
                "url": submission.get("url")
            }

            #  Process images if URL looks like an image file
            image_url = submission.get("url", "")
            if any(ext in image_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                img_path = download_image(image_url)
                if img_path:
                    try:
                        # Perform OCR and store in dictionary
                        post["image_text"] = pytesseract.image_to_string(Image.open(img_path))
                    except Exception as e:
                        print(f"OCR Error for {image_url}: {e}")
                    finally:
                        # Delete image 
                        if os.path.exists(img_path):
                            os.remove(img_path)

            save_post_to_db(conn, post)
            fetched += 1
            pbar.update(1)

        after = data["data"].get("after")
        time.sleep(1) # Respect Reddit API
        if not after: break

    conn.close()
    pbar.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int, help="Number of posts to fetch")
    args = parser.parse_args()

    engine = create_engine(MYSQL_URL)
    scrape_subreddit("investing", args.n, engine)
