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

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(recipes)
app.register_blueprint(ingredients)
app.register_blueprint(pantry)

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
    return render_template('recipespage.html')


if __name__ == '__main__':
    app.run(debug=True)
