######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from datetime import datetime
from flask import Flask, Response, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import flask_login
import config

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'dev'

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = config.User
app.config['MYSQL_DATABASE_PASSWORD'] = config.Password
app.config['MYSQL_DATABASE_DB'] = config.DB
app.config['MYSQL_DATABASE_HOST'] = config.Host
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()

with open('schema.sql', 'r') as f:
	with conn.cursor() as cursor:
		for line in f.read().split(';\n'):
			cursor.execute(line)
	conn.commit()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit' value='Log In'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		fname=request.form.get('fname')
		lname=request.form.get('lname')
		email=request.form.get('email')
		password=request.form.get('password')
		hometown=request.form.get('hometown')
		dob=request.form.get('dob')
		gender=request.form.get('gender')

	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (fname, lname, email, hometown, dob, gender, password) \
								VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')"
								.format(fname, lname, email, hometown, dob, gender, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))


#Gets album info
def getUserAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name FROM Albums WHERE owner_id = '{0}'".format(uid))
	return cursor.fetchall()

#Gets photos in specific album
def getAlbumPhotos(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE photo_id IN \
					(SELECT photo_id FROM PhotoAlbums WHERE album_id = '{0}')".format(aid))
	return cursor.fetchall() 

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getSinglePhoto(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE photo_id = '{0}'".format(pid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

#Gets photos that don't belong to any albums
def getUsersFreePhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE photo_id NOT IN (SELECT photo_id FROM PhotoAlbums) \
						AND user_id = '{0}'".format(uid))
	return cursor.fetchall()

#Gets photos with specific tag
def getTaggedPhotos(tid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE photo_id IN \
					(SELECT photo_id FROM Tagged WHERE tag_id = '{0}')".format(tid))
	return cursor.fetchall()

# Gets comments info
def getComments(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT comment_text, email, date_created FROM Comments, Users WHERE photo_id = {0} AND user_id = owner_id".format(pid))
	return cursor.fetchall()

# Gets user emails of those who liked photo
def getLikes(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id IN (SELECT user_id FROM Likes WHERE photo_id = '{0}')".format(pid))
	return cursor.fetchall()

# Checks if user is among the list of likes
def userinLikes(uid, pid):
	cursor = conn.cursor
	cursor.execute("SELECT COUNT(*) FROM Likes WHERE user_id IN (SELECT user_id FROM Likes WHERE photo_id = '{0}' AND user_id = {1})".format(pid, uid))

# Gets number of likes for a photo
def getNumLikes(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(user_id) AS NumOfLikes FROM Likes WHERE photo_id = '{0}'".format(pid))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

#Gets friends list
def getUsersFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT friend_id FROM Follows WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

#Gets users with mutual friends
def getFriendsofFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Follows WHERE friend_id IN dbo.getUsersFriends('{0}') \
					AND user_id <> '{0}'".format(uid))
	return cursor.fetchall()

#Inserts friend relationship
def insertFriends(email1, email2):
	cursor = conn.cursor()
	uid1 = getUserIdFromEmail(email1)
	uid2 = getUserIdFromEmail(email2)
	print(cursor.execute("INSERT INTO Follows (user_id, friend_id) VALUES ('{0}', '{1}')" \
							.format(uid1, uid2)))
	conn.commit()

#Deletes friend relationship
def deleteFriends(fid):
	cursor = conn.cursor()
	print(cursor.execute("DELETE FROM Follows WHERE friend_id = '{0}'".format(fid)))
	conn.commit()

#Inserts album info
def insertAlbum(uid, aname, date):
	cursor = conn.cursor()
	print(cursor.execute("INSERT INTO Albums (album_name, owner_id, date_created) VALUES ('{0}', '{1}', '{2}')" \
							.format(aname, uid, date)))
	conn.commit()

#Deletes specific photo
def deletePhoto(pid):
	cursor = conn.cursor()
	print(cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(pid)))
	conn.commit()
	print(cursor.rowcount, "record(s) deleted")

#Delete specific album and its photos
def deleteAlbums (aid):
	cursor = conn.cursor()
	print(cursor.execute("DELETE FROM Photos WHERE photo_id IN (SELECT photo_id FROM PhotoAlbums WHERE album_id = \
							'{0}')".format(aid)))
	print(cursor.execute("DELETE FROM Albums WHERE album_id = '{0}'".format(aid)))
	conn.commit()

#Deletes photo relationship to an album
def deletePhotoAlbum (pid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM PhotoAlbums WHERE photo_id = '{0}'".format(pid))
	conn.commit()

#Inserts photo relationship to an album
def insertPhotoAlbum(aid, pid):
	cursor = conn.cursor()
	print(cursor.execute("INSERT INTO PhotoAlbums (album_id, photo_id) VALUES ('{0}', '{1}')" \
							.format(aid, pid)))
	conn.commit()

#Inserts tag info
def insertTags(tname):
	cursor = conn.cursor()
	print(cursor.execute("INSERT INTO Tags (tag_name) SELECT * FROM (SELECT '{0}') AS tmp \
							WHERE NOT EXISTS (SELECT tag_id FROM Tags WHERE tag_name = '{0}') LIMIT 1".format(tname)))
	conn.commit()

#Inserts relationship between photo and tag
def insertTagged(tname, pid):
	cursor = conn.cursor()
	insertTags(tname)
	print(cursor.execute("INSERT INTO Tagged (photo_id) VALUES ('{0}')".format(pid)))
	conn.commit()

#Inserts comment info
def insertComments(ctxt, uid, pid):
	cursor = conn.cursor()
	now = datetime.now()
	formatted_date = now.strftime('%Y-%m-%d')
	print(cursor.execute("INSERT INTO Comments (comment_text, owner_id, date_created, photo_id) VALUES ('{0}', '{1}', '{2}', '{3}')" \
							.format(ctxt, uid, formatted_date, pid)))
	conn.commit()

def insertLikes(uid, pid):
	cursor = conn.cursor()
	print(cursor.execute("INSERT INTO Likes VALUES ('{0}', '{1}')".format(uid, pid)))
	conn.commit()

#Deletes a tag
def deleteTags(tname):
	cursor = conn.cursor()
	print(cursor.execute("DELETE FROM Tags WHERE tag_name = '{0}'".format(tname)))
	conn.commit()

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code


#Personal profile page
@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", photos=getUsersFreePhotos(uid), albums=getUserAlbums(uid), owner = True, base64=base64)

#Loads Other Users' profiles
@app.route('/user/<email>')
def show_user_profile(email):
	uid = getUserIdFromEmail(email)
	return render_template('hello.html', message="Here's {0}'s profile".format(email), photos=getUsersFreePhotos(uid), albums=getUserAlbums(uid), owner = False, base64=base64)

#Passes search query to load user profile
@app.route('/usersearch', methods=['Post'])
def pass_user_profile():
	umail = request.form.get('search')
	return redirect(url_for('show_user_profile', email = umail))

#Loads page for viewing personal album
@app.route('/profile/viewalbum<int:album_id>')
@flask_login.login_required
def viewalbum(album_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('editalbum.html', name=flask_login.current_user.id, picsinalbum=getAlbumPhotos(album_id), owner = True, edit = False, base64=base64)

#Loads page for viewing other Users' album
@app.route('/user/viewalbum<int:album_id>')
@flask_login.login_required
def viewUseralbum(album_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('editalbum.html', message="Here's their album", name=flask_login.current_user.id, picsinalbum=getAlbumPhotos(album_id), owner = False, edit = False, base64=base64)

#Loads page for viewing personal posts/comments
@app.route('/profile/viewpost<int:photo_id>')
@flask_login.login_required
def viewpost(photo_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('viewpost.html', name=flask_login.current_user.id, photos=getSinglePhoto(photo_id), comments = getComments(photo_id), owner = True, base64=base64)

#Loads page for viewing other Users' personal posts/comments
@app.route('/user/viewpost<int:photo_id>')
def viewuserpost(photo_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('viewpost.html', name=flask_login.current_user.id, photos=getSinglePhoto(photo_id), comments = getComments(photo_id), owner = False, base64=base64)

#Handles comment insertion into a post
@app.route('/user/addcomment<int:photo_id>', methods=['Post'])
def addcomment(photo_id):
	ctxt = request.form.get('comment')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	insertComments(ctxt, uid, photo_id)
	return redirect(request.referrer)


#Handles photo deletion
@app.route('/profile/delete/p<int:photo_id>', methods=['Post'])
@flask_login.login_required
def delete_photo(photo_id):
	deletePhoto(photo_id)
	return redirect(request.referrer)

#Handles adding photos to album
@app.route('/profile/add_photo/<int:photo_id>', methods=['Post'])
@flask_login.login_required
def add_photoalbum(photo_id):
	pid = photo_id
	insertPhotoAlbum(session['aid'], pid)
	return redirect(request.referrer)

#Handles photo removal from album
@app.route('/profile/remove_photo/<int:photo_id>', methods=['Post'])
@flask_login.login_required
def remove_photo(photo_id):
	pid = photo_id
	deletePhotoAlbum(pid)
	return redirect(request.referrer)

#Handles album deletion
@app.route('/profile/delete/a<int:album_id>', methods=['Post'])
@flask_login.login_required
def delete_album(album_id):
	deleteAlbums(album_id)
	return redirect(url_for('protected'))

#Loads edit page for modifying album
@app.route('/profile/edit/a<int:album_id>', methods=['Post', 'Get'])
@flask_login.login_required
def edit_album(album_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	aid = album_id
	session['aid'] = aid
	return render_template('editalbum.html', name=flask_login.current_user.id, message="Add or remove photos from your album", photos=getUsersFreePhotos(uid), picsinalbum=getAlbumPhotos(aid), owner = True, edit = True, base64=base64)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		print(cursor.execute('''INSERT INTO Photos (imgdata, user_id, caption) VALUES (%s, %s, %s )''', (photo_data, uid, caption)))
		conn.commit()
		return redirect('profile')
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

@app.route('/create', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		aname = request.form.get('album_name')
		cursor = conn.cursor()
		now = datetime.now()
		formatted_date = now.strftime('%Y-%m-%d')
		print(cursor.execute("INSERT INTO Albums (album_name, owner_id, date_created) VALUES ('{0}', '{1}', '{2}')".format(aname, uid, formatted_date)))
		conn.commit()
		return redirect('profile')
	#The method is GET so we return a  HTML form to create an album.
	else:
		return render_template('create.html')

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)