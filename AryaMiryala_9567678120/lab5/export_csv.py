import pandas as pd
from sqlalchemy import create_engine

# Use your verified connection string
engine = create_engine("mysql+pymysql://root:1234@127.0.0.1:3306/lab5_db")

def export_data():
    print("Fetching 5,000 records from MySQL...")
    # Fetch everything so your CSV is complete
    df = pd.read_sql("SELECT * FROM posts", engine)
    
    # Save it, overwriting the old 100-record file
    df.to_csv("posts.csv", index=False)
    print(f"Done! posts.csv now contains {len(df)} records.")

if __name__ == "__main__":
    export_data()