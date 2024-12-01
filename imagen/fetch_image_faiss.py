import cv2
import numpy as np
import faiss
import pandas as pd
import urllib.request
import pickle

# Función para extraer características SIFT
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
        # Seleccionar los top_k descriptores más importantes
        keypoint_descriptor_pairs = list(zip(keypoints, descriptors))
        keypoint_descriptor_pairs.sort(key=lambda x: x[0].response, reverse=True)
        selected_descriptors = np.array([pair[1] for pair in keypoint_descriptor_pairs[:top_k]])
        return selected_descriptors
    except Exception as e:
        print(f"Error procesando la imagen en {url}: {e}")
        return None

# Cargar el CSV con los enlaces de imágenes
df = pd.read_csv('images.csv')

# Inicializar la lista de descriptores y sus IDs
all_descriptors = []
image_ids = []

# Procesar las imágenes
for index, row in df.iterrows():  # cuenta desde 0 sin contar header
    if index == 10000:
        break
    url = row['link']
    descriptors = select_top_sift_features(url, top_k=10)
    if descriptors is not None:
        all_descriptors.extend(descriptors)
        # Asociar el ID de la imagen con cada descriptor
        image_ids.extend([index] * len(descriptors))  # Usamos 'index' como ID de imagen

# Convertir a un numpy array de tipo float32 para FAISS
all_descriptors = np.array(all_descriptors, dtype='float32')

# Crear el índice FAISS
dimension = 128  # Los descriptores SIFT tienen dimensión 128
index = faiss.IndexFlatL2(dimension)

# Añadir los descriptores al índice
index.add(all_descriptors)

# Guardar el índice FAISS en un archivo
faiss.write_index(index, 'faiss_index.bin')

# Guardar image_ids en un archivo .pkl
with open('image_ids.pkl', 'wb') as f:
    pickle.dump(image_ids, f)
