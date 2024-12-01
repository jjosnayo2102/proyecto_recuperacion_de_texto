from flask import Flask, render_template, request, url_for
from texto.fetch import default_value
from texto.retrieval import recuperacion
from texto.retrieval_postgresql import recuperacion_postgresql
from imagen.retrieval_image_rtree import recuperacion_imagenes_rtree
from imagen.retrieval_image_sec import recuperacion_imagenes_sec
from imagen.retrieval_image_faiss import recuperacion_imagenes_faiss
import time
from PIL import Image

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/text', methods=['GET', 'POST'])
def text_retrieval():
    if request.method == 'POST':
        query_text = request.form['query_text']
        k = int(request.form['k'])
        method = request.form['method']
        if method == 'propia':
            inicio = time.time()
            results = recuperacion(query_text, k)
            final = time.time()
            tiempo_propio = round((final - inicio)*1000,4)
            print(f"Tiempo de ejecución: {tiempo_propio} ms")
        elif method == 'postgresql':
            inicio = time.time()
            results = recuperacion_postgresql(query_text, k)
            final = time.time()
            tiempo_postgresql = round((final - inicio)*1000,4)
            print(f"Tiempo de ejecución: {tiempo_postgresql} ms")
        return render_template('texto.html', results=results)
    return render_template('texto.html', results=None)

@app.route('/image', methods=['GET', 'POST'])
def image_retrieval():
    if request.method == 'POST':
        query_image = request.files['query_image']
        k = int(request.form['k'])
        image = Image.open(query_image)
        method = request.form['method']
        if method == "secuencial":
            inicio = time.time()
            results = recuperacion_imagenes_sec(image,k)
            final = time.time()
            tiempo_sec = round((final - inicio)*1000,4)
            print(f"Tiempo de ejecución: {tiempo_sec} ms")
        elif method == "rtree":
            inicio = time.time()
            results = recuperacion_imagenes_rtree(image, k)
            final = time.time()
            tiempo_rtree = round((final - inicio)*1000,4)
            print(f"Tiempo de ejecución: {tiempo_rtree} ms")
        elif method == "faiss":
            inicio = time.time()
            results = recuperacion_imagenes_faiss(image,k)
            final = time.time()
            tiempo_faiss = round((final - inicio)*1000,4)
            print(f"Tiempo de ejecución: {tiempo_faiss} ms")
        else:
            results = [{"titulo": "15970.jpg", "url": "http://assets.myntassets.com/v1/images/style/properties/7a5b82d1372a7a5c6de67ae7a314fd91_images.jpg"},
                   {"titulo": "39386.jpg", "url": "http://assets.myntassets.com/v1/images/style/properties/4850873d0c417e6480a26059f83aac29_images.jpg"},
                   {"titulo": "59263.jpg", "url": "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg"}
                   ,{"titulo": "21379.jpg", "url": "http://assets.myntassets.com/v1/images/style/properties/8153dc35d9a5420eeb93922067137db6_images.jpg"}]
        return render_template('imagen.html', results=results)
    return render_template('imagen.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
