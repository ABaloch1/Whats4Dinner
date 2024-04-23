from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
# from flask_mysqldb import MySQL
import mysql.connector
import hashlib

# import MySQLdb.cursors
# import MySQLdb.cursors, re, hashlib

from auth import auth
from recipes import recipes
from ingredients import ingredients
from pantry import pantry
from user import user

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(recipes)
app.register_blueprint(ingredients)
app.register_blueprint(pantry)
app.register_blueprint(user)

# ---

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

@app.route('/show_recipes')
def guest_page():
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT * FROM Recipes;")
    recipes = cur.fetchall()
    return render_template('recipespage.html', recipes=recipes)

@app.route('/info_recipe', methods=['GET', 'POST'])
def info_recipe():
    if request.method == 'POST' and 'recipeID' in request.form:
        recipeId =  request.form["recipeID"]
        recipeTitle= request.form["recipeTitle"]
        description= request.form["description"]
        cook_time= request.form["cook"]
        prep_time= request.form["prepTime"]
        


        # instructions= request.form["instructions"]
        instruction = request.form["instructions"].split('\n')

        #steps = [step.strip() for step in steps if step.strip()]

        # Create a numbered list of steps
        instruction = [f"{instruction}" for i, instruction in enumerate(instruction)]

        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT Ingredient, Amount FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (recipeId,))
        ingredients = cur.fetchall()
        return render_template('recipeinfo.html', recipeTitle=recipeTitle,description=description,cook_time=cook_time,prep_time=prep_time,instructions=instruction,ingredients=ingredients)


if __name__ == '__main__':
    app.run(debug=True)
