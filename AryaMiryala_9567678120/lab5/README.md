# DSCI-560 Lab 5 – Data Collection (Reddit Scraper)

## Overview

Due to delays in Reddit API key approval, we utilized Reddit’s publicly accessible JSON endpoints (e.g., https://www.reddit.com/r/hardwareswap/new.json) to retrieve structured subreddit data.

This method provides direct access to Reddit’s REST data in JSON format without requiring OAuth authentication. Compared to HTML scraping with BeautifulSoup, the JSON endpoint provides cleaner, structured data and simplifies pagination using the `after` parameter. Therefore, it served as a reliable alternative to PRAW for data collection.

## What reddict_scrapper.py Script Does

- Fetches subreddit posts using Reddit JSON endpoint
- Handles pagination using the `after` parameter
- Supports large requests (5000+ posts)
- Implements rate limiting to avoid request failures
- Masks usernames for privacy compliance
- Converts timestamps to UTC format
- Performs preprocessing:
  - Removes markdown links
  - Removes URLs
  - Removes special characters
  - Normalizes whitespace
- Extracts keywords
- Stores both raw and cleaned text in MySQL
- Prevents duplicate entries using primary key constraint

---


## Requirements 

Install required Python packages:

```bash
pip install -r requirements.txt 
```

## Database Setup

Make sure MySQL is running.

Create database and table schema:
mysql -u root < schema.sql

Confirm database:
USE redditdb;
SHOW TABLES;

Run the script with the number of posts to fetch:
python reddit_scrapper.py 100

The script will:

- Automatically paginate
- Sleep between requests (rate limiting)
- Stop once desired number of posts is reached

## Database Structure

### Table: `posts`

| Column          | Description                          |
|-----------------|--------------------------------------|
| id              | Reddit post ID (Primary Key)         |
| subreddit       | Subreddit name                       |
| author_masked   | Hashed username                      |
| created_utc     | Normalized UTC timestamp             | 
| title           | Raw post title                       |
| selftext        | Raw post body                        |
| cleaned_text    | Preprocessed text for NLP            |
| keywords        | Extracted keywords                   |
| image_text      | Placeholder for OCR                  |
| embedding       | Placeholder for embeddings           |
| cluster         | Placeholder for clustering           |
| url             | Reddit permalink                     |
| fetched_at      | Timestamp of insertion               |


Notes for Team

- Raw text is stored in title and selftext
- Preprocessed text is stored in cleaned_text
- Extracted keywords are stored in keywords
- Embeddings and clustering will populate embedding and cluster
- Preprocessing and clustering modules should build directly on this database.