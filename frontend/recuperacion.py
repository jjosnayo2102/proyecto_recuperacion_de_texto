from csvs import vectorizar, computar_tf_idf, similitud_coseno, preprocesar
import pandas as pd

idf = pd.read_csv('idf.csv')
vocab = pd.read_csv('vocabulario.csv')
vectors = pd.read_csv('vectores.csv')
spotify = pd.read_csv("spotify_songs.csv")
letras = spotify["lyrics"]

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