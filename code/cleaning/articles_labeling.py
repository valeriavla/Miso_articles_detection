# %%
import pandas as pd
import numpy as np

articles = pd.read_csv("articles_autolabeled.csv")

articles = articles[pd.notnull(articles['hechos'])]
print(articles.isna().any())
print(articles.isnull().any())

print(articles.shape)

#randomly exploring the sentiment of some articles
import random

art_nums = [random.randint(0, 1999) for a in range(20)]

print("actual labels",articles["label"].unique())

for x in art_nums:
    print(articles["hechos"][x])
    label = input("1 for misogynistic, 0 non-misogynistic")
    articles.loc[x,'label'] = label

print("introduced labels",articles["label"].unique())

articles.to_csv("articles_labeled.csv",encoding='utf-8')


