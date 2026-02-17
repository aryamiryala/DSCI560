# DSCI-560 Lab 5 – Data Collection (Reddit Scraper)

## Overview

Due to delays in Reddit API key approval, we utilized Reddit’s publicly accessible JSON endpoints (e.g., https://www.reddit.com/r/investing/new.json) to retrieve structured subreddit data.

This method provides direct access to Reddit’s REST data in JSON format without requiring OAuth authentication. Compared to HTML scraping with BeautifulSoup, the JSON endpoint provides cleaner, structured data and simplifies pagination using the `after` parameter. Therefore, it served as a reliable alternative to PRAW for data collection.

## What reddit_scrapper.py Script Does

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

## What clustering.py Script Does
- Transforms raw text into mathematical representations to find patterns across posts
- Uses Doc2Vec to convert cleaned text into 20-dimension vector values
- Implements K-Means clustering algorithm to group the 100+ messages into 5 distinct clusters based on their content similarity
- Identifies the mathematical center of each cluster
- Updates the cluster and embedding columns in the posts table for every processed entry
- Generates a bar chart of clusters


---

## What automation.py Script Does
- Maintains the database in real time
- Accepts an interval parameter (in minutes) to periodically run the scraping, preprocessing, and clustering scripts
- Keeps the lab5_db updated with the latest subreddit listings without manual intervention
- Implements a keyword cluster search where a user can input a keyword (e.g., "GPU") to find the cluster that matches most closely
- Displays similar messages from the matching cluster to help the user verify content similarity 
- Monitors the pipeline and provides status messages 

---


## What export_csv.py Script Does
- Used as a helper script to view SQL in csv format

---

## Requirements 

Install required Python packages:

```bash
pip install -r requirements.txt 
```
```bash

sudo apt install tesseract-ocr

```

## Database Setup

Set your MySQL connection string using the MYSQL_URL environment variable.
Make sure MySQL is running.

Create database and table schema:
mysql -u root < schema.sql

Confirm database:
USE lab5_db;
SHOW TABLES;

## Manual
Run the script with the number of posts to fetch:

```bash
python reddit_scrapper.py 100

```

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
| image_text      | Extracted OCR text from image posts  |
| embedding       | Pickled Doc2Vec vector stored as BLOB|
| cluster         | Cluster label assigned by K-Means    |
| url             | Reddit permalink                     |
| fetched_at      | Timestamp of insertion               |

```bash
python clustering.py
```
This running this will run clustering and display visualization

## Visualization of Clustering Results

To validate clustering performance, a bar chart visualization is generated after the clustering process completes.

The chart displays:

- X-axis: Cluster IDs 
- Y-axis: Number of posts assigned to each cluster

## Automatic
```bash
python automation.py 5
```
Running automation will automatically retrieve posts, store them, generate embeddings, cluster, and update DB
