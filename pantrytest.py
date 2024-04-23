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
            return render_template('pantrypage.html')
    return render_template("pantrypage.html")



@pantry.route('/update_pantry', methods=['GET', 'POST'])
def update_pantry():
    try:
        categories = ['Carbs', 'Fruits', 'Vegetables', 'Grains',
                      'Meat', 'Seafood', 'Dairy & Eggs', 'Complementary', 'Misc']

        # Initialize dictionary to hold ingredients for each category
        categorized_ingrs = {category: [] for category in categories}

        # Fetch all ingredients and categorize them
        for category in categories:
            cur.execute(
                "SELECT * FROM Ingredients WHERE Category = %s", (category,))
            ingrs = cur.fetchall()
            categorized_ingrs[category] = ingrs

        # Fetch user's ingredients
        username = session['username']
        cur.execute(
            "SELECT * FROM Pantry WHERE Username = %s", (username,))
        user_ingrs = cur.fetchall()

        if request.method == 'POST':
            selected_ingredients = request.form.getlist('selected_ingredients')

            # Add selected ingredients to user's pantry
            for ingredient in selected_ingredients:
                cur.execute(
                    "INSERT INTO Pantry (Username, Ingredient_Name) VALUES (%s, %s)", (username, ingredient))
                cnx.commit()

            # Remove ingredients not selected
            for ingr in user_ingrs:
                if ingr[1] not in selected_ingredients:
                    cur.execute(
                        "DELETE FROM Pantry WHERE Username = %s AND Ingredient_Name = %s", (username, ingr[1]))
                    cnx.commit()

        # Render the template with categorized ingredients and user's ingredients
        return render_template('pantrypage.html', categorized_ingrs=categorized_ingrs, user_ingrs=user_ingrs)

    except Exception as e:
        cnx.rollback()
        print(f"Error: {e}")
        return redirect('/pantry')

