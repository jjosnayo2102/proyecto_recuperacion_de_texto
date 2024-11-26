import rtree
import cv2
import pandas as pd
import numpy as np

# Cargar el CSV con los enlaces de imágenes
df = pd.read_csv('images.csv')
contenido = df["link"]

# Cargar el índice desde los archivos existentes
idx = rtree.index.Index("rtree")

def preprocesar_imagen(url_image):
    # Convertir la imagen a un arreglo NumPy (compatible con OpenCV)
    image_np = np.array(url_image)
    # Convertir la imagen de RGB (Pillow) a BGR (OpenCV)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    # Convertir a escala de grises
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    # Inicializar el detector SIFT
    sift = cv2.SIFT_create()
    # Detectar keypoints y calcular descriptores SIFT
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return descriptors

def recuperacion_imagenes_rtree(query_image, k):
    vectores = preprocesar_imagen(query_image)
    res_parciales = []
    for query_point in vectores:
        nearest = list(idx.nearest(query_point, num_results=k)) # puntos mas cercanos a característica de imagen
        res_parciales.append(nearest)
        # print(f"Los {k} vecinos más cercanos a {query_point} son:", nearest)
    res = [] 
    # encontrar los más cercanos globales en base a los parciales
    resd = []
    for index in res:
        titulo = df["filename"].iloc[index-1]
        url = df["link"].iloc[index-1]
        d = {"titulo": titulo, "url": url}
        resd.append(d)
    return d

