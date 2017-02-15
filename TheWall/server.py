from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import time
import datetime
import re
from flask.ext.bcrypt import Bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'ILikePonies' 
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'thewall')

# Should we use some helper functions? ex/ return registration();
def validate_user():
	print session
	if not 'user_id' in session or session['user_id'] <= 0:
		# if we don't have a user_id OR it is an invalid id, login
		return {'valid' : False, 'render' : render_template("login.html") }
	return {'valid' : True }
	# call at top of every page
	# if user is invalid, render login template
	# or maybe just redirect index?
# print mysql.query_db("SELECT * FROM states")

@app.route('/')
def index():

	if 'user_id' in session and session['user_id'] > 0:
		# user is logged in, send him to the wall with jon snow!
		print "Logged in with UserID ", session['user_id']
		return redirect('/wall')

	# if not 'user_id' in session or session['user_id'] <= 0:
	# 	# if we don't have a user_id OR it is an invalid id, login
	# 	return render_template("index.html")

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

	return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():

	if 'user_id' in session and session['user_id'] > 0:
		redirect('/reset')

	print request.form
	error = False
	if request.form['action'] == "Login":
		print "Processing Login for", request.form['email']
		if EMAIL_REGEX.match(request.form['email']) and len(request.form['password']) > 8:
			# user is logging in and has entered 'legit' data
			data = {'email' : request.form['email'] }
			results = mysql.query_db("SELECT id, first_name, last_name, password FROM users WHERE email = :email LIMIT 1", data )
		
			if len(results) > 0 and bcrypt.check_password_hash(results[0]['password'], request.form['password']):
				results = results[0]
				session['user_id'] = results['id']
				session['first_name'] = results['first_name']
				session['last_name'] = results['last_name']
				return redirect('/wall')
			else:
				# retry login or register if you don't have an account
				# login form with optional fields to register?
				flash("Invalid email or password", 'error')
				session['email'] = request.form['email']
				error = True

		else:
			#flash message and error out
			flash("Invalid email or password", 'error')
			error = True

	elif request.form['action'] == "Register":
		print "Processing registration!"
		if not EMAIL_REGEX.match(request.form['email']):
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

		if not error:
			data = {'first_name': request.form['first_name'], 'last_name' : request.form['last_name'], 'email' : request.form['email'], 'password' : bcrypt.generate_password_hash( request.form['password'] ) }
			results = mysql.query_db(u"INSERT IGNORE INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ( :first_name, :last_name, :email, :password, NOW(), NOW() )", data)
			print "New UserID:", results
			session['user_id'] = results



	return redirect('/')

@app.route('/wall')
def castle_black():
	isValidUser = validate_user()
	if isValidUser['valid'] == False:
		return isValidUser['render']

	query = "SELECT messages.id AS message_id, users.id AS user_id, CONCAT(users.first_name, \" \", users.last_name) AS name, messages.message, messages.created_at, messages.updated_at FROM messages JOIN users ON users.id = messages.user_id ORDER BY messages.created_at DESC LIMIT 100"
	results = mysql.query_db(query)
	#print results
	for index, message in enumerate(results):
		#print "Message:", message
		query = "SELECT users.id AS user_id, CONCAT(users.first_name, \" \", users.last_name) AS name, comments.comment, comments.created_at, comments.updated_at FROM comments JOIN users ON users.id = comments.user_id WHERE comments.message_id = :message_id ORDER BY comments.created_at ASC LIMIT 1000"
		data = { 'message_id' : int(message['message_id']) }
		comments = mysql.query_db(query, data)
		results[index]['comments'] = comments


	return render_template("wall.html", messages = results, datetime = datetime, str = str )

	# query all posts on the wall
		# for each post, query comments

@app.route('/message', methods=['POST'])
def post_message():
	#TODO RATE LIMITING
	error = False

	if not 'post' in request.form or ('post' in request.form and len(request.form['post']) < 5):
		flash("Post must be at least 5 characters")
		error = True
	else:
		query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES(:message, :user_id, NOW(), NOW())"
		data = { 'message' : request.form['post'], 
				'user_id' : session['user_id']
		}
		result = mysql.query_db( query, data )
		session['last_post'] = time.asctime()


	if( error == True ):
		session['error'] = True
	else:
		if 'error' in session:
			session.pop('error')
		flash("Posted!", "success")

	return redirect('/wall')

@app.route('/message/<message_id>')
def view_message(message_id):
	# view a single message thread
	isValidUser = validate_user()
	if isValidUser['valid'] == False:
		return isValidUser['render']

	if message_id.isdigit() and int(message_id) > 0:
		query = "SELECT messages.id AS message_id, users.id AS user_id, CONCAT(users.first_name, \" \", users.last_name) AS name, messages.message, messages.created_at, messages.updated_at FROM messages JOIN users ON users.id = messages.user_id WHERE messages.id = :message_id LIMIT 1"
		data = { 'message_id' : message_id }
		results = mysql.query_db(query, data)
		for index, message in enumerate(results):
			#print "Message:", message
			query = "SELECT users.id AS user_id, CONCAT(users.first_name, \" \", users.last_name) AS name, comments.comment, comments.created_at, comments.updated_at FROM comments JOIN users ON users.id = comments.user_id WHERE comments.message_id = :message_id ORDER BY comments.created_at ASC LIMIT 1000"
			data = { 'message_id' : int(message['message_id']) }
			comments = mysql.query_db(query, data)
			results[index]['comments'] = comments
	else:
		return redirect('/wall')

	return render_template("wall.html", messages = results, datetime = datetime, str = str )


@app.route('/comment', methods=['POST'])
def post_comment():
	#TODO RATE LIMITING
	error = False

	if not 'post' in request.form or ('post' in request.form and len(request.form['post']) < 5):
		flash("Post must be at least 5 characters")
		error = True
	else:
		query = "INSERT INTO comments (comment, user_id, message_id, created_at, updated_at) VALUES(:comment, :user_id, :message_id, NOW(), NOW())"
		data = { 'comment' : request.form['post'], 
				'user_id' : session['user_id'],
				'message_id' : request.form['message_id']
		}
		result = mysql.query_db( query, data )
		session['last_post'] = time.asctime()


	if( error == True ):
		session['error'] = True
	else:
		if 'error' in session:
			session.pop('error')
		flash("Posted!", "success")

	if 'ajax' in request.form:
		return render_template('comments.html')

	return redirect('/wall')

@app.route('/reset')
def reset():
	session.clear()
	return redirect('/')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    #r.headers['Cache-Control'] = 'public, max-age=0'
    return r

app.run(debug=True) # run our server
