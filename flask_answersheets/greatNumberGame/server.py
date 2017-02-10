from flask import Flask, render_template, redirect, request, session
import random
app = Flask(__name__)
app.secret_key='lksadflsjdf'

@app.route('/')
def index():
    if 'random' not in session:
        session['random'] = random.randint(1, 100)
    return render_template('index.html')

@app.route('/guess', methods=['POST'])
def guess():
    print request.form['guess']
    session['guess'] = {}
    if int(request.form['guess']) > session['random']:
        cclass = 'high'
        result = 'Guess is to high!'
    elif int(request.form['guess']) < session['random']:
        cclass = 'low'
        result = 'Guess is to low!'
    else:
        cclass = 'correct'
        result = "You're correct, how did you know?"

    session['guess']['class'] = cclass
    session['guess']['result'] = result

    print session['guess']
    return redirect('/')

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return redirect('/')

app.run(debug=True)
