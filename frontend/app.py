from flask import Flask, render_template, request
from recuperacion import retrieve_text

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        user_input = request.form['user_input']
        num_elements = int(request.form['num_elements'])
        option = request.form['option']
        
        results = retrieve_text(user_input, num_elements, option)
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)