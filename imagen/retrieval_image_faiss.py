import cv2
import pandas as pd
import numpy as np
from collections import defaultdict
import pickle
import faiss

# Cargar el CSV con los enlaces de imágenes
df = pd.read_csv('imagen/images.csv')

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

# Cargar image_ids desde un archivo .pkl
with open('image_ids_faiss_1000.pkl', 'rb') as f:
    image_ids = pickle.load(f)

indice = faiss.read_index('faiss_index_1000.bin')

def recuperacion_imagenes_faiss(query_image, k):
    vectores = preprocesar_imagen(query_image)
    res_parciales = []
    for query_point in vectores:
        query_point = np.expand_dims(query_point, axis=0)
        _,nearest = indice.search(query_point, k)
        # conversión con la imagen a la que pertenece cada indice (posición del search)
        top = [image_ids[i] for i in nearest[0]] # corregir
        res_parciales.append(top)
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
