import pandas as pd

column_names = [
    "age", "workclass", "fnlwgt", "education", "education-num",
    "marital-status", "occupation", "relationship", "race", "sex",
    "capital-gain", "capital-loss", "hours-per-week", "native-country",
    "income"
]

df = pd.read_csv("adult.data", header=None, names=column_names, sep=", ", engine="python")

# How big is our dataset?
print("Rows and columns:", df.shape)

# What are the column names?
print("Columns:", df.columns.tolist())

# Show me the first 5 rows
print(df.head())

# Show me just the sex column
print(df["sex"])

# Show me just the race column
print(df["race"])

print(df["income"].value_counts())

# Give me only the rows where sex is Male
males = df[df["sex"] == "Male"]

# Give me only the rows where sex is Female
females = df[df["sex"] == "Female"]

print("Total males:", len(males))
print("Total females:", len(females))