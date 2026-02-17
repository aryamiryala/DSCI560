import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from scipy.spatial import distance
import pickle
import matplotlib.pyplot as plt
import os

# Use the same connection as our scraper
MYSQL_URL = os.environ.get("MYSQL_URL")
engine = create_engine(MYSQL_URL)


#loads id and cleaned text- > create embeddings -> run kmeans and then update cluster labels
def run_analysis():
    # select id to identify each post and the cleaned_text to create the math vectors
    df = pd.read_sql("SELECT id, cleaned_text FROM posts", engine)
    
    if df.empty: return print("No data to analyze.")

    # a) Message content abstraction via doc2vec embedding
    print("Generating doc2vec embeddings..")
    docs = [TaggedDocument(doc.split(), [i]) for i, doc in enumerate(df['cleaned_text'])]
    model = Doc2Vec(docs, vector_size=20, window=2, min_count=1, workers=4)
    vectors = np.array([model.infer_vector(doc.split()) for doc in df['cleaned_text']])
    

    # b) Clustering messages with k-means clustering (k=5)
    print("Clustering messages..")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10).fit(vectors)
    df['cluster'] = kmeans.labels_
        
    # Update database
    with engine.begin() as conn:
        for idx, row in df.iterrows():
            embedding_blob = pickle.dumps(vectors[idx], protocol=pickle.HIGHEST_PROTOCOL) #converts it into binary data
            conn.execute(text("UPDATE posts SET cluster=:c, embedding=:e  WHERE id=:id"), 
                         {"c": int(row['cluster']),"e": embedding_blob, "id": row['id']})
    print("Clusters updated in DB.")

def show_cluster():

    # Get cluster counts
    df_counts = pd.read_sql(
        "SELECT cluster, COUNT(*) as count FROM posts GROUP BY cluster",
        engine
    )
    if df_counts.empty:
        print("No cluster data to visualize.")
        return

    # Bar chart to display results
    plt.figure()
    plt.bar(df_counts['cluster'].astype(str), df_counts['count'])
    plt.xlabel("Cluster")
    plt.ylabel("Number of Posts")
    plt.title("Number of Posts per Cluster")
    plt.show()

    print("\nCluster Distribution:")
    print(df_counts)
if __name__ == "__main__":
    run_analysis()
    show_cluster()