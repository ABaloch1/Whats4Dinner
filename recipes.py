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
	cur = cnx.cursor()

@recipes.route('/recipe_creation', methods=['POST', 'GET'])
def create_recipe():
	update_config()
	if request.method == 'POST':
		try:	#get the user data from the form
			name = request.form['recipe_name']
			ID = request.form['recipe_ID']
			category = request.form['recipe_category']
			instructions = request.form['recipe_instructions']
			description = request.form['recipe_description']
			prep_time = request.form['prep_time']
			cook_time = request.form['cook_time']
			
			#check if the recipe already exists
			cur.execute("SELECT COUNT(*) FROM Recipes WHERE Recipe_ID = ?", (ID,))
			exists = cur.fetchone()[0]
			if not exists:
				#insert the user data in the correct table
				cur.execute("INSERT INTO Recipes (Recipe_ID, Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES (?,?,?,?,?,?,?)", (ID, name, category, description, prep_time, cook_time, instructions))
        
				cnx.commit() #commit changes
		except:
			cnx.rollback()
			return render_template('newRecipe.html')
	return render_template("recipes.html")
   	
@recipes.route('/list_recipes')
def list_recipes():
	update_config()
	cur.execute("SELECT * FROM Recipes")
	recipes = cur.fetchall()[0]
	return render_template('recipes.html', recipes=recipes)

@recipes.route('/recipesinfo/<int:recipe_id>', methods=['GET', 'POST'])
def recipesinfo_page(recipe_id):
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

@recipes.route('/add_ingredient_recipe', methods=['POST', 'GET'])
def add_ingredient_recipe():
	update_config()
	if request.method == 'POST':
		try:
			i_name = request.form['name']
			r_ID = request.form['recipe_ID']
			amount = request.form['amount']

			cur.execute("SELECT COUNT(*) FROM Ingredients WHERE Name = ?", (name,))
			i_exists = cur.fetchone()[0]
			if i_exists:
				cur.execute("SELECT COUNT(*) FROM Recipes WHERE Recipe_ID = ?", (r_ID,))
				r_exists = cur.fetchone()[0]
			if r_exists:
				cur.execute("SELECT COUNT(*) FROM Recipes WHERE Recipe_ID = %s AND Name = %s", (recipe_name, ingredient_name))
				in_recipe = cur.fetchone()[0]
				if not in_recipe:
					cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient, Amount) VALUES (%s, %s)", (recipe_ID, i_name, amount))
					cnx.commit()
		except:
			cnx.rollback()
			return render_template('recipes.html')
	return render_template("recipes.html")
    
@recipes.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
	update_config()
	if request.method == 'POST':
		#deletes the recipe
		cursor.execute("DELETE FROM Recipes WHERE Recipe_ID = %s", (recipe_id,))
		cnx.commit()
		return render_template('recipes.html')
		
@recipes.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
	update_config()
	try:
		if request.method == 'GET':
			#retrieves the recipe details
			cur.execute("SELECT * FROM Recipes WHERE Recipe_ID = %s", (recipe_id,))
			recipe = cur.fetchone()[0]
			if recipe:
				return render_template('edit_recipe.html', recipe=recipe)
		elif request.method == 'POST':
			name = request.form['name']
			category = request.form['category']
			description = request.form['description']
			prep_time = request.form['prep_time']
			cook_time = request.form['cook_time']
			instructions = request.form['instructions']
		
			#updates the recipe in the database
			cur.execute("UPDATE Recipes SET Name = %s, Category = %s, Description = %s, Prep_Time = %s, Cook_Time = %s, Instructions = %s WHERE Recipe_ID = %s", (name, category, description, prep_time, cook_time, instructions, recipe_id))
			cnx.commit()
	except:
		cnx.rollback()
		return render_template('recipes.html')
	return render_template('edit_recipe.html', recipe=recipe)
