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
        name = session['firstName']
        all_ingredients = ['Flour', 'Sugar', 'Eggs', 'Milk', 'Butter']
        user_ingredients = ['Flour', 'Eggs']
        return render_template('test_pantry.html', name=name, all_ingredients=all_ingredients, user_ingredients=user_ingredients)

    message = ''
    return render_template('register.html', message='Please sign in.')


@pantry.route('/update_pantry', methods=['GET', 'POST'])
def update_pantry():
    try:
        user_ingredients = []
        cur.execute("SELECT Ingredient FROM User_Pantry WHERE Username = ?", (session[username],))
        user_ingredients = cur.fetchall()
        user_ingredients = [ingredient[0] for ingredient in user_ingredients]

        params = "RI.Ingredient = '" #string
        for i in ingredient_list:
            params += ingredient_list[i] + "'"
            if i < len(ingredient_list) - 1: #add except for when it's the last ingredient
                params += "OR RI.Ingredient = "

    cur.execute("SELECT R.Recipe_ID FROM Recipes R INNER JOIN Recipe_Ingredients RI ON R.Recipe_ID=RI.Recipe_ID WHERE %s", (params) #idk if we need recipe_id    
    possible_recipes = cur.fetchall()    
    missing_ingredients_per_recipe = []
    
            for recipe_id in possible_recipes:
            recipe_ingredients = []
            cur.execute("SELECT Ingredient FROM Recipe_Ingredients WHERE Recipe_ID = ?", (recipe_ID,))
            recipe_ingredients = cur.fetchall()
            recipe_ingredients = [ingredient[0] for ingredient in recipe_ingredients]
            missing_ingredients = []
            for ingredient in recipe_ingredients:
                if ingredient not in user_ingredients:
                    missing_ingredients.append(ingredient)
            if missing_ingredients:
                missing_ingredients_per_recipe.append((recipe_id, missing_ingredients))


    #show the possible_recipes
    """
    Final SQL string should look similar to this:
    SELECT R.Recipe_ID FROM Recipes R INNER JOIN Recipe_Ingredients RI ON R.Recipe_ID=RI.Recipe_ID WHERE RI.Ingredient = 'milk' OR RI.Ingredient = 'egg' OR RI.Ingredient = 'bread';
    """


        categories = ['Carbs', 'Fruits', 'Vegetables', 'Grains',
                      'Meat', 'Seafood', 'Dairy & Eggs', 'Complementary', 'Misc']

        # Initialize dictionary to hold ingredients for each category
        categorized_ingredients = {category: [] for category in categories}

        # Fetch all ingredients and categorize them
        for category in categories:
            cur.execute(
                "SELECT * FROM Ingredients WHERE Category = %s", (category,))
            ingrs = cur.fetchall()
            categorized_ingredients[category] = ingrs

        if request.method == 'POST':
            selected_ingredients = request.form.getlist('selected_ingredients')

            # Add selected ingredients to user's pantry
            for ingredient in selected_ingredients:
                cur.execute(
                    "INSERT INTO Pantry (Username, Ingredient_Name) VALUES (%s, %s)", (username, ingredient))
                cnx.commit()

            # Remove ingredients not selected
            for ingredient in user_ingredients:
                if ingr[1] not in selected_ingredients:
                    cur.execute(
                        "DELETE FROM Pantry WHERE Username = %s AND Ingredient_Name = %s", (username, ingr[1]))
                    cnx.commit()

        # Render the template with categorized ingredients and user's ingredients
        return render_template('pantrypage.html', categorized_ingrs=categorized_ingrs, user_ingredients=user_ingredients, possible_recipes=possible_recipes, missing_ingredients_per_recipe=missing_ingredients_per_recipe)

    except Exception as e:
        cnx.rollback()
        print(f"Error: {e}")
        return redirect('/pantry')
