import nltk
import math
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd
import shelve
import re

nltk.download('punkt')
stemmer = SnowballStemmer('english')

with open("stoplist.txt", encoding="latin1") as file:
    stoplist = {line.rstrip().lower() for line in file}  # Usar un conjunto para búsquedas más rápidas

def preprocesamiento(texto):
    if not texto or pd.isnull(texto):
        return []
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    tokens = nltk.word_tokenize(texto, language='english')
    words = [word for word in tokens if word not in stoplist]
    words = [stemmer.stem(word) for word in words]
    return words

class InvertIndex:
    def __init__(self, index_file):
        self.index_file = index_file
        self.index = defaultdict(list)
        self.idf = defaultdict(float)
        self.length = defaultdict(float)

    def building(self, database_name, position_text):
        N = 0  # Contador total de documentos

        for database in pd.read_csv(database_name, chunksize=100):
            doc_count = database.shape[0]
            N += doc_count
            coleccion = database[position_text]

            # Crear un índice temporal para el bloque actual
            block_index = defaultdict(Counter)

            for i, letra in enumerate(coleccion):
                doc_id = i + 1
                words = preprocesamiento(letra)
                term_counter = Counter(words)

                for word, count in term_counter.items():
                    block_index[word][doc_id] += count

            # Guardar los términos de este bloque en el índice
            with shelve.open(self.index_file + "_postings_list", writeback=True) as pl:
                for word, postings in block_index.items():
                    if word not in pl:
                        pl[word] = []
                    # Calcular el tf y guardar la publicación
                    pl[word].extend((doc_id, math.log10(tf + 1)) for doc_id, tf in postings.items())

        # Calcular el IDF después de construir el índice
        for word in block_index:
            self.idf[word] = len(block_index[word])

        # Guardar el IDF
        with open(self.index_file + ".dat", "wb") as file:
            pickle.dump((self.idf, self.length), file)

        # Calcular longitudes y guardar en el archivo
        with shelve.open(self.index_file + "_postings_list") as pl:
            for term in self.idf:
                postingslist = pl[term]
                for doc_id, tf in postingslist:
                    self.length[doc_id] += self.idf[term] * tf

    def load_index(self):
        with open(self.index_file + ".dat", 'rb') as f:
            self.idf, self.length = pickle.load(f)

    def retrieval(self, query, k):
        query_terms = Counter(preprocesamiento(query))
        scores = defaultdict(float)
        query_norm = 0
        for term, tf in query_terms.items():
            if term in self.idf:
                w_t_q = math.log10(tf + 1) * self.idf[term]
                query_norm += w_t_q ** 2
                with shelve.open(self.index_file + "_postings_list") as pl:
                    postingslist = pl.get(term, [])
                    for doc_id, tf_t_d in postingslist:
                        w_t_d = tf_t_d * self.idf[term]
                        scores[doc_id] += w_t_d * w_t_q

        query_norm = math.sqrt(query_norm)
        for doc_id in scores:
            scores[doc_id] /= (self.length[doc_id] * query_norm)

        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return top_k


index = InvertIndex("indice_prueba")
index.building('spotify_songs.csv', 'lyrics')
