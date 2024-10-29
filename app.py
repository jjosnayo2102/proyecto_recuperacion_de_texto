from flask import Flask, render_template, request
from retrieval import recuperacion
from retrieval_postgresql import recuperacion_postgresql
# Importa la función para recuperación de imágenes, si ya la tienes
# from retrieval_images import recuperacion_imagenes
import time

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
            results = recuperacion(query_text, k)
            # results = [{"titulo": "temporal", "puntaje": -1, "autor": "temporal", "letra": "temporal"}]
        elif method == 'postgresql':
            results = recuperacion_postgresql(query_text, k)
        return render_template('texto.html', results=results)
    return render_template('texto.html', results=None)

@app.route('/image', methods=['GET', 'POST'])
def image_retrieval():
    if request.method == 'POST':
        query_image = request.form['query_image']
        k = int(request.form['k'])
        # Supón que tienes una función llamada `recuperacion_imagenes`
        # results = recuperacion_imagenes(query_image, k)
        # Aquí solo es un ejemplo, adapta `results` a tu implementación de recuperación de imágenes
        results = [
            {'image_url': 'url_de_la_imagen_1', 'title': 'Título 1'},
            {'image_url': 'url_de_la_imagen_2', 'title': 'Título 2'},
        ]
        return render_template('imagen.html', results=results)
    return render_template('imagen.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
