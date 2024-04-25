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

recipes = Blueprint('recipes', __name__, template_folder='templates')

def update_config():
    global config
    config = {
        'user': session['username'],
        'password': session['password'],
        'host': 'localhost',
        'database': 'mydatabase',
    }
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor(dictionary=True)

@recipes.route('/admin_panel/list_recipes',methods = ['POST', 'GET'])
def list_recipes_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        # try:

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("SELECT * FROM Recipes;")
        rows = cur.fetchall()

        ingredients = []
        for row in rows:
            cur.execute("SELECT * FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (row["Recipe_ID"],))
            vals = cur.fetchall()
            ingredients.append(vals)


        return render_template("admin_panel/list_recipes.html",rows = rows, ingredients=ingredients)
        # except:
        #     return render_template("admin_panel/list_recipes.html",rows = [])

    return render_template("register.html", message='Not authorized')

# ---

@recipes.route('/admin_panel/create_recipe')
def create_recipe_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("SELECT Name FROM Ingredients")
        ingredients = cur.fetchall()

        return render_template('admin_panel/recipe.html', ingredients=ingredients)

    message = ''
    return render_template('register.html', message='')


@recipes.route('/admin_panel/create_recipe_function', methods=['GET', 'POST'])
def create_recipe_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    if request.method == 'POST' and 'recipeTitle' in request.form:
        # print(request)
        recipeTitle = request.form['recipeTitle']
        description = request.form['description']
        cook_time = request.form['cook']
        prep_time = request.form['prepTime']
        instructions = request.form['instructions']

        ingredients = request.form.getlist('ingredients[]')
        measurements = request.form.getlist('measurements[]')

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES (%s, %s, %s, %s, %s, %s);", (recipeTitle, "Temp", description, prep_time, cook_time, instructions))
            cnx.commit()

            cur.execute("SELECT * FROM Recipes ORDER BY Recipe_ID DESC LIMIT 1;")
            row = cur.fetchone()
            recipe_id = row['Recipe_ID']

            for i in range( len(ingredients) ):
                    cur.execute(
                        'INSERT INTO Recipe_Ingredients VALUES (%s,%s, %s)', (recipe_id, ingredients[i], measurements[i]))
                    cnx.commit()


        except:
            # cnx.rollback()
            # return redirect('/admin_panel/create_recipe')
            cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES (%s, %s, %s, %s, %s, %s);", (recipeTitle, "Temp", description, prep_time, cook_time, instructions))
            cnx.commit()

            cur.execute("SELECT * FROM Recipes ORDER BY Recipe_ID DESC LIMIT 1;")
            row = cur.fetchone()
            recipe_id = row['Recipe_ID']

            for i in range( len(ingredients) ):
                    cur.execute(
                        'INSERT INTO Recipe_Ingredients VALUES (%s,%s, %s)', (recipe_id, ingredients[i], measurements[i]))
                    cnx.commit()

        return redirect('/admin_panel/list_recipes')

    msg = ''
    return render_template('login.html', message=msg)


@recipes.route('/admin_panel/update_recipe_auto_page', methods=['GET', 'POST'])
def update_recipe_auto_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    if request.method == 'POST' and 'recipeTitle' in request.form:
        recipe_title = request.form['recipeTitle']
        description = request.form['description']
        cook_time = request.form['cook']
        prep_time = request.form['prepTime']
        instructions = request.form['instructions']

        recipe_id = request.form['recipeID']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (recipe_id,))
        ingredients = cur.fetchall()

        cur.execute("SELECT Name FROM Ingredients")
        all_ingredients = cur.fetchall()




        return render_template('/admin_panel/update_recipe_auto.html', recipe_title=recipe_title, desc=description, cook_time=cook_time, prep_time=prep_time, instr=instructions, recipe_id=recipe_id, ingredients=ingredients, all_ingredients=all_ingredients)
    else:
        # Return a response indicating that the request was not processed as expected
        return "Something went wrong", 400

@recipes.route('/admin_panel/update_recipe_auto_function', methods=['GET', 'POST'])
def update_recipe_auto_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    if request.method == 'POST' and 'recipeTitle' in request.form:
        recipe_title = request.form['recipeTitle']
        description = request.form['description']
        cook_time = request.form['cook']
        prep_time = request.form['prepTime']
        instructions = request.form['instructions']

        recipe_id = request.form['recipeID']

        ingredients = request.form.getlist('ingredients[]')
        measurements = request.form.getlist('measurements[]')

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        if description and cook_time and prep_time and instructions:
            try:
                cur.execute("UPDATE Recipes SET Name = %s, Description = %s, Cook_Time = %s, Prep_Time = %s, Instructions = %s WHERE Recipe_ID = %s;", (recipe_title, description, cook_time, prep_time, instructions, recipe_id))
                cnx.commit()

                cur.execute("DELETE FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (recipe_id,))
                cnx.commit()

                for i in range( len(ingredients) ):
                    cur.execute(
                        'INSERT INTO Recipe_Ingredients VALUES (%s,%s, %s)', (recipe_id, ingredients[i], measurements[i]))
                    cnx.commit()

                return redirect('/admin_panel/list_recipes')
            except:
                # cnx.rollback()
                # return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
                cur.execute("UPDATE Recipes SET Name = %s, Description = %s, Cook_Time = %s, Prep_Time = %s, Instructions = %s WHERE Recipe_ID = %s;", (recipe_title, description, cook_time, prep_time, instructions, recipe_id))
                cnx.commit()

                cur.execute("DELETE FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (recipe_id,))
                cnx.commit()

                for i in range( len(ingredients) ):
                    cur.execute(
                        'INSERT INTO Recipe_Ingredients VALUES (%s,%s, %s)', (recipe_id, ingredients[i], measurements[i]))
                    cnx.commit()

                return redirect('/admin_panel/list_recipes')
        else:
            pass


        return render_template('/admin_panel/update_recipe_auto.html', recipe_title=recipe_title, desc=description, cook_time=cook_time, prep_time=prep_time, instr=instructions)
    else:
        # Return a response indicating that the request was not processed as expected
        return "Something went wrong", 400
# ---

@recipes.route('/admin_panel/update_recipe')
def update_recipe_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return redirect( url_for('auth.list_recipes_page'))

    message = ''
    return render_template('register.html', message='')


@recipes.route('/admin_panel/delete_recipe')
def delete_recipe_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:
            # added after safe rbac branch
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Recipes;")
            rows = cur.fetchall()

            ingredients = []
            for row in rows:
                cur.execute("SELECT * FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (row["Recipe_ID"],))
                vals = cur.fetchall()
                ingredients.append(vals)


            return render_template("admin_panel/delete_recipe.html",rows = rows)
        except:
            return render_template("admin_panel/delete_recipe.html",rows = [])
    message = ''
    return render_template('register.html', message='')

@recipes.route('/admin_panel/delete_recipe_function', methods=['GET', 'POST'])
def delete_recipe_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'recipeID' in request.form:
        recipe_id = request.form['recipeID']

        try:
            # added after safe rbac branch
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            cur.execute("DELETE FROM Recipes WHERE Recipe_ID = %s;", (recipe_id,))
            cnx.commit() 

            cur.execute("SELECT * FROM Recipes;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_recipes.html",rows = rows, ingredients=[])
        except:
            return render_template("admin_panel/list_recipes.html",rows = [])

        return render_template('admin_panel/delete_ingredient.html', message = "Deleted {}".format(ingredient_name))


@recipes.route('/recipesinfo/<int:recipe_id>', methods=['GET', 'POST'])
def recipesinfo_page(recipe_id):
    update_config()
	try:
		cur = cnx.cursor(dictionary=True)
		if request.method == 'GET':
			#retrieves the recipe details
			cur.execute("SELECT * FROM Recipes WHERE Recipe_ID = %s", (recipe_id,))
			recipe = cur.fetchone()
			if recipe:

                # Fetch ingredients for the recipe
				cur.execute("SELECT ingredient, measurement FROM Ingredients WHERE Recipe_ID = %s", (recipe_id,))
				ingredients = cur.fetchall()

				instruction = recipe["Instructions"].split('\n')

				#steps = [step.strip() for step in steps if step.strip()]

                # Create a numbered list of steps
				num_inst = [f"{instruction}" for i, instruction in enumerate(instruction)]

				recipe["Instructions"] = num_inst



			return render_template('recipe_info.html',ingredients=ingredients , recipes=recipe)
	except:
		cnx.rollback()
		return render_template('recipes.html')

