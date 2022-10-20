from nltk.corpus import stopwords
import nltk
from wordcloud import WordCloud
from gensim.utils import simple_preprocess
import gensim.corpora as corpora
import gensim
from pprint import pprint
import re
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
import matplotlib.pyplot as plt
import dash
from src.topicModelling.preprocessing import clean
import os.path
import os

def create_topics(filepath):
    # Data reading and cleaning
    df = pd.read_excel(
        filepath)
    basename = os.path.basename(filepath).split(".")[0]
    text_df = df[["text"]]
    text_df = text_df.dropna()
    print("Cleaning Text")
    text_df["text"] = text_df["text"].apply(lambda x: clean(x))
    print("Cleaning Done")
    text_df_list = text_df.values.tolist()
    text_df_list_final = [val for sublist in text_df_list for val in sublist]

    print("Processing Topics")
    model = SentenceTransformer("roberta-base-nli-stsb-mean-tokens")

    print("Embedding Topics")
    embeddings = model.encode(text_df_list_final, show_progress_bar=True)

    print("Clustering Topics, this step may take a longer time for large datasets")

    umap_embeddings = umap.UMAP(
        n_neighbors=15, n_components=5, metric='cosine').fit_transform(embeddings)

    cluster = hdbscan.HDBSCAN(min_cluster_size=10, metric='euclidean',
                            cluster_selection_method='eom').fit(umap_embeddings)


    # Prepare data
    umap_data = umap.UMAP(n_neighbors=15, n_components=2,
                        min_dist=0.0, metric='cosine').fit_transform(embeddings)
    result = pd.DataFrame(umap_data, columns=['x', 'y'])
    result['labels'] = cluster.labels_

    docs_df = pd.DataFrame(text_df_list_final, columns=["Doc"])
    docs_df['Topic'] = cluster.labels_
    docs_df['Doc_ID'] = range(len(docs_df))
    docs_df["Topic"].unique()
    docs_df = docs_df.dropna()
    docs_per_topic = docs_df.groupby(
        ['Topic'], as_index=False).agg({'Doc': ' '.join})


    def c_tf_idf(documents, m, ngram_range=(1, 1)):
        count = CountVectorizer(ngram_range=ngram_range,
                                stop_words="english").fit(documents)
        t = count.transform(documents).toarray()
        w = t.sum(axis=1)
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        return tf_idf, count


    tf_idf, count = c_tf_idf(docs_per_topic.Doc.values, m=len(text_df_list_final))


    def extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n):
        words = count.get_feature_names_out()
        labels = list(docs_per_topic.Topic)
        tf_idf_transposed = tf_idf.T
        indices = tf_idf_transposed.argsort()[:, -n:]
        top_n_words = {label: [(words[j], tf_idf_transposed[i][j])
                            for j in indices[i]][::-1] for i, label in enumerate(labels)}
        return top_n_words


    def extract_topic_sizes(df):
        topic_sizes = (df.groupby(['Topic'])
                        .Doc
                        .count()
                        .reset_index()
                        .rename({"Topic": "Topic", "Doc": "Size"}, axis='columns')
                        .sort_values("Size", ascending=False))
        return topic_sizes


    top_n_words = extract_top_n_words_per_topic(
        tf_idf, count, docs_per_topic, 10)

    top_words_output = []
    for (key, value) in top_n_words.items():
        top_words_output.append([key, list(map(lambda x: x[0], value))])


    topic_sizes = extract_topic_sizes(docs_df)
    pie_chart_df = pd.DataFrame(data=top_words_output, columns=["Topic", "Words"])
    final_chart_df = pie_chart_df.merge(topic_sizes, left_on="Topic", right_on="Topic")


    path = "./assets/outputs/topic_modeling/"
    docs_df["original_text"] = df["text"]
    docs_df["cleaned_text"] = docs_df["Doc"]
    docs_df = docs_df[["original_text", "cleaned_text", "Topic"]]
    final_chart_df.to_csv(os.path.join(path, f"{basename}_chart.csv"), index=False)
    docs_df.to_csv(os.path.join(path, f"{basename}_documents.csv"), index=False)
    docs_per_topic.to_csv(os.path.join(path, f"{basename}_wordcloud.csv"), index=False)
    print("Done")

