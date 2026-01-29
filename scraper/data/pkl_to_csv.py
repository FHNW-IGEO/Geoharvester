import pickle
import pandas as pd

with open("enhanced_merged_data.pkl", "rb") as f:
    data = pickle.load(f)

df = (
    data if isinstance(data, pd.DataFrame)
    else pd.DataFrame(data)
)

df.to_csv("pkl_to_csv_output.csv", index=False)
