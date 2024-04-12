from flask import Flask
import mysql.connector

app = Flask(__name__)

from flask_mysqldb import MySQL
'''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'rose'
app.config['MYSQL_PASSWORD'] = 'rose'
app.config['MYSQL_DB'] = 'MyDB'
'''
config = {
	'user': 'rose',
	'password': 'rose',
	'host': 'localhost',
	'database': 'mydatabase',
}

@app.route('/')
def home():
	return render_template('index.html')
    
@app.route('/login', methods = ['POST', 'GET']
def login():
	if request.method = 'POST':
		try:
			un = request.form['username']
			ps = request.form['password']
			cnx = mysql.connector.connect(**config)
			cur = cnx.cursor()
			#cur.execute("INSERT ")
			
		except: 
			#need to add rollback?
    
@app.route('/add_user')
def add_user():
	return render_template('addUser.html')

@app.route('/user_creation', methods = ['POST', 'GET'])
def submit_review():
	if request.method == 'POST':
		try:		#get the user data from the form
			username = request.form['username']
			password = request.form['password']
			email = request.form['email']
  			
			with sql.connect("mydatabase.db") as con:
			cur = con.cursor()
				# Check if the user already exists
			cur.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
			exists = cur.fetchone()[0]
			if not exists:
				#insert the user data in the correct table
			cur.execute("INSERT INTO Users (Username, Password, Email) VALUES (?, ?, ?)" (username,password,email) )
            
			con.commit() #commit changes
		except:
			con.rollback()
			return render_template('addUser.html')
		finally:
			con.close()	#close connection
	return render_template("index.html")

if __name__ == '__main__':
	app.run(debug=True)
