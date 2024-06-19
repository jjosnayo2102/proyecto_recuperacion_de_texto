import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import nltk
from collections import defaultdict
nltk.download('stopwords')

idf = pd.read_csv('idf.csv')
vocab = pd.read_csv('vocabulario.csv')
vectors = pd.read_csv('vectores.csv')
spotify = pd.read_csv("spotify_songs.csv")
letras = spotify["lyrics"]

def stem_tokens(tokens, language="english"):
    stemmer = SnowballStemmer(language)
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

def filtrar_stopwords(term, language="english"):
    stop_words = stopwords.words(language)
    stop_words += [',', '.', '!', '?', '¿', '¡', ':', ';']
    stop_words = set(stop_words)
    filtered_tokens = [word for word in term if word not in stop_words]
    return filtered_tokens

def preprocesar(query):
    tokens = word_tokenize(query)
    terms = stem_tokens(tokens)
    res = filtrar_stopwords(terms)
    return res

def computar_tf_idf(query, idf):
    tf_idf = {}
    tf = defaultdict(int)
    for term in query:
        tf[term] += 1
    for term in query:
        if idf[term]:
            tf_idf[term] = (tf[term]/len(query))*idf[term]
    return tf_idf

def vectorizar(doc_tf_idf, vocab):
    vector = [0.0] * len(vocab)
    for term, weight in doc_tf_idf.items():
        if term in vocab:
            vector[vocab.index(term)] = weight
    return vector

def similitud_coseno(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def retrieve_text(query, k, option=1):
    results = []
    if option == 1:
        query_terms = preprocesar(query)
        query_tf_idf = computar_tf_idf(query_terms, idf)
        query_vector = vectorizar(query_tf_idf, vocab)
        similitudes = []
        for id, doc_vector in enumerate(vectors):
            similitudes.append((similitud_coseno(query_vector, doc_vector),id))
        res = sorted(similitudes, reverse=True)
        resk = res[0:k]
        for fila in resk:
            d = {}
            d['id'] = fila[1]
            d['score'] = fila[0]
            d['text'] = letras.iloc[fila[0]]
            results.append(d)
    return results