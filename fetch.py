import nltk
import math
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd
import re

# nltk.download('punkt')
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
        database = pd.read_csv(database_name)
        N = database.shape[0]
        coleccion = database[position_text]
        for doc_id, doc in enumerate(coleccion):
            id = doc_id + 1
            terms = preprocesamiento(doc)
            doc_frec = Counter(terms)
            for term, frec in doc_frec.items():
                self.index[term].append((id, math.log10(1 + frec)))
                self.idf[term] += 1
        for t in self.idf:
            self.idf[t] = math.log10(N/self.idf[t])
        for term, pl in self.index.items():
            for doc_id,tf in pl:
                self.length[doc_id] += (self.idf[term]*tf)**2
        for d in self.length:
            self.length[d] = math.sqrt(self.length[d])
        with open(self.index_file, "wb") as f:
            pickle.dump((self.index,self.idf,self.length),f)

    def load_index(self):
        with open(self.index_file, 'rb') as f:
            self.index, self.idf, self.length = pickle.load(f)

    def retrieval(self, query, k):
        query_terms = Counter(preprocesamiento(query))
        scores = defaultdict(float)
        query_norm = 0
        for term, tf in query_terms.items():
            if term in self.idf:
                w_t_q = math.log10(tf + 1) * self.idf[term]
                query_norm += w_t_q ** 2
                for doc_id, tf_t_d in self.index[term]:
                        w_t_d = tf_t_d * self.idf[term]
                        scores[doc_id] += w_t_d * w_t_q
        query_norm = math.sqrt(query_norm)
        for doc_id in scores:
            scores[doc_id] /= (self.length[doc_id] * query_norm)
        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return top_k


# index = InvertIndex("indice_prueba.dat")
# index.building('spotify_songs.csv', 'lyrics')
