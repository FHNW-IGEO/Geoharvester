import pandas as pd

df = pd.read_csv("output.csv", low_memory=False)
df.to_pickle("test.pkl")