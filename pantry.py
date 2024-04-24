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

pantry = Blueprint('pantry', __name__, template_folder='templates')


@pantry.route('/pantry')
def pantry_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return redirect( '/update_pantry' )
    else:
        message = ''
        return render_template('register.html', message='Please sign in.')


@pantry.route('/update_pantry', methods=['GET', 'POST'])
def update_pantry():
    try:
        config = {
            'user': session['username'],
            'password': session['password'],
            'host': 'localhost',
            'database': 'mydatabase',
        }
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        if request.method == 'POST':
            user_ingredients = []
            cur.execute("SELECT Ingredient FROM User_Pantry WHERE Username = %s", (session['username'],))
            user_ingredients = cur.fetchall()
            user_ingredients = [ingredient[0] for ingredient in user_ingredients]
            
            params = "RI.Ingredient = '" #string
            for i, ingredient in enumerate(user_ingredients):
                params += ingredient + "'"
                if i < len(user_ingredients) - 1: #add except for when it's the last ingredient
                    params += "OR RI.Ingredient = "
            
            cur.execute("SELECT R.Recipe_ID FROM Recipes R INNER JOIN Recipe_Ingredients RI ON R.Recipe_ID=RI.Recipe_ID WHERE %s", (params,))
            possible_recipes = cur.fetchall()    
            missing_ingredients_per_recipe = []
            
            for recipe_id in possible_recipes:
                recipe_ingredients = []
                cur.execute("SELECT Ingredient FROM Recipe_Ingredients WHERE Recipe_ID = %s", (recipe_id,))
                recipe_ingredients = cur.fetchall()
                recipe_ingredients = [ingredient[0] for ingredient in recipe_ingredients]
                missing_ingredients = []
            
            for ingredient in recipe_ingredients:
                if ingredient not in user_ingredients:
                    missing_ingredients.append(ingredient)
            if missing_ingredients:
                missing_ingredients_per_recipe.append((recipe_id, missing_ingredients))
                
            categories = ['Carbs', 'Fruits', 'Vegetables', 'Grains', 'Meat', 'Seafood', 'Dairy & Eggs', 'Complementary', 'Misc']
        
            # Initialize dictionary to hold ingredients for each category
            categorized_ingredients = {category: [] for category in categories}

            # Fetch all ingredients and categorize them
            for category in categories:
                cur.execute(
                    "SELECT * FROM Ingredients WHERE Category = %s", (category,))
                ingredients = [ingredient[0] for ingredient in cur.fetchall()]
                categorized_ingredients[category] = ingredients
                print(ingredients)

        if request.method == 'POST':
            selected_ingredients = request.form.getlist('selected_ingredients')

            # Add selected ingredients to user's pantry
            for ingredient in selected_ingredients:
                cur.execute(
                    "INSERT INTO User_Pantry (Username, Ingredient_Name) VALUES (%s, %s)", (username, ingredient))
                cnx.commit()

            # Remove ingredients not selected
            for ingredient in user_ingredients:
                if ingredient[0] not in selected_ingredients:
                    cur.execute(
                        "DELETE FROM User_Pantry WHERE Username = %s AND Ingredient_Name = %s", (username, ingr[0]))
                    cnx.commit()

        # Render the template with categorized ingredients and user's ingredients
        return render_template('pantrypage.html', name=session['firstName'], categorized_ingredients=categorized_ingredients, user_ingredients=user_ingredients, possible_recipes=possible_recipes, missing_ingredients_per_recipe=missing_ingredients_per_recipe)

    except Exception as e:
        cnx.rollback()
        # print(f"Error: {e}")
        # return redirect('/pantry')
        return f"Error: {e}"
