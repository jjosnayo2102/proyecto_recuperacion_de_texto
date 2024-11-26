import rtree
import cv2
import pandas as pd
import urllib.request
import numpy as np

# Inicializar el R-tree
prop = rtree.index.Property()
prop.dimension = 128
prop.buffering_capacity = 4
prop.dat_extension = "data"
prop.idx_extension = "index"
idx = rtree.index.Index("rtree", properties=prop)

# Inicializar el detector SIFT
sift = cv2.SIFT_create()

# Función para extraer características de una imagen desde una URL
def extract_sift_features(url):
    try:
        # Descargar la imagen
        resp = urllib.request.urlopen(url)
        img_array = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)  # Leer la imagen

        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detectar keypoints y calcular descriptores SIFT
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        return descriptors  # Devolver los descriptores SIFT
    except Exception as e:
        print(f"Error procesando la imagen en {url}: {e}")
        return None

# Cargar el CSV con los enlaces de imágenes
df = pd.read_csv('images.csv')

# Procesar las imágenes
for index, row in df.iterrows():
    if index > 2:
        break
    url = row['link']
    descriptors = extract_sift_features(url)
    if descriptors is not None:
        for vector in descriptors:
            # Usar las dos primeras dimensiones del descriptor como coordenadas 2D
            coord = tuple(vector)
            # Insertar en el R-tree con el ID de la imagen
            idx.insert(index, coord)
