from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = 'ThisIsSecret'

@app.route('/')
def index():
    return render_template('index.html', one=10, two=5)

@app.route('/survey', methods=['POST'])
def create():
    errors = []
    if not len(request.form['name']):
        errors.append('Name field required!')
    if not len(request.form['comment']):
        errors.append('Comment field required!')
    if len(request.form['comment']) > 120:
        errors.append('Comments must be less than 120 characters long!')

    if errors:
        for error in errors:
            flash(error)
        return redirect('/')
    else:
        session['name'] = request.form['name']
        session['language'] = request.form['language']
        session['location'] = request.form['location']
        session['comment'] = request.form['comment']
        return redirect('/result')

@app.route('/result')
def result():
    return render_template('result.html')

app.run(debug=True)
