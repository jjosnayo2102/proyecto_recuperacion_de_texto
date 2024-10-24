import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd
# nltk.download('punkt')

import re
stemmer = SnowballStemmer('spanish')
with open("stoplist.txt", encoding="latin1") as file:
    stoplist = [line.rstrip().lower() for line in file]

def preprocesamiento(texto):
  if not texto or pd.isnull(texto):
        return []
  # convertir a minúsculas y eliminar signos
  texto = texto.lower()
  texto = re.sub(r"[^\w\s]", "", texto)
  # tokenizar
  tokens = nltk.word_tokenize(texto, language='spanish')
  # filtrar stopwords
  words = [word for word in tokens if word not in stoplist]
  # reducir palabras
  words = [stemmer.stem(word) for word in words]
  return words

class InvertIndex:
    def __init__(self, index_file):
        self.index_file = index_file
        self.index = {}
        self.idf = {}
        self.length = {}

    def preprocesamiento(self, texto):
        # convertir a minúsculas y eliminar signos
        texto = texto.lower()
        texto = re.sub(r"[^\w\s]", "", texto)
        # tokenizar
        tokens = nltk.word_tokenize(texto, language='spanish')
        # filtrar stopwords
        words = [word for word in tokens if word not in stoplist]
        # reducir palabras
        words = [stemmer.stem(word) for word in words]
        return words
    
    def building(self, database, position_text):
        textos = database.iloc[:, position_text]
        coleccion = []
        doc_frecuencias = defaultdict(int)
        doc_term_frequencies = []
        for doc_id, texto in enumerate(textos):
            procesado = preprocesamiento(texto)
            coleccion.append(procesado)
            term_freq = Counter(procesado)
            doc_term_frequencies.append(term_freq)
            for term in term_freq.keys():
                doc_frecuencias[term] += 1
        num_docs = len(coleccion)
        for doc_id, term_freq in enumerate(doc_term_frequencies):
            for term, tf in term_freq.items():
                if term not in self.index:
                    self.index[term] = []
                self.index[term].append((doc_id, tf))
        for term, df in doc_frecuencias.items():
            self.idf[term] = np.log(num_docs / df)
        for doc_id, term_freq in enumerate(doc_term_frequencies):
            suma_cuadrados = 0
            for term, tf in term_freq.items():
                tf_idf = tf * self.idf[term]
                suma_cuadrados += tf_idf ** 2
            self.length[doc_id] = float(np.sqrt(suma_cuadrados))
        with open(self.index_file, 'wb') as f:
            pickle.dump({'index': self.index, 'idf': self.idf, 'length': self.length}, f)

    def load_index(self):
        with open(self.index_file, 'rb') as f:
            data = pickle.load(f)
            self.index = data['index']
            self.idf = data['idf']
            self.length = data['length']

    def retrieval(self, query, k):
        scores = {}
        query_terms = preprocesamiento(query)
        query_tf = Counter(query_terms)
        query_weights = {}
        query_norm = 0
        for term, tf in query_tf.items():
            if term in self.idf:
                query_weights[term] = tf * self.idf[term]
                query_norm += (query_weights[term] ** 2)
        query_norm = np.sqrt(query_norm)
        for term in query_terms:
            if term in self.index:
                postings = self.index[term] 
                for doc_id, tf_doc in postings:
                    w_td = tf_doc * self.idf[term] 
                    w_tq = query_weights.get(term, 0) 
                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += w_td * w_tq
        for doc_id in scores:
            if self.length[doc_id] > 0 and query_norm > 0:
                scores[doc_id] /= (self.length[doc_id] * query_norm)
        result = sorted(scores.items(), key=lambda tup: tup[1], reverse=True)
        return result[:k]

# df = pd.read_csv('spotify_songs.csv')
# index = InvertIndex("indice_prueba.dat")
# index.building(df, 3)