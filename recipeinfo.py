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

recipesinfo = Blueprint('recipesinfo', __name__, template_folder='templates')

@recipesinfo.route('/recipesinfo/<int:recipe_id>', methods=['GET', 'POST'])
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
				num_inst = [f"{i+1}. {instruction}" for i, instruction in enumerate(instruction)]

				recipe["Instructions"] = num_inst



			return render_template('recipe_info.html',ingredients=ingredients , recipes=recipe)
	except:
		cnx.rollback()
		return render_template('recipes.html')


		
