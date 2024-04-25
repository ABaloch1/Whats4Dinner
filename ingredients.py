from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
#from flask_mysqldb import MySQL
import mysql.connector

secret_key = 'this is our top secret super key that definently isnt going to also be uploaded on our github page'

config = {
    'user': 'group20',
    'password': 'group20',
    'host': 'localhost',
    'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()

ingredients = Blueprint('ingredients', __name__, template_folder='templates')

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

@ingredients.route('/admin_panel/create_ingredient')
def create_ingredient_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/create_ingredient.html')

    message = ''
    return render_template('register.html', message='')

# ---

@ingredients.route('/admin_panel/create_ingredient_function', methods=['GET', 'POST'])
def create_ingredient_function():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        category = request.form['category']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        # try:
        cur.execute("INSERT INTO Ingredients (Name, Allergy_Category, Category) VALUES (%s, %s, %s);", (ingredient_name, allergy_category, category))
        cnx.commit()        
        # except:
        #     cnx.rollback()
        #     return render_template('admin_panel/create_ingredient.html', message = "Duplicate entry.")

        return render_template('/admin_panel/create_ingredient.html', message = "Added {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---

@ingredients.route('/admin_panel/update_ingredient')
def update_ingredient_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_ingredient.html')

    message = ''
    return render_template('register.html', message='')
    
# ---

@ingredients.route('/admin_panel/update_ingredient_function', methods=['GET', 'POST'])
def update_ingredient_function():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        category = request.form['category']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        if allergy_category:
            try:
                cur.execute("UPDATE Ingredients SET Allergy_Category = %s WHERE Name = %s;", (allergy_category, ingredient_name,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass

        if category:
            try:
                cur.execute("UPDATE Ingredients SET Category = %s WHERE Name = %s;", (category, ingredient_name,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass



        return render_template('admin_panel/update_ingredient.html', message = "Updated {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---

@ingredients.route('/admin_panel/list_ingredients',methods = ['POST', 'GET'])
def list_ingredients_page():
    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        # try:

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("SELECT * FROM Ingredients;")
        rows = cur.fetchall()

        return render_template("admin_panel/list_ingredients.html",rows = rows)
        # except:
        #     return render_template("admin_panel/list_ingredients.html",rows = [])
    return render_template("register.html", message='Not authorized')

# ---

@ingredients.route('/admin_panel/delete_ingredients')
def delete_ingredients_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_ingredient.html')

    message = ''
    return render_template('register.html', message='')

# ---

@ingredients.route('/admin_panel/delete_ingredient_function', methods=['GET', 'POST'])
def delete_ingredient_function():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("DELETE FROM Ingredients WHERE Name = %s;", (ingredient_name,))
            cnx.commit() 
        except:
            cnx.rollback()
            return render_template('admin_panel/delete_ingredient.html', message = "Error. Had to roll back.")

        return render_template('admin_panel/delete_ingredient.html', message = "Deleted {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---
