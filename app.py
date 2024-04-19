from flask import Flask, render_template, redirect, url_for, request, session
# from flask_mysqldb import MySQL
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
        name = "{} {}, username: {}".format(
            session['firstName'], session['lastName'], session['username'])
        return render_template('home.html', username=name)
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

            try:
                cur.execute(
                    "SELECT First_Name, Last_Name FROM Users WHERE Username = %s", (session['username'],))
                row = cur.fetchone()
                session['firstName'] = row['First_Name']
                session['lastName'] = row['Last_Name']
            except:
                session['firstName'] = 'ERROR'
                session['lastName'] = 'ERROR'

            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password.'

    return render_template('login.html', message=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('firstName', None)
    session.pop('lastName', None)
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

                cur.execute('INSERT INTO Users VALUES (%s,%s,%s,%s)',
                            (username, password, first_name, last_name))
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


@app.route('/recipe_creation', methods=['POST', 'GET'])
def create_recipe():
	if request.method == 'POST':
		try:  # get the user data from the form
			name = request.form['recipe_name']
			ID = request.form['recipe_ID']
			category = request.form['recipe_category']
			instructions = request.form['recipe_instructions']
			with sql.connect("mydatabase.db") as con:
				cur = con.cursor()
					# Check if the recipe already exists
				cur.execute("SELECT COUNT(*) FROM Recipes WHERE Recipe_ID = ?", (ID,))
				exists = cur.fetchone()[0]
			if not exists:
				# insert the user data in the correct table
				cur.execute("INSERT INTO Recipes (Recipe_ID, Name, Category, Instructions) VALUES (?,?,?,?)" (
				    ID, name, category, instructions,))

				con.commit()  # commit changes
		except:
			con.rollback()
			return render_template('newRecipe.html')
		finally:
			con.close()  # close connection
	return render_template("recipes.html")


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
	
@app.route('/add_ingredient_recipe', methods=['POST', 'GET'])
def add_ingredient_recipe():
	if request.method == 'POST':
		try:
			i_name = request.form['name']
			r_ID = request.form['recipe_ID']

			cur.execute("SELECT COUNT(*) FROM Ingredients WHERE Name = ?", (name,))
			i_exists = cur.fetchone()[0]
			if i_exists:
				cur.execute("SELECT COUNT(*) FROM Recipes WHERE Recipe_ID = ?", (r_ID,))
				r_exists = cur.fetchone()[0]
				if r_exists:
					cur.execute("SELECT COUNT(*) FROM Recipes WHERE Recipe_ID = %s AND Name = %s", (recipe_name, ingredient_name))
					in_recipe = cur.fetchone()[0]
					if not in_recipe:
						cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient) VALUES (%s, %s)", (recipe_ID, i_name))
						con.commit()
					else:
						print("Ingredient already in recipe.")
				else:
					print("Recipe does not exist.")
			else:
				print("Ingredient does not exist.")
		except:
			con.rollback()
			return render_template('recipes.html')
		finally:
			con.close()	#close connection
	return render_template("recipes.html")

if __name__ == '__main__':
	app.run(debug=True)
