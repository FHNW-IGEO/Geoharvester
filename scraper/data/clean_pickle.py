import pandas as pd
from datetime import datetime

df = pd.read_pickle("merged_data.pkl")

# inspect rows
# print(df[df["abstract"] == "webgis@swisstopo.ch"])
# count_faulty = len(df[df["abstract"] == "webgis@swisstopo.ch"])
# print("faulty: ", count_faulty)

# drop rows by condition
#df = df[df["abstract"] != "webgis@swisstopo.ch"] # keeps everything that is not (exclude)

# save back
#df.to_pickle("cleaned_merged_data.pkl")


# -------------------
# Manually add timestamp and reason
# df["reason"] = "existing"
# timestamp = datetime.now().strftime("%d, %m, %Y")
# df["timestamp"] = timestamp
# # save back
# df.to_pickle("cleaned_merged_data.pkl")