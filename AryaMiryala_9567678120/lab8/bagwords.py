from gensim.models import Word2Vec
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score, davies_bouldin_score
import ast

df = pd.read_csv('cleaned_posts.csv')

# corpus for Word2Vec
df['tokens'] = df['tokens'].apply(ast.literal_eval)
corpus = df['tokens'].tolist()


# train Word2Vec
w2v_model = Word2Vec(
    sentences=corpus,
    vector_size=100,  
    window=5,
    min_count=2,
    workers=4,
    epochs=20
)


#repeat for dimensions
word_configs = [
    {"name": "BoW_20", "K": 20},
    {"name": "BoW_100", "K": 100},
    {"name": "BoW_300", "K": 300}
]

# get word vectors
words = list(w2v_model.wv.index_to_key)
word_vectors = np.array([w2v_model.wv[word] for word in words])
results = []
for cfg in word_configs:
    print(f"--- Processing {cfg['name']} ---")
    
    #limit k to vocaulary size 
    #K = min(cfg["K"], len(words))
    K = cfg["K"]
    
    # cluster words into K bins
    kmeans_words = KMeans(n_clusters=K, random_state = 44, n_init = 10)
    word_labels = kmeans_words.fit_predict(word_vectors)
    
    # map word to its cluster
    word_cluster_map = dict(zip(words, word_labels))
    
    # create document vectors
    doc_vectors = []
    
    #loop through each token of post
    for tokens in df['tokens']:
        vec = np.zeros(K)
        total = 0
        
        for word in tokens:
            if word in word_cluster_map:
                cluster_id = word_cluster_map[word]
                vec[cluster_id] += 1
                total += 1
        
        if total > 0:
            vec = vec / total  # normalize
        
        doc_vectors.append(vec)

    doc_vectors = np.array(doc_vectors)

    normalized_doc_vectors = normalize(doc_vectors)

    num_clusters = 5
    kmeans_docs = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    doc_clusters = kmeans_docs.fit_predict(normalized_doc_vectors)

    df[f"cluster_{cfg['name']}"] = doc_clusters
    #for evaluation later
    sil_score = silhouette_score(normalized_doc_vectors, doc_clusters, metric='cosine')
    db_score = davies_bouldin_score(normalized_doc_vectors, doc_clusters)

    results.append({
        "Method": "BoW",
        "Dimension": K,
        "Silhouette": sil_score,
        "Davies_Bouldin": db_score
    })

    print(f"Silhouette Score ({cfg['name']}):", sil_score)
    print(f"Davies-Bouldin Score ({cfg['name']}):", db_score)


df.to_csv("word2vec_bow_results.csv", index=False)
results_df = pd.DataFrame(results)
results_df.to_csv("bow_evaluation_results.csv", index=False)
print("W2V Results saved.")