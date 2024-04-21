from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
# from flask_mysqldb import MySQL
import mysql.connector
import hashlib

# import MySQLdb.cursors
# import MySQLdb.cursors, re, hashlib

from auth import auth

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(recipes)

#---

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

	try: 
		print(session['username'])
	except:
		print("no session")

	return render_template('welcome.html')



# ---


@app.route('/guest_page')
def guest_page():
    return render_template('guest.html')


@app.route('/ingredient_creation', methods=['POST', 'GET'])
def create_ingredient():
	if request.method == 'POST':
		try:
			name = request.form['name']
			allergy = request.form['allergy']
			category = request.form['category']
			with sql.connect("mydatabase.db") as con:
				cur = con.cursor()
					# Check if the user already exists
				cur.execute("SELECT COUNT(*) FROM Ingredients WHERE Name = ?", (name,))
				exists = cur.fetchone()[0]
			if not exists:
				# insert the user data in the correct table
				cur.execute("INSERT INTO Ingredients (Name, Allegery_Category, Category) VALUES (?,?,?)" (
				    name, allergy, category,))

				con.commit()  # commit changes
		except:
			con.rollback()
			return render_template('pantry.html')
		finally:
			con.close()  # close connection
	return render_template("pantry.html")

@app.route('/add_ingredient_pantry', methods=['POST', 'GET'])
def add_ingredient_pantry():
	if request.method == 'POST':
		try:
			name = request.form['name']
			username = session['username']

			cur.execute("SELECT COUNT(*) FROM Ingredients WHERE Name = ?", (name,))
			exists = cur.fetchone()[0]
			if exists:
				cur.execute(
				    "SELECT COUNT(*) FROM Pantry WHERE Username = %s AND Ingredient = %s", (username, name))
				in_pantry = cur.fetchone()[0]
				if not in_pantry:
					cur.execute(
					    "INSERT INTO Pantry (Username, Ingredient_Name) VALUES (%s, %s)", (username, name))
					con.commit()
				else:
					print("Ingredient is already in pantry.")
			else:
				print("Ingredient does not exist.")
		except:
			con.rollback()
			return render_template('pantry.html')
		finally:
			con.close()	#close connection
	return render_template("pantry.html")

if __name__ == '__main__':
	app.run(debug=True)
