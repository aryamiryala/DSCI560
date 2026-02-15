import sys
import time
import subprocess
import pandas as pd
from sqlalchemy import create_engine

# Use the same connection as our scraper
MYSQL_URL = "mysql+pymysql://root1234@127.0.0.1:3306/lab5_db"

def run_full_pipeline(n_posts):
    print(f"\n[{time.ctime()}] Collecting data...")
    subprocess.run(["python3", "reddit_scrapper.py", str(n_posts)])
    
    print(f"[{time.ctime()}] Processing & clustering...")
    # This runs the analysis script you just verified in IMG_0661.jpg
    subprocess.run(["python3", "clustering.py"]) 
    print(f"[{time.ctime()}] Update complete \n")

def find_closest_cluster(user_input):
    engine = create_engine(MYSQL_URL)
    # Keyword search to find which cluster the user's input might belong to
    query = f"SELECT cluster, COUNT(*) as count FROM posts WHERE cleaned_text LIKE '%%{user_input}%%' GROUP BY cluster ORDER BY count DESC LIMIT 1;"
    result = pd.read_sql(query, engine)
    
    if not result.empty:
        cluster_id = result['cluster'].values[0]
        print(f"\nYour input '{user_input}' most likely belongs to Cluster {cluster_id}.")
        print(f"Displaying other similar messages from Cluster {cluster_id}:")
        
        # Display sample from that cluster
        samples = pd.read_sql(f"SELECT title FROM posts WHERE cluster = {cluster_id} LIMIT 3", engine)
        for t in samples['title']:
            print(f" - {t}")
    else:
        print(f"\nNo direct cluster match for '{user_input}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 automation.py <interval_minutes>")
        sys.exit(1)

    interval_min = int(sys.argv[1])
    n_to_fetch = 50 # Standard batch size
    
    print(f"Starting automation with interval: {interval_min} minutes.")
    
    try:
        while True:
            run_full_pipeline(n_to_fetch)
            
            print(f"System idling for {interval_min} minutes.")
            print("Enter a keyword to find its cluster (or 'exit'):")
            
            user_query = input(">> ")
            if user_query.lower() == 'exit':
                break
            elif user_query:
                find_closest_cluster(user_query)
            
            print(f"Waiting for next update cycle...")
            time.sleep(interval_min * 60)
            
    except KeyboardInterrupt:
        print("\nAutomation terminated by user.")
