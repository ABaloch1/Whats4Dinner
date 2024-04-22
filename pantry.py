from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
from flask_mysqldb import MySQL
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

pantry = Blueprint('pantry', __name__, template_folder='templates')


@pantry.route('/pantry')
def pantry_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        name = session['firstName']
        all_ingredients = ['Flour', 'Sugar', 'Eggs', 'Milk', 'Butter']
        user_ingredients = ['Flour', 'Eggs']
        return render_template('test_pantry.html', name=name, all_ingredients=all_ingredients, user_ingredients=user_ingredients)

    message = ''
    return render_template('register.html', message='Please sign in.')


@pantry.route('/update_pantry', methods=['POST'])
def update_pantry():
    # Get the list of selected ingredients from the form
    user_ingredients = request.form.getlist('ingredients')
    return redirect('/pantry')
