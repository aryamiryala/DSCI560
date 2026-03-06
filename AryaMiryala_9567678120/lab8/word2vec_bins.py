import pandas as pd
import ast
import numpy as np
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

# Load data 
df = pd.read_csv('cleaned_posts.csv')
df['tokens'] = df['tokens'].apply(ast.literal_eval)
all_posts_tokens = df['tokens'].tolist()

dimensions = [20, 100, 300]

# Train Word2Vec to vectorize all words in the dataset 
print("Training Word2Vec model: ")
w2v_model = Word2Vec(sentences=all_posts_tokens, vector_size=100, window=5, min_count=1, workers=4)
words = list(w2v_model.wv.index_to_key)
word_vectors = w2v_model.wv.vectors

for K in dimensions:
    print(f"Processing with K={K} bins")
    
    # Cluster words into K-bins
    word_kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
    word_clusters = word_kmeans.fit_predict(word_vectors)
    word_to_bin = dict(zip(words, word_clusters))
    
    # Create document vectors each with K-entries 
    doc_vectors = []
    for tokens in all_posts_tokens:
        bin_vector = np.zeros(K)
        word_count = 0
        
        for word in tokens:
            if word in word_to_bin:
                bin_idx = word_to_bin[word]
                bin_vector[bin_idx] += 1
                word_count += 1
        
        # Normalize by dividing by total number of words in the post 
        if word_count > 0:
            bin_vector = bin_vector / word_count
            
        doc_vectors.append(bin_vector)
    
    # Cluster the documents using cosine distance 
    doc_vectors_norm = normalize(doc_vectors)
    doc_kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df[f"w2v_bin_cluster_{K}"] = doc_kmeans.fit_predict(doc_vectors_norm)

# Save final results 
df.to_csv('word2vec_binning_results.csv', index=False)
print("Results saved to word2vec_binning_results.csv")