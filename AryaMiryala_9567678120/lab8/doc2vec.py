import pandas as pd
import ast
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score, davies_bouldin_score

# load data
df = pd.read_csv('cleaned_posts.csv')
df['tokens'] = df['tokens'].apply(ast.literal_eval)

# prepare taggeddocuments
tagged_data = [TaggedDocument(words=row['tokens'], tags=[str(i)]) for i, row in df.iterrows()]

configs = [
    {"name": "Config_Small", "vector_size": 20, "epochs": 10},
    {"name": "Config_Medium", "vector_size": 100, "epochs": 20},
    {"name": "Config_Large", "vector_size": 300, "epochs": 30}
]
results = []
for cfg in configs:
    print(f"--- Training {cfg['name']} ---")
    
    # train doc2vec
    model = Doc2Vec(vector_size=cfg['vector_size'], epochs=cfg['epochs'], min_count=2, workers=4)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)
    
    # extract vectors
    vectors = [model.dv[str(i)] for i in range(len(tagged_data))]
    
    # cluster using cosine distance
    normalized_vectors = normalize(vectors) 
    num_clusters = 5  
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(normalized_vectors)
    
    # save clusters 
    df[f"cluster_{cfg['name']}"] = clusters
    #for evaluation later
    sil_score = silhouette_score(normalized_vectors, clusters, metric='cosine')
    db_score = davies_bouldin_score(normalized_vectors, clusters)

    results.append({
        "Method": "Doc2Vec",
        "Dimension": cfg["vector_size"],
        "Silhouette": sil_score,
        "Davies_Bouldin": db_score
    })

    print(f"Silhouette Score ({cfg['name']}):", sil_score)
    print(f"Davies-Bouldin Score ({cfg['name']}):", db_score)

# save final results
df.to_csv('doc2vec_results.csv', index=False)
results_df = pd.DataFrame(results)

results_df.to_csv("doc2vec_evaluation_results.csv", index=False)
print("Task 1 complete! Results saved to lab8_results.csv")