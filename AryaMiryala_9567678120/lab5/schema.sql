CREATE DATABASE IF NOT EXISTS lab5_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lab5_db;

CREATE TABLE IF NOT EXISTS posts (
    id VARCHAR(64) PRIMARY KEY,
    subreddit VARCHAR(128),
    author_masked VARCHAR(128),
    created_utc DATETIME,
    title TEXT,
    selftext LONGTEXT,
    image_text LONGTEXT,
    keywords TEXT,
    cleaned_text LONGTEXT,
    embedding BLOB,
    cluster INT,
    url TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
