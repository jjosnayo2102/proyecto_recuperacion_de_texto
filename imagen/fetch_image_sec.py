# el fetch demora mucho para miles de datos
import cv2
import pandas as pd
import numpy as np
import urllib.request
import pickle

# Inicializar el detector SIFT
sift = cv2.SIFT_create()

# Función para extraer características de una imagen desde una URL
def select_top_sift_features(url, top_k=10):
    try:
        resp = urllib.request.urlopen(url)
        img_array = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sift = cv2.SIFT_create()
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        if descriptors is None:
            return None
        keypoint_descriptor_pairs = list(zip(keypoints, descriptors))
        keypoint_descriptor_pairs.sort(key=lambda x: x[0].response, reverse=True)
        selected_pairs = keypoint_descriptor_pairs[:top_k]
        selected_descriptors = np.array([pair[1] for pair in selected_pairs])
        return selected_descriptors
    except Exception as e:
        print(f"Error procesando la imagen en {url}: {e}")
        return None

# Cargar el CSV con los enlaces de imágenes
df = pd.read_csv('images.csv')

bd = []
# Procesar las imágenes
for index, row in df.iterrows(): # cuenta desde 0 sin contar header
    url = row['link']
    if index == 1000:
        break
    # extraer solo algunas caracteristicas
    descriptors = select_top_sift_features(url)
    if descriptors is not None:
        bd.append(descriptors)
    else:
        bd.append([[]])

with open("index_image_sec.dat", "wb") as archivo:
    pickle.dump(bd, archivo)