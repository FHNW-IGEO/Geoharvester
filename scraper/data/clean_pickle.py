import pandas as pd
from datetime import datetime

df = pd.read_pickle("merged_data.pkl")

# inspect rows
print(df[df["abstract"] == "webgis@swisstopo.ch"])
count_faulty = len(df[df["abstract"] == "webgis@swisstopo.ch"])
print("faulty: ", count_faulty)

# drop rows by condition
# df = df[df["abstract"] != "webgis@swisstopo.ch"] # keeps everything that is not (exclude)

# save back
#df.to_pickle("merged_data.pkl")

