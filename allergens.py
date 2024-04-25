from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
import mysql.connector
import hashlib

secret_key = 'this is our top secret super key that definitely isn\'t going to be uploaded to our GitHub page'

config = {
    'user': 'group20',
    'password': 'group20',
    'host': 'localhost',
    'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()

allergens = Blueprint('allergens', __name__, template_folder='templates')

def update_config():
    global config
    config = {
        'user': session['username'],
        'password': session['password'],
        'host': 'localhost',
        'database': 'mydatabase',
    }
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor()

# ---

@allergens.route('/admin_panel/create_allergen')
def create_allergens_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/create_allergen.html')

    message = ''
    return render_template('register.html', message='')

# ---

@allergens.route('/admin_panel/create_allergen_function', methods=['GET', 'POST'])
def create_allergen_function():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'allergenName' in request.form:
        allergen_name = request.form['allergenName']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("INSERT INTO Allergens (Name) VALUES (%s);", (allergen_name,))
            cnx.commit()        
        except:
            cnx.rollback()
            return render_template('admin_panel/create_allergen.html', message = "Duplicate entry.")


        return render_template('/admin_panel/create_allergen.html', message = "Created {}".format(allergen_name))

    return render_template('login.html', message=msg)

# ---

@allergens.route('/admin_panel/delete_allergen')
def delete_allergens_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_allergen.html')

    message = ''
    return render_template('register.html', message='')

# ---

@allergens.route('/admin_panel/delete_allergen_function', methods=['GET', 'POST'])
def delete_allergens_function():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'allergenName' in request.form:
        allergen_name = request.form['allergenName']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("DELETE FROM Allergens WHERE Name = %s;", (allergen_name,))
            cnx.commit() 
        except:
            cnx.rollback()
            return render_template('admin_panel/delete_allergen.html', message = "Error. Had to roll back.")

        return render_template('admin_panel/delete_allergen.html', message = "Deleted {}".format(allergen_name))

    return render_template('login.html', message=msg)

# ---

@allergens.route('/admin_panel/list_allergens',methods = ['POST', 'GET'])
def list_allergens_page():
    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:

            # added after safe rbac branch
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Allergens;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_allergens.html",rows = rows)
        except:
            return render_template("admin_panel/list_allergens.html",rows = [])
    return render_template("register.html", message='Not authorized')
