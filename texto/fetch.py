import nltk
import math
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd
import re
import os

# nltk.download('punkt')
stemmer = SnowballStemmer('english')

with open("texto/stoplist.txt", encoding="latin1") as file:
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

def default_value():
    return [0, -1]

class InvertIndex:
    def __init__(self, index_file):
        self.index_file = index_file + ".pkl"
        self.postings_file = index_file + "_postingslist.pkl"
        self.indice = defaultdict(default_value)  # idf, pos de postingslist
        self.diccionario = defaultdict(list)
        self.length = defaultdict(float)
        if not os.path.exists(self.postings_file):
            with open(self.postings_file, "wb") as f:
                pass  # Crea el archivo vacío

    def building(self, database_name, position_text):
        N = 0
        for bloque in pd.read_csv(database_name, chunksize=1000):
            N += bloque.shape[0]
            coleccion = bloque[position_text]
            for doc_id, doc in enumerate(coleccion):
              id = doc_id + 1
              terms = preprocesamiento(doc)
              doc_frec = Counter(terms)
              for term, frec in doc_frec.items():
                  self.diccionario[term].append((id, math.log10(1 + frec)))
                  self.indice[term][0] += 1
            # logica para ingresar indice local en postings list
            for term, pl in self.diccionario.items():
                if self.indice[term][1] == -1:
                    # guardar el nuevo postings list del término
                    with open(self.postings_file, 'r+b') as file:
                        file.seek(0,2)
                        npos = file.tell()
                        self.indice[term][1] = npos
                        bloque = (pl,-1)
                        pickle.dump(bloque, file)
                else:
                    with open(self.postings_file, 'r+b') as file:
                        file.seek(0,2)
                        npos = file.tell()
                        nbloque = (pl,-1)
                        pickle.dump(nbloque,file)
                        file.seek(self.indice[term][1],0)
                        bloque_postingslist = pickle.load(file)
                        pos = bloque_postingslist[1]
                        # encadenar nuevo bloque al final de la lista
                        while bloque_postingslist[1] != -1:
                            pos = bloque_postingslist[1]
                            file.seek(bloque_postingslist[1],0)
                            bloque_postingslist = pickle.load(file)
                        postingslist = bloque_postingslist[0]
                        bloque = (postingslist,npos)
                        if pos == -1:
                            file.seek(self.indice[term][1],0)
                        else:
                            file.seek(pos,0)
                        pickle.dump(bloque, file)
            self.diccionario = defaultdict(list)
        for t in self.indice:
            self.indice[t][0] = math.log10(N/self.indice[t][0])
        # logica para crear length
        for term in self.indice:
                # leer el postings list de cada termino
                with open(self.postings_file, "rb") as file:
                    file.seek(self.indice[term][1],0)
                    pl = pickle.load(file)
                    while pl[1] != -1:
                        for doc_id, tf in pl[0]:
                          self.length[doc_id] += (self.indice[term][0]*tf)**2
                        file.seek(pl[1],0)
                        pl = pickle.load(file)
                    for doc_id, tf in pl[0]:
                        self.length[doc_id] += (self.indice[term][0]*tf)**2
        for d in self.length:
            self.length[d] = math.sqrt(self.length[d])
        with open(self.index_file, 'wb') as f:
            pickle.dump(self.indice, f)
            pickle.dump(self.length, f)

    def load_index(self):
        with open(self.index_file, 'rb') as f:
            self.indice = pickle.load(f)
            self.length = pickle.load(f)

    def retrieval(self, query, k):
        query_terms = Counter(preprocesamiento(query))
        scores = defaultdict(float)
        query_norm = 0
        for term, tf in query_terms.items():
            if term in self.indice:
                w_t_q = math.log10(tf + 1) * self.indice[term][0]
                query_norm += w_t_q ** 2
                # leer postings_list para cada termino
                with open(self.postings_file, "rb") as file:
                    file.seek(self.indice[term][1], 0)
                    pl = pickle.load(file)
                    while pl[1] != -1:
                        for doc_id, tf_t_d in pl[0]:
                            w_t_d = tf_t_d * self.indice[term][0]
                            scores[doc_id] += w_t_d * w_t_q
                        file.seek(pl[1],0)
                        pl = pickle.load(file)
                    for doc_id, tf_t_d in pl[0]:
                        w_t_d = tf_t_d * self.indice[term][0]
                        scores[doc_id] += w_t_d * w_t_q             
        query_norm = math.sqrt(query_norm)
        for doc_id in scores:
            scores[doc_id] /= (self.length[doc_id] * query_norm)
        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return top_k


# index = InvertIndex("indice")
# index.building('spotify_songs.csv', 'lyrics')
