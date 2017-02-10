from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', one=10, two=5)

@app.route('/survey', methods=['POST'])
def create():
    response = {
        'name':request.form['name'],
        'language':request.form['language'],
        'location':request.form['location'],
        'comment':request.form['comment'],
    }
    return render_template('result.html', response=response)

app.run(debug=True)
