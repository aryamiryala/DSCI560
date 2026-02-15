import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from scipy.spatial import distance

def run_analysis():
    engine = create_engine("mysql+pymysql://root:1234@127.0.0.1:3306/lab5_db")
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

    # Find messages closest to centroids
    for i, center in enumerate(kmeans.cluster_centers_):
        cluster_indices = np.where(df['cluster'] == i)[0]
        
    # Update database
    with engine.connect() as conn:
        for idx, row in df.iterrows():
            conn.execute(text("UPDATE posts SET cluster=:c WHERE id=:id"), 
                         {"c": int(row['cluster']), "id": row['id']})
            conn.commit()
    print("Clusters updated in DB.")

if __name__ == "__main__":
    run_analysis()
