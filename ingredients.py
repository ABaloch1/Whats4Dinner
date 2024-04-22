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


@ingredients.route('/ingredient_creation', methods=['POST', 'GET'])
def create_ingredient():
    if request.method == 'POST':
        try:  # get the ingr data from the form
            name = request.form['name']
            allergy = request.form['allergy']
            category = request.form['category']

            # Check if the ingr already exists
            cur.execute(
                "SELECT COUNT(*) FROM Ingredients WHERE Name = ?", (name,))
            exists = cur.fetchone()[0]
            if not exists:
                # insert the data in the correct table
                cur.execute(
                    "INSERT INTO Ingredients (Name, Allergy_Category, Category) VALUES (?,?,?)", (name, allergy, category))

                cnx.commit()  # commit changes
        except:
            cnx.rollback()
            return render_template('pantry.html')
    return render_template("pantry.html")


@ingredients.route('/delete_ingr/<string:name>', methods=['POST', 'GET'])
def delete_ingredient(name):
    if request.method == 'POST':
        # deletes the ingr
        cursor.execute("DELETE FROM Ingredients WHERE Name = %s", (name,))
        cnx.commit()
    return render_template('admin.html')

@ingredients.route('/edit_ingr/<string:name>', methods=['GET', 'POST'])
def edit_recipe(name):
    try:
        if request.method == 'GET':
            # retrieves the ingr details
            cur.execute("SELECT * FROM Ingredients WHERE Name = %s", (name,))
            ingr = cur.fetchone()[0]
            if recipe:
                return render_template('edit_recipe.html', ingr=ingr)
        elif request.method == 'POST':
            name = request.form['name']
            allergy = request.form['allergy']
            category = request.form['category']

            # updates the ingr in the database
            cur.execute(
                "UPDATE Ingredients SET Name = %s, Allergy_Category = %s, Category = %s,", (name, allergy, category))
            cnx.commit()
    except:
        cnx.rollback()
        return render_template('edit_ingr.html')
    return render_template('admin.html', name=name)
