import pandas as pd
import numpy as np


doc = pd.read_csv("doc2vec_evaluation_results.csv")
bow = pd.read_csv("bow_evaluation_results.csv")

combined = pd.concat([doc, bow])
print(combined.sort_values(by=["Method", "Dimension"]))