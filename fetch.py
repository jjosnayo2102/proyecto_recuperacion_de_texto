import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd
import re
import os

# nltk.download('punkt')
stemmer = SnowballStemmer('english')
with open("stoplist.txt", encoding="latin1") as file:
    stoplist = [line.rstrip().lower() for line in file]

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
    def __init__(self, index_file, block_size=1000):
        self.index_file = index_file
        self.block_size = block_size
        self.temp_dir = 'temp_indices'  # Directorio para archivos temporales

        # Crear el directorio temporal si no existe
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def building(self, database, position_text):
        num_docs = len(database)
        temp_file_name = os.path.join(self.temp_dir, 'temp_indices.dat')

        # Crear o limpiar el archivo temporal
        with open(temp_file_name, 'wb') as f:
            pass

        # Leer el archivo en bloques
        for start in range(0, num_docs, self.block_size):
            end = min(start + self.block_size, num_docs)
            textos = database.iloc[start:end, position_text]
            doc_frecuencias = defaultdict(int)
            local_index = defaultdict(list)

            for doc_id, texto in enumerate(textos):
                procesado = preprocesamiento(texto)
                term_freq = Counter(procesado)
                for term, tf in term_freq.items():
                    doc_frecuencias[term] += 1
                    local_index[term].append((start + doc_id, tf))
            
            # Guardar el índice local en el archivo temporal
            with open(temp_file_name, 'ab') as f:
                pickle.dump(local_index, f)

        # Fusionar índices temporales
        self.index = self.merge_temp_indices(temp_file_name, num_docs)

        # Guardar el índice final
        with open(self.index_file, 'wb') as f:
            pickle.dump({'index': self.index, 'idf': self.idf, 'length': self.length}, f)

        # Eliminar el archivo temporal
        os.remove(temp_file_name)

    def merge_temp_indices(self, temp_file_name, num_docs):
        merged_index = defaultdict(list)
        doc_frecuencias = defaultdict(int)

        # Leer el archivo temporal
        with open(temp_file_name, 'rb') as f:
            while True:
                try:
                    local_index = pickle.load(f)
                    for term, postings in local_index.items():
                        merged_index[term].extend(postings)
                        for _, _ in postings:
                            doc_frecuencias[term] += 1
                except EOFError:
                    break

        # Calcular IDF
        self.idf = {term: np.log(num_docs / df) for term, df in doc_frecuencias.items()}

        # Calcular longitud de documentos
        self.length = {}
        for term, postings in merged_index.items():
            for doc_id, tf_doc in postings:
                if doc_id not in self.length:
                    self.length[doc_id] = 0
                tf_idf = tf_doc * self.idf.get(term, 0)
                self.length[doc_id] += tf_idf ** 2
        
        # Calcular la norma de los documentos
        for doc_id in self.length:
            self.length[doc_id] = float(np.sqrt(self.length[doc_id]))

        return merged_index

    def load_index(self, term=None):
        if term and os.path.exists(self.index_file):
            with open(self.index_file, 'rb') as f:
                data = pickle.load(f)
                self.index = data['index']
                self.idf = data['idf']
                self.length = data['length']
            return self.index.get(term, [])
        elif os.path.exists(self.index_file):
            with open(self.index_file, 'rb') as f:
                data = pickle.load(f)
                self.index = data['index']
                self.idf = data['idf']
                self.length = data['length']
        return None

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
            postings = self.load_index(term)  # Cargar solo el término necesario
            if postings:
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
# index = InvertIndex("indice.dat")
# index.building(df, 3)  # 'lyrics' es la cuarta columna
