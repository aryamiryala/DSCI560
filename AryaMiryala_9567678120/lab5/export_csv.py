import pandas as pd
from sqlalchemy import create_engine

import os

# sql connection
MYSQL_URL = os.environ.get("MYSQL_URL")
engine = create_engine(MYSQL_URL)

def export_data():
    print("Fetching 5,000 records from MySQL...")
    # Fetch everything so your CSV is complete
    df = pd.read_sql("SELECT * FROM posts", engine)
    
    # save
    df.to_csv("posts.csv", index=False)
    print(f"Done! posts.csv now contains {len(df)} records.")

if __name__ == "__main__":
    export_data()