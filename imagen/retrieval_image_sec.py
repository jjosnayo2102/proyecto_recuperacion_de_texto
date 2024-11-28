import cv2
import pandas as pd
import numpy as np
import heapq
from collections import defaultdict
import pickle

def ED(P,Q):
    P = np.array(P)
    Q = np.array(Q)
    return np.linalg.norm(abs(P-Q))

def knnsecundario(query, collection):
    max_heap = []
    for f in range(len(collection)):
        dist = ED(collection[f], query)
        if len(max_heap) < 1:
            heapq.heappush(max_heap, (-dist, f))
        else:
            heapq.heappushpop(max_heap, (-dist, f))
    for dist, f in max_heap:
        res = collection[f]
    return res

def knnSearch(query, collection, k):
    max_heap = []
    for f in range(len(collection)):
        dist = ED(collection[f], query)
        if len(max_heap) < k:
            heapq.heappush(max_heap, (-dist, f))
        else:
            heapq.heappushpop(max_heap, (-dist, f))
    res = [f for dist, f in max_heap]
    return res

# Inicializar el detector SIFT
sift = cv2.SIFT_create()

def preprocesar_imagen(url_image):
    # Convertir la imagen a un arreglo NumPy (compatible con OpenCV)
    image_np = np.array(url_image)
    # Convertir la imagen de RGB (Pillow) a BGR (OpenCV)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    # Convertir a escala de grises
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    # Detectar keypoints y calcular descriptores SIFT
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    keypoint_descriptor_pairs = list(zip(keypoints, descriptors))
    keypoint_descriptor_pairs.sort(key=lambda x: x[0].response, reverse=True)
    selected_pairs = keypoint_descriptor_pairs[:10]
    selected_descriptors = np.array([pair[1] for pair in selected_pairs])
    return selected_descriptors

with open("index_image_sec.dat", "rb") as file:
    bd = pickle.load(file)

df = pd.read_csv("imagen/images.csv")

def recuperacion_imagenes_sec(query_image, k):
    vectores = preprocesar_imagen(query_image)
    res_parciales = []
    for query_vector in vectores:
        coleccion = []
        for descriptor in bd:
            nearest_i = knnsecundario(query_vector, descriptor) # se usa la matriz descriptor de cada imagen como una colección
            # se obtiene el descriptor mas cercano a la característica de la inmagen
            coleccion.append(nearest_i)
        nearest = knnSearch(query_vector, coleccion, k)
        res_parciales.append(nearest)
    puntajes = defaultdict(float)
    for i, nearest in enumerate(res_parciales):
      for rank, obj in enumerate(nearest):  # rank es la posición del objeto en el ranking (0 es el primer vecino)
        # Asignar un puntaje inversamente proporcional a la posición
        puntaje = 1 / (rank + 1)  # Un puntaje mayor para los objetos más cercanos (mejor posición)
        puntajes[obj] += puntaje  # Sumar el puntaje total para cada objeto
    ranking_global = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
    res = [x[0] for x in ranking_global[:k]]  # Extraer solo los índices (primeros elementos de las tuplas)
    resd = []
    for index in res:
        titulo = df["filename"].iloc[index]
        url = df["link"].iloc[index]
        d = {"titulo": titulo, "url": url}
        resd.append(d)
    return resd
    

