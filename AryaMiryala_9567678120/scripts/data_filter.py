import os
import csv
from bs4 import BeautifulSoup

input_path = os.path.join("..", "data", "raw_data", "web_data.html")
processed_dir = os.path.join("..", "data", "processed_data")

# Read the web_data.html file into BeautifulSoup
with open(input_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

print("Filtering fields...")

# Extract Market Banner Data
market_data = []
market_items = soup.find_all(class_="MarketCard-container")

for item in market_items:
    symbol = item.find(class_="MarketCard-symbol")
    position = item.find(class_="MarketCard-stockPosition")
    change = item.find(class_="MarketCard-changePct")
    
    if symbol and position and change:
        market_data.append([
            symbol.get_text(strip=True), 
            position.get_text(strip=True), 
            change.get_text(strip=True)
        ])

# Extract Latest News Data 
news_data = []
news_items = soup.find_all(class_="LatestNews-item")

for news in news_items:
    timestamp = news.find(class_="LatestNews-timestamp")
    title_tag = news.find(class_="LatestNews-headline")
    
    if timestamp and title_tag:
        title = title_tag.get_text(strip=True)
        link = title_tag.get('href') # Extract the URL link
        news_data.append([timestamp.get_text(strip=True), title, link])

# Store Data in CSV Files
print("Storing Market data...")
market_csv_path = os.path.join(processed_dir, "market_data.csv")
with open(market_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Symbol", "Position", "ChangePct"])
    writer.writerows(market_data)

# Save News Data 
print("Storing News data...")
news_csv_path = os.path.join(processed_dir, "news_data.csv")
with open(news_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Title", "Link"])
    writer.writerows(news_data)

print("CSV created successfully in processed_data folder.")