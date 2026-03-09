# Representing Document Concepts with Embeddings

## Overview

This project explores two methodologies for transforming unstructured Reddit text data into numerical vectors for the purpose of document clustering.
We compare a neural based approach (Doc2Vec) against a frequency based approach (Word2Vec with Bag of Words binning) across three different dimensions.
The pipeline processes raw tokens, generates embeddings across multiple dimensions (K=20, 100, 300), and performs K-Means clustering to identify 
hidden thematic structures.

---

## Requirements

To run these scripts, you will need Python 3.x and the following libraries installed. You can install the dependencies using:
```bash
pip install pandas numpy gensim scikit-learn
```

---

## File Overview 

- **cleaned_posts.csv**: The input dataset containing tokenized Reddit posts.
- **doc2vec.py**: Implements the Gensim Doc2Vec model to transform tagged Reddit posts into continuous vectors. Handles three configuration tiers (Small, Medium, Large) and applies L2-normalization for cosine distance clustering.
- **bagofwords.py**: Trains a Word2Vec model on the global vocabulary, clusters words into K-bins, and creates normalized frequency vectors for each document.
- **evaluation.py**: A comparison script that loads results from both methods and prints a comparative table of Silhouette and Davies-Bouldin scores.

---

## Execution Pipeline

Follow these steps in order to move from raw tokens to a finalized comparative report.

### Step 1: Generate Doc2Vec Embeddings

Execute the script which trains the model to understand document intent and context to generate embeddings and clusters for the 20, 100, and 300-dimension configurations.

```bash
python3 doc2vec.py
```
**Output:** `doc2vec_results.csv` and `doc2vec_evaluation_results.csv`

### Step 2: Run Word2Vec Bag-of-Words

Execute the script which treats documents as a distribution of semantic word clusters to perform word binning and generate document frequency vectors.

```bash
python3 bagofwords.py
```
**Output:** `word2vec_bow_results.csv` and `bow_evaluation_results.csv`

### Step 3: Comparative Analysis

Run the evaluation script to see the final quantitative comparison between the two methodologies.

```bash
python3 evaluation.py
```

---

### Summary of Results & Rationale

- The Word2Vec based Bag of Words (BoW) approach significantly outperformed Doc2Vec at the 20-dimension level. It achieved the highest Silhouette
  Score (0.281) and the lowest Davies-Bouldin Score (2.028), indicating highly distinct and compact clusters.
- Both methods saw a decline in cluster quality as dimensionality increased. For BoW, moving from 20 to 300 dimensions caused the Silhouette score
  to drop from 0.28 to 0.04, likely due to increased vector sparsity.
- Doc2Vec struggled across all configurations, with scores peaking at only 0.12 in the 20-dimension setting. This suggests that the model may
  require a larger or more diverse dataset to effectively learn nuanced document level relationships.



