import nltk
import math
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd
import shelve

# nltk.download('punkt')
import re
stemmer = SnowballStemmer('english')
with open("stoplist.txt", encoding="latin1") as file:
    stoplist = [line.rstrip().lower() for line in file]

def preprocesamiento(texto):
  if not texto or pd.isnull(texto):
        return []
  texto = texto.lower()
  texto = re.sub(r"[^\w\s]", "", texto)
  tokens = nltk.word_tokenize(texto, language='english') # la mayoría de canciones está en inglés
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
        #spimi
        n = 0
        N = 0
        for database in pd.read_csv(database_name,chunksize=100): # leer por partes
            doc_count = database.shape[0]
            doc_terms = defaultdict(Counter)
            coleccion = database[position_text]
            for i, letra in enumerate(coleccion):
                doc_id = i+1
                words = preprocesamiento(letra)
                doc_terms[doc_id] = Counter(words)
                for word in set(words):
                    self.index[word].append((doc_id, math.log10(doc_terms[doc_id][word] + 1)))
            N += doc_count
            for word in self.index:
                df = len(self.index[word])
                self.idf[word] += df # primero se guardan df's
            # ir metiendo los terminos de los indices locales en sus postings lists
            with shelve.open(self.index_file + "_postings_list") as pl:
                for term in self.index:
                    if term not in pl:
                        pl[term] = []
                    pl[term].extend(self.index[term])
            self.index = defaultdict(list)
            n += 1
        # crear el idf
        for key in self.idf:
            self.idf[key] = math.log10(N / self.idf[key])
        # crear el length de cada documento usando memoria secundaria
        with shelve.open(self.index_file + "_postings_list") as indice:
            for term in self.idf:
                postingslist = indice[term]
                for p in postingslist:
                    self.length[p[0]] += self.idf[term]*p[1]
        with open(self.index_file + ".dat", "wb") as file:
            pickle.dump((self.idf,self.length), file)


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
                with shelve.open(self.index_file + "_postings_list") as indice:
                    postingslist = indice[term]
                    for doc_id, tf_t_d in postingslist:
                        w_t_d = tf_t_d * self.idf[term]
                        scores[doc_id] += w_t_d * w_t_q 
        query_norm = math.sqrt(query_norm)
        for doc_id in scores:
            scores[doc_id] /= (self.length[doc_id]*query_norm)
        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return top_k


# index = InvertIndex("indice")
# index.building('spotify_songs.csv', 'lyrics')