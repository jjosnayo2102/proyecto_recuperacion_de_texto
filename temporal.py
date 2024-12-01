import faiss
import numpy as np

# Crear un conjunto de vectores aleatorios
dimension = 128
num_vectors = 1000
vectors = np.random.random((num_vectors, dimension)).astype('float32')

# Crear un índice FAISS (L2 es la distancia euclidiana)
index = faiss.IndexFlatL2(dimension)

# Añadir vectores al índice
index.add(vectors)

# Buscar los k vectores más cercanos
query_vector = np.random.random((1, dimension)).astype('float32')
k = 5
distances, indices = index.search(query_vector, k)

print("Distancias:", distances)
print("Índices:", indices)
