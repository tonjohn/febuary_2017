from flask import Flask, render_template, request, redirect, session, flash
import time
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'ILikePonies' 
# our index route will handle rendering our form
@app.route('/')
def index():
	if not 'first_name' in session:
		session.first_name = ""
	if not 'last_name' in session:
		session.last_name = ""
	if not 'email' in session:
		session.email = ""
	if not 'error' in session:
		session.email = ""
		session.last_name = ""
		session.first_name = ""

	return render_template("index.html")
# this route will handle our form submission
# notice how we defined which HTTP methods are allowed by this route
@app.route('/submit', methods=['POST'])
def handle_survey():
	
	error = False

	if len(request.form['email']) < 1:
		flash("Email cannot be blank")
		error = True
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("Invalid Email Address", 'error')
		error = True
	else:
		session['email'] = request.form['email']

	session['first_name'] = request.form['first_name']
	if( not session['first_name'].isalpha() ):
		session.pop("first_name")
		error = True
		flash("Invalid First Name", "error")

	session['last_name'] = request.form['last_name']
	print session['last_name'], request.form['last_name']
	if( not session['last_name'].isalpha() ):
		session.pop('last_name')
		error = True
		flash("Invalid Last Name", "error")

	if( len(request.form['password']) <= 8 ):
		error = True
		flash("Password must be greater than 8 characters")
	elif( request.form['password'] != request.form['confirm_password']):
		error = True
		flash("Passwords do not match", "error")
	# elif( False )
	# 	error = True
	# 	flash("Password must contain 1 uppercase letter and 1 number")

	# 1986-05-15
	print "DOB:", request.form['dob']
	if len(request.form['dob']) > 0:
		dob = time.strptime(request.form['dob'], '%Y-%m-%d')
		tNow = time.strptime(time.asctime())
		print dob[0]

		print "Dob:", dob
		print "tNow:", tNow
		if dob[0] >= tNow[0]:
			error = True
			flash('Must be older than 1 year', 'error')
		# time.struct_time(tm_year=1986, tm_mon=5, tm_mday=15, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=135, tm_isdst=-1)
	else:
		error = True
		flash('Please provide your Date of Birth', 'error')

	if( error == True ):
		session['error'] = True
	else:
		if 'error' in session:
			session.pop('error')
		flash("Thanks for submitting your information.", "success")

	return redirect('/')

@app.route('/results')
def display_results():
	return render_template("results.html")

@app.route('/reset')
def reset():
	session.clear()
	return redirect('/')

app.run(debug=True) # run our server
