import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import nltk
from collections import defaultdict
nltk.download('stopwords')

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

spotify = pd.read_csv("spotify_songs.csv")

datos = spotify[["track_name","track_artist","lyrics", "language"]].to_numpy()
datos = list(datos)
documentos = []
for cancion in datos:
    texto = str(cancion[0]) + " " + str(cancion[1]) + " " + str(cancion[2])
    texto = texto.lower()
    token = word_tokenize(texto)
    if cancion[3] == "es":
        term = stem_tokens(token, "spanish")
        term_filt = filtrar_stopwords(term, "spanish")
    elif cancion[3] == 'it':
        term = stem_tokens(token, "italian")
        term_filt = filtrar_stopwords(term, "italian")
    elif cancion[3] == 'pt':
        term = stem_tokens(token, "portuguese")
        term_filt = filtrar_stopwords(term, "portuguese")
    elif cancion[3] == 'dt':
        term = stem_tokens(token, "deutch")
        term_filt = filtrar_stopwords(term, "deutch")
    else:
        term = stem_tokens(token, "english")
        term_filt = filtrar_stopwords(term, "english")
    documentos.append(term_filt)

index = defaultdict(list)
for doc_id, doc in enumerate(documentos):
    for term in doc:
        index[term].append(doc_id)
 
       
def computar_idf_tf_y_idf(documents):
    N = len(documents)
    tf = defaultdict(lambda: defaultdict(int))
    df = defaultdict(int)
    for doc_id, doc in enumerate(documents):
        for term in doc:
            tf[doc_id][term] += 1
        for term in set(doc):
            df[term] += 1
    idf = {}
    for term in df:
        idf[term] = np.log10(N / df[term])
    tf_idf = defaultdict(lambda: defaultdict(float))
    for doc_id, doc in enumerate(documents):
        doc_len = len(doc)
        for term, count in tf[doc_id].items():
            tf_idf[doc_id][term] = (count / doc_len) * idf[term]
    return tf_idf, idf

tf_idf, idf = computar_idf_tf_y_idf(documentos)

def vectorizar(doc_tf_idf, vocab):
    vector = [0.0] * len(vocab)
    for term, weight in doc_tf_idf.items():
        if term in vocab:
            vector[vocab.index(term)] = weight
    return vector

vocab = list(index.keys())
vectors = [vectorizar(tf_idf[doc_id], vocab) for doc_id in range(len(documentos))] 

def computar_tf_idf(query, idf):
    tf_idf = {}
    tf = defaultdict(int)
    for term in query:
        tf[term] += 1
    for term in query:
        if idf[term]:
            tf_idf[term] = (tf[term]/len(query))*idf[term]
    return tf_idf

def similitud_coseno(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

vocabulario = pd.DataFrame(vocab)
idfs = pd.DataFrame(idf)
documentos_vectoriales = pd.DataFrame(vectors)
vocabulario.to_csv("vocabulario.csv", index=False)
idfs.to_csv("idf.csv", index=False)
documentos_vectoriales.to_csv("vectores.csv", index=False)