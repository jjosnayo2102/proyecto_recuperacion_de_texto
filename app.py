from flask import Flask, render_template, request
from retrieval import recuperacion
from retrieval_postgresql import recuperacion_postgresql

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query_text = request.form['query_text']
        k = int(request.form['k'])
        method = request.form['method']
        if method == 'propia':
            results = recuperacion(query_text, k)
        elif method == 'postgresql':
            results = recuperacion_postgresql(query_text, k)
        return render_template('index.html', results=results)
    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
