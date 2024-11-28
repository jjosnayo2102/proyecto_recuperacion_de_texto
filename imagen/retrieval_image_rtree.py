# no eficiente: miles de busquedas con millones de vectores por query
import rtree
import cv2
import pandas as pd
import numpy as np
from collections import defaultdict

# Cargar el CSV con los enlaces de imágenes
df = pd.read_csv('imagen/images.csv')

# Cargar el índice desde los archivos existentes
prop = rtree.index.Property()
prop.dimension = 128
prop.buffering_capacity = 64
idx = rtree.index.Index("rtree", properties=prop)

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

def recuperacion_imagenes_rtree(query_image, k):
    vectores = preprocesar_imagen(query_image)
    res_parciales = []
    for query_point in vectores:
        query_point = tuple(query_point)
        nearest = list(idx.nearest(query_point, num_results=k)) # puntos mas cercanos a característica de 
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