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
    try:
        if request.method == 'GET':
            # retrieves the ingredients in a list according to category
            categories = ['Carbs', 'Fruits', 'Vegetables', 'Grains',
                          'Meat', 'Seafood', 'Dairy & Eggs', 'Complementary', 'Misc']
            all_ingrs = []
            user_ingrs = []

            for category in categories:
                cur.execute(
                    "SELECT * FROM Ingredients WHERE Category = %s", (category))
                ingrs = cur.fetchall()
                all_ingrs += ingrs

            cur.execute(
                "SELECT * FROM Pantry WHERE Username = %s", (username,))
            user_ingrs = cur.fetchall()

            return render_template('pantry.html', all_ingrs=all_ingrs, user_ingrs=user_ingrs)
        elif request.method == 'POST':
            username = session['username']
            selected_ingredients = request.form.getlist('selected_ingredients')

            for ingredient in selected_ingredients:
                cur.execute(
                    "SELECT COUNT(*) FROM Pantry WHERE Username = %s AND Ingredient = %s", (username, ingredient))
                in_pantry = cur.fetchone()[0]
                if not in_pantry:
                    cur.execute(
                        "INSERT INTO Pantry (Username, Ingredient_Name) VALUES (%s, %s)", (username, ingredient))
                    cnx.commit()

            cur.execute(
                "SELECT * FROM Pantry WHERE Username = %s", (username,))
            user_ingrs = cur.fetchall()

            for ingr in user_ingrs:
                if ingr[1] not in selected_ingredients:
                    cur.execute(
                        "DELETE FROM Pantry WHERE Username = %s AND Ingredient_Name = %s", (username, ingr[1]))
                    cnx.commit()

    except:
        cnx.rollback()
        return redirect('/pantry')
    return redirect('/pantry')
