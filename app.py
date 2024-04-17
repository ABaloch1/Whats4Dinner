import mysql.connector
from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL

app = Flask(__name__)



# ---
'''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'rose'
app.config['MYSQL_PASSWORD'] = 'rose'
app.config['MYSQL_DB'] = 'MyDB'
'''
#---

config = {
	'user': 'group20',
	'password': 'group20',
	'host': 'localhost',
	'database': 'mydatabase',
}

#---

@app.route('/')
def home():
	return render_template('welcome.html')

# @app.route('/guestroute')
# def guest_route():
#     # Your logic here
#     return redirect(url_for('guest_page'))

# @app.route('/loginroute')
# def login_route():
#     # Your logic here
#     return redirect(url_for('login_page'))

# @app.route('/registerroute')
# def register_route():
#     # Your logic here
#     return redirect(url_for('register_page'))

#---

@app.route('/guest_page')
def guest_page():
    return render_template('guest.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/register_page')
def register_page():
    return render_template('register.html')

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
