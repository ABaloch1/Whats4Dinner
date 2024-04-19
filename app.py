from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL
import mysql.connector
import hashlib

# import MySQLdb.cursors
# import MySQLdb.cursors, re, hashlib

app = Flask(__name__)

app.secret_key = 'this is our top secret super key that definently isnt going to also be uploaded on our github page'

# ---

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'group20'
# app.config['MYSQL_PASSWORD'] = 'group20'
# app.config['MYSQL_DB'] = 'mydatabase'

# ---

# --> Update with user credentials for RBAC
config = {
    'user': 'group20',
    'password': 'group20',
    'host': 'localhost',
    'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)

# ---


@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))
# ---


@app.route('/guest_page')
def guest_page():
    return render_template('guest.html')


@app.route('/login_page')
def login_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])

    message = ''
    return render_template('login.html', message='')


@app.route('/register_page')
def register_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])

    message = ''
    return render_template('register.html', message='')


@app.route('/login/', methods=['GET', 'POST'])
def login():

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        hashed_password = password + app.secret_key
        hashed_password = hashlib.sha256(hashed_password.encode())

        password = hashed_password.hexdigest()

        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password,))

        account = cur.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['Username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password.'

    return render_template('login.html', message=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT * FROM Users WHERE Username = %s', (username,))
        account = cur.fetchone()

        if account:
            msg = 'Username is already taken.'
        elif not username or not password:
            msg = 'Please complete the form.'
        else:
            hashed_password = password + app.secret_key
            hashed_password = hashlib.sha256(hashed_password.encode())

            password = hashed_password.hexdigest()

            try:
	            first_name = request.form['firstName']
	            last_name = request.form['lastName']

	            cur.execute('INSERT INTO Users VALUES (%s,%s,%s,%s)', (username, password, first_name, last_name))
	            cnx.commit()

	            # --
	            checked_allergies = request.form.getlist('allergies')
	            for allergy in checked_allergies:
	                cur.execute(
	                    'INSERT INTO User_Allergens VALUES (%s,%s)', (username, allergy))
	                cnx.commit()
	            # --

	            msg = 'Success! Account registered!'
	            return redirect(url_for('home'))
            except:
            	cnx.rollback()
            	msg = 'Something happenend. Database rolling back.'
            # --

            msg = 'Success! Account registered!'
            return redirect(url_for('home'))

    elif request.method == 'POST':
        msg = 'Incomplete form'
    return render_template('register.html', message=msg)

# @app.route('/login_user')
# def login_user():
# 	return render_template('Loginpage.html')

# @app.route('/login', methods = ['POST', 'GET'])
# def login():
# 	if request.method == 'POST':
# 		try:
# 			un = request.form['username']
# 			ps = request.form['password']
# 			cnx = mysql.connector.connect(**config)
# 			cur = cnx.cursor()
# 			#cur.execute("INSERT ")

# 		except:
# 			pass
# 			#need to add rollback?

# @app.route('/register_user')
# def add_user():
# 	return render_template('adduser.html')

# @app.route('/register', methods = ['POST', 'GET'])
# def register_user():
# 	if request.method == 'POST':
# 		try:		#get the user data from the form
# 			username = request.form['username']
# 			password = request.form['password']
# 			email = request.form['email']

# 			with sql.connect("mydatabase.db") as con:
# 				cur = con.cursor()
# 					# Check if the user already exists
# 				cur.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
# 				exists = cur.fetchone()[0]
# 			if not exists:
# 				pass
# 				#insert the user data in the correct table
# 			cur.execute("INSERT INTO Users (Username, Password, Email) VALUES (?, ?, ?)" (username,password,email) )

# 			con.commit() #commit changes
# 		except:
# 			con.rollback()
# 			return render_template('addUser.html')
# 		finally:
# 			con.close()	#close connection
# 	return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
