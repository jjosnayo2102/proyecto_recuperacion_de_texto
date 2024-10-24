import nltk
import math
from nltk.stem.snowball import SnowballStemmer
import pickle
from collections import defaultdict, Counter
import pandas as pd

# nltk.download('punkt')
import re
stemmer = SnowballStemmer('english')
with open("stoplist.txt", encoding="latin1") as file:
    stoplist = [line.rstrip().lower() for line in file]

def preprocesamiento(texto):
  if not texto or pd.isnull(texto):
        return []
  # convertir a minúsculas y eliminar signos
  texto = texto.lower()
  texto = re.sub(r"[^\w\s]", "", texto)
  # tokenizar
  tokens = nltk.word_tokenize(texto, language='english')
  # filtrar stopwords
  words = [word for word in tokens if word not in stoplist]
  # reducir palabras
  words = [stemmer.stem(word) for word in words]
  return words

class InvertIndex:
    def __init__(self, index_file):
        self.index_file = index_file
        self.index = defaultdict(list)
        self.idf = {}
        self.length = {}

    def building(self, database, position_text):
        doc_count = database.shape[0]
        doc_terms = defaultdict(Counter)
        for i, doc in enumerate(database.itertuples(index=False), 1):
            doc_id = i
            words = preprocesamiento(getattr(doc, position_text))
            doc_terms[doc_id] = Counter(words)
            for word in set(words):
                self.index[word].append((doc_id, math.log10(doc_terms[doc_id][word] + 1)))
        for word in self.index:
            df = len(self.index[word])
            self.idf[word] = math.log10(doc_count / df)
        for doc_id, terms in doc_terms.items():
            norm = 0
            for word, tf in terms.items():
                weight = tf * self.idf[word]
                norm += weight ** 2
            self.length[doc_id] = math.sqrt(norm)
        with open(self.index_file, 'wb') as f:
            pickle.dump((self.index, self.idf, self.length), f)

    def load_index(self):
        with open(self.index_file, 'rb') as f:
            self.index, self.idf, self.length = pickle.load(f)

    def retrieval(self, query, k):
        query_terms = preprocesamiento(query)
        query_weights = defaultdict(float)
        norm_query = 0
        for term in query_terms:
            if term in self.idf:
                tf = math.log10(query_terms.count(term) + 1)
                query_weights[term] = tf * self.idf[term]
                norm_query += (tf * self.idf[term]) ** 2
        norm_query = math.sqrt(norm_query)
        doc_scores = defaultdict(float)
        for term, weight_query in query_weights.items():
            if term in self.index:
                for doc_id, weight_doc in self.index[term]:
                    doc_scores[doc_id] += weight_query * weight_doc
        for doc_id in doc_scores:
            if self.length[doc_id] > 0:
                doc_scores[doc_id] /= (self.length[doc_id] * norm_query)
                doc_scores[doc_id] = round(doc_scores[doc_id], 4)
        ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return ranked_docs

# df = pd.read_csv('spotify_songs.csv')
# index = InvertIndex("indice.dat")
# index.building(df, 'lyrics')

# Agregar memoria secundaria en el building
# Obtener índice de memoria secundaria
