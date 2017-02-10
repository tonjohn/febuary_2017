from flask import Flask, render_template, request, redirect, session, flash

import re, datetime
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^[a-zA-Z0-9]+$')

app = Flask(__name__)
app.secret_key = 'mySecretKey'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    errors = []
    if not len(request.form['first_name']):
        errors.append({'error': 'First name is required!', 'category': 'first_name'})
    if not request.form['first_name'].isalpha():
        errors.append({'error': 'Only alphabetic characters are accepted!', 'category': 'first_name'})
    if not len(request.form['last_name']):
        errors.append({'error': 'Last name is required!', 'category': 'last_name'})
    if not request.form['last_name'].isalpha():
        errors.append({'error': 'Only alphabetic characters are accepted!', 'category': 'last_name'})
    if not len(request.form['email']):
        errors.append({'error': 'Email is required!', 'category': 'email'})
    if not len(request.form['dob']):
        errors.append({'error': 'Date of birth is required!', 'category': 'dob'})
    if request.form['dob'] >= str(datetime.date.today()):
        errors.append({'error': 'Date of birth must be in the past!', 'category': 'dob'})
    if len(request.form['password']) < 8:
        errors.append({'error': 'Password must be at least 8 characters long!', 'category': 'password'})
    if not PASSWORD_REGEX.match(request.form['password']):
        errors.append({'error': 'Password must contain at least 1 number and uppercase letter!', 'category': 'password'})
    if not EMAIL_REGEX.match(request.form['email']):
        errors.append({'error': 'Please enter a valid email!', 'category': 'email'})
    if not request.form['password'] == request.form['confirm_password']:
        errors.append({'error': 'Passwords must match!', 'category': 'confirm_password'})

    if errors:
        for error in errors:
            flash(error['error'], error['category'])
    else:
        flash('Thank you for submitting you information!', 'success')
    return redirect('/')

app.run(debug=True)
