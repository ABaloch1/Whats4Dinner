app.py                                                                                              0000664 0001750 0001750 00000005351 14612341050 011156  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
# from flask_mysqldb import MySQL
import mysql.connector
import hashlib

# import MySQLdb.cursors
# import MySQLdb.cursors, re, hashlib

from auth import auth
from user import user
from pantry import pantry
from recipes import recipes
from allergens import allergens
from ownerpanel import ownerpanel
from ingredients import ingredients

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(pantry)
app.register_blueprint(recipes)
app.register_blueprint(allergens)
app.register_blueprint(ownerpanel)
app.register_blueprint(ingredients)

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
    cur = cnx.cursor(dictionary=True)
    cur.execute("SELECT * FROM Recipes;")
    recipes = cur.fetchall()
    return render_template('recipespage.html', recipes=recipes)

@app.route('/info_recipe', methods=['GET', 'POST'])
def info_recipe():
    if request.method == 'POST' and 'recipeID' in request.form:
        recipeId =  request.form["recipeID"]
        recipeTitle= request.form["recipeTitle"]
        description= request.form["description"]
        cook_time= request.form["cook"]
        prep_time= request.form["prepTime"]
        


        # instructions= request.form["instructions"]
        instruction = request.form["instructions"].split('\n')

        #steps = [step.strip() for step in steps if step.strip()]

        # Create a numbered list of steps
        instruction = [f"{instruction}" for i, instruction in enumerate(instruction)]

        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT Ingredient, Amount FROM Recipe_Ingredients WHERE Recipe_ID = %s;", (recipeId,))
        ingredients = cur.fetchall()
        return render_template('recipeinfo.html', recipeTitle=recipeTitle,description=description,cook_time=cook_time,prep_time=prep_time,instructions=instruction,ingredients=ingredients)


if __name__ == '__main__':
    app.run(debug=True)
                                                                                                                                                                                                                                                                                       auth.py                                                                                             0000664 0001750 0001750 00000017572 14612344660 011361  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
import mysql.connector
import hashlib


secret_key = 'this is our top secret super key that definently isnt going to also be uploaded on our github page'
#global config
config = {
    'user': 'group20',
    'password': 'group20',
    'host': 'localhost',
    'database': 'mydatabase',
}
#add when we have time to fix bugs 
#cnx = mysql.connector.connect(**config) 
auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/home')
def home():
    if 'loggedin' in session:
        name = "{} {}, username: {}".format(
            session['firstName'], session['lastName'], session['username'])
        return render_template('home.html', username=name)
    return render_template('login.html', message="Please log in first") #redirect(url_for('login'))


@auth.route('/login_page')
def login_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])

    message = ''
    return render_template('login.html', message='')


@auth.route('/login/', methods=['GET', 'POST'])
def login():

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        hashed_password = password + secret_key
        hashed_password = hashlib.sha256(hashed_password.encode())

        password = hashed_password.hexdigest()

        # this uses global guest permissions
        global config
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password,))

        account = cur.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['Username']
            session['password'] = password
            # update connection to use user credentials
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)
            cur.execute(
                "SELECT First_Name, Last_Name FROM Users WHERE Username = %s", (session['username'],))
            row = cur.fetchone()
            session['firstName'] = row['First_Name']
            session['lastName'] = row['Last_Name']
            cur.close()
            cnx.close()

            config = {
                'user': 'root',
                'password': 'root1',
                'host': 'localhost',
                'database': 'mydatabase',
            }
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True, buffered=True)

            cur.execute("SELECT FROM_USER FROM mysql.role_edges WHERE TO_USER = %s", (session['username'],))
            role = cur.fetchone()
            session['role'] = role['FROM_USER']
            print(session['role'])
            cur.close()
            cnx.close()

            config = {
                'user': session['username'],
                'password': session['password'],
                'host': 'localhost',
                'database': 'mydatabase',
            }
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            return redirect(url_for('auth.home'))
        else:
            msg = 'Incorrect username/password.'

    return render_template('login.html', message=msg)


@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('firstName', None)
    session.pop('lastName', None)
    session.pop('password', None)
    session.pop('role', None)
    global config
    config = {
        'user': 'group20',
        'password': 'group20',
        'host': 'localhost',
        'database': 'mydatabase',
    }
    session['username'] = "group20"
    session['password'] = "group20"
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor(dictionary=True)
    return render_template('login.html') #redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        global config
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT * FROM Users WHERE Username = %s', (username,))
        account = cur.fetchone()

        if account:
            msg = 'Username is already taken.'
        elif not username or not password:
            msg = 'Please complete the form.'
        else:
            hashed_password = password + secret_key
            hashed_password = hashlib.sha256(hashed_password.encode())

            password = hashed_password.hexdigest()

            #try:
            first_name = request.form['firstName']
            last_name = request.form['lastName']

            cur.execute('INSERT INTO Users VALUES (%s,%s,%s,%s)',
                        (username, password, first_name, last_name))
            cnx.commit()

            # --
            checked_allergies = request.form.getlist('allergies')
            for allergy in checked_allergies:
                cur.execute(
                    'INSERT INTO User_Allergens VALUES (%s,%s)', (username, allergy))
                cnx.commit()
            # --

            cur.close()
            cnx.close()

            #global config
            config = {
                'user': 'root',
                'password': 'root1',
                'host': 'localhost',
                'database': 'mydatabase',
            }
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)
            cur.execute("CREATE USER %s@'localhost' IDENTIFIED WITH mysql_native_password BY %s", (username, password))
            #cur.execute("GRANT CONNECT ON mydatabase.* TO %s@'localhost'", (username,))
            cnx.commit()
            cur.execute("GRANT 'member' TO %s@'localhost'", (username,))
            cur.execute("SET DEFAULT ROLE 'member' TO %s@'localhost'", (username,))
            cur.execute("flush privileges")
            cnx.commit()

            cur.close()
            cnx.close()

            config = {
                'user': 'group20',
                'password': 'group20',
                'host': 'localhost',
                'database': 'mydatabase',
            }
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            msg = 'Success! Account registered!'
            return render_template('login.html', message=msg) #redirect(url_for('auth.login'))
            # except:
            #     cnx.rollback()
            #     msg = 'Something happenend. Database rolling back.'
            
            # --

            # msg = 'Success! Account registered!'
            # return redirect(url_for('auth.home'))

    elif request.method == 'POST':
        msg = 'Incomplete form'
    return render_template('register.html', message=msg)

@auth.route('/register_page')
def register_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])

    message = ''
    return render_template('register.html', message='')


# --- Admin Functionality

@auth.route('/admin_panel/')
def admin_panel_page():

    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    if 'loggedin' in session:
        owner = False
        if session['role'] == 'owner':
            owner = True
        return render_template('admin_panel/adminpanel.html', owner=owner)

    message = ''
    return render_template('register.html', message='')

# ---
                                                                                                                                      ingredients.py                                                                                      0000664 0001750 0001750 00000015606 14612344660 012727  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
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

# ---

@ingredients.route('/admin_panel/create_ingredient')
def create_ingredient_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/create_ingredient.html')

    message = ''
    return render_template('register.html', message='')

# ---

@ingredients.route('/admin_panel/create_ingredient_function', methods=['GET', 'POST'])
def create_ingredient_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        category = request.form['category']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        # try:
        cur.execute("INSERT INTO Ingredients (Name, Allergy_Category, Category) VALUES (%s, %s, %s);", (ingredient_name, allergy_category, category))
        cnx.commit()        
        # except:
        #     cnx.rollback()
        #     return render_template('admin_panel/create_ingredient.html', message = "Duplicate entry.")

        return render_template('/admin_panel/create_ingredient.html', message = "Added {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---

@ingredients.route('/admin_panel/update_ingredient')
def update_ingredient_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_ingredient.html')

    message = ''
    return render_template('register.html', message='')
    
# ---

@ingredients.route('/admin_panel/update_ingredient_function', methods=['GET', 'POST'])
def update_ingredient_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        category = request.form['category']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        if allergy_category:
            try:
                cur.execute("UPDATE Ingredients SET Allergy_Category = %s WHERE Name = %s;", (allergy_category, ingredient_name,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass

        if category:
            try:
                cur.execute("UPDATE Ingredients SET Category = %s WHERE Name = %s;", (category, ingredient_name,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass



        return render_template('admin_panel/update_ingredient.html', message = "Updated {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---

@ingredients.route('/admin_panel/list_ingredients',methods = ['POST', 'GET'])
def list_ingredients_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        # try:

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("SELECT * FROM Ingredients;")
        rows = cur.fetchall()

        return render_template("admin_panel/list_ingredients.html",rows = rows)
        # except:
        #     return render_template("admin_panel/list_ingredients.html",rows = [])
    return render_template("register.html", message='Not authorized')

# ---

@ingredients.route('/admin_panel/delete_ingredients')
def delete_ingredients_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_ingredient.html')

    message = ''
    return render_template('register.html', message='')

# ---

@ingredients.route('/admin_panel/delete_ingredient_function', methods=['GET', 'POST'])
def delete_ingredient_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']

        # added after safe rbac branch
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("DELETE FROM Ingredients WHERE Name = %s;", (ingredient_name,))
            cnx.commit() 
        except:
            cnx.rollback()
            return render_template('admin_panel/delete_ingredient.html', message = "Error. Had to roll back.")

        return render_template('admin_panel/delete_ingredient.html', message = "Deleted {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---
                                                                                                                          ownerpanel.py                                                                                       0000664 0001750 0001750 00000005170 14612344660 012561  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
import mysql.connector
import hashlib


secret_key = 'this is our top secret super key that definently isnt going to also be uploaded on our github page'


ownerpanel = Blueprint('ownerpanel', __name__, template_folder='templates')

config = {
    'user': 'group20',
    'password': 'group20',
    'host': 'localhost',
    'database': 'mydatabase',
}

def update_config():
    global config
    config = {
        'user': session['username'],
        'password': session['password'],
        'host': 'localhost',
        'database': 'mydatabase',
    }
    global cur
    global cnx
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor(dictionary=True)

@ownerpanel.route('/owner/update_admin_page')
def update_admin_page():
    update_config()
    if session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. Not Owner. You must be a Eugene imposter')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('owner_update_admin.html')


@ownerpanel.route('/owner/grant_admin', methods=['GET', 'POST'])
def grant_admin():
    update_config()
    if session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. Not Owner. You must be a Eugene imposter')

    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']

        global config
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("GRANT 'admin' TO %s@'localhost';", (username,))
        cnx.commit() 

        cur.execute("FLUSH PRIVILEGES;")
        cnx.commit()

        return render_template('owner_update_admin.html', message="Granted Admin to {}".format(username))

    return render_template('/')


@ownerpanel.route('/owner/revoke_admin', methods=['GET', 'POST'])
def revoke_admin():
    update_config()
    if session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. Not Owner. You must be a Eugene imposter')
    
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']

        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("REVOKE 'admin' FROM %s@'localhost';", (username,))
        cnx.commit() 

        cur.execute("FLUSH PRIVILEGES;")
        cnx.commit()

        return render_template('owner_update_admin.html', message="Revoked Admin from {}".format(username))

    return render_template('/')                                                                                                                                                                                                                                                                                                                                                                                                        pantry.py                                                                                           0000664 0001750 0001750 00000012055 14612350363 011721  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
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
cur = cnx.cursor(dictionary=True)

pantry = Blueprint('pantry', __name__, template_folder='templates')

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

@pantry.route('/pantry')
def pantry_page():
    update_config()
    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return redirect( '/update_pantry' )
    else:
        message = ''
        return render_template('register.html', message='Please sign in.')


@pantry.route('/update_pantry', methods=['GET', 'POST'])
def update_pantry():
    update_config()
    #try:
    config = {
        'user': session['username'],
        'password': session['password'],
        'host': 'localhost',
        'database': 'mydatabase',
    }
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor(dictionary=True)

    if request.method == 'GET':
        cur.execute("SELECT R.Name FROM Recipes R;")
        recipes = cur.fetchall()
        
        user_ingredients = []
        cur.execute("SELECT Ingredient FROM User_Pantry WHERE Username = %s", (session['username'],))
        user_ingredients = cur.fetchall()
        user_ingredients = [ingredient['Ingredient'] for ingredient in user_ingredients]
        
        params = "RI.Ingredient = '" #string
        for i, ingredient in enumerate(user_ingredients):
            params += ingredient + "'"
            if i < len(user_ingredients) - 1: 
                params += "OR RI.Ingredient = "
        
        cur.execute("SELECT R.Recipe_ID FROM Recipes R INNER JOIN Recipe_Ingredients RI ON R.Recipe_ID=RI.Recipe_ID WHERE %s", (params,))
        possible_recipes = cur.fetchall()    
        missing_ingredients_per_recipe = []
        
        for recipe_id in possible_recipes:
            recipe_ingredients = []
            cur.execute("SELECT Ingredient FROM Recipe_Ingredients WHERE Recipe_ID = %s", (recipe_id,))
            recipe_ingredients = cur.fetchall()
            recipe_ingredients = [ingredient['Ingredient'] for ingredient in recipe_ingredients]
            missing_ingredients = []
        
            for ingredient in recipe_ingredients:
                if ingredient not in user_ingredients:
                    missing_ingredients.append(ingredient)
            if missing_ingredients:
                missing_ingredients_per_recipe.append((recipe_id, missing_ingredients))
            
        categories = ['Carbs','Instrument' ,'Fruits', 'Vegetables', 'Grains', 'Meat', 'Seafood', 'Dairy & Eggs', 'Complementary', 'Misc']
    
        # Initialize dictionary to hold ingredients for each category
        categorized_ingredients = {category: [] for category in categories}

        # Fetch all ingredients and categorize them
        for category in categories:
            cur.execute(
                "SELECT * FROM Ingredients WHERE Category = %s", (category,))
            ingredients = [ingredient['Name'] for ingredient in cur.fetchall()]
            categorized_ingredients[category] = ingredients
            
        return render_template('pantrypage.html', name=session['username'], categorized_ingredients=categorized_ingredients, recipes=recipes, user_ingredients=user_ingredients, possible_recipes=possible_recipes, missing_ingredients_per_recipe=missing_ingredients_per_recipe)

        

    if request.method == 'POST':
        selected_ingredients = request.form.getlist('selected_ingredients')
        user_ingredients = []
        cur.execute("SELECT Ingredient FROM User_Pantry WHERE Username = %s", (session['username'],))
        user_ingredients = cur.fetchall()
        user_ingredients = [ingredient['Ingredient'] for ingredient in user_ingredients]

        # Add selected ingredients to user's pantry
        for ingredient in selected_ingredients:
            cur.execute(
                "INSERT INTO User_Pantry (Username, Ingredient) VALUES (%s, %s)", (session['username'], ingredient))
            cnx.commit()

        # Remove ingredients not selected
        for ingredient in user_ingredients:
            if ingredient not in selected_ingredients:
                cur.execute(
                    "DELETE FROM User_Pantry WHERE Username = %s AND Ingredient = %s", (session['username'], ingredient))
                cnx.commit()
                
        return redirect('/pantry')

    # Render the template with categorized ingredients and user's ingredients


# except Exception as e:
#     cnx.rollback()
#     # print(f"Error: {e}")
#     # return redirect('/pantry')
#     return f"Error: {e}"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   recipes.py                                                                                          0000664 0001750 0001750 00000031256 14612344660 012045  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
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

                                                                                                                                                                                                                                                                                                                                                  reset_db.py                                                                                         0000664 0001750 0001750 00000002365 14612341050 012167  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  #Timestamp: 4/21 8:16pm

import mysql.connector

#change to fit your user, password, and database name
config = {
	'user': 'root',
	'password': 'root1',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor(dictionary=True)
cur.execute("SET foreign_key_checks=0")
cur.execute("DROP USER IF EXISTS 'group20'@'localhost'")
cur.execute("DROP USER IF EXISTS 'mrkrabs'@'localhost'")
cur.execute("DROP ROLE IF EXISTS 'owner'")
cur.execute("DROP ROLE IF EXISTS 'admin'")
cur.execute("DROP ROLE IF EXISTS 'member'")
cur.execute("DROP ROLE IF EXISTS'Guest'")
cur.execute("SELECT Username FROM Users")
users = cur.fetchall()
for user in users:
	cur.execute("DROP USER IF EXISTS %s@'localhost'", (user['Username'],))


cur.execute( '''
	DROP TABLE IF EXISTS Users
''')

cur.execute( '''
	DROP TABLE IF EXISTS User_Pantry
''')

cur.execute( '''
	DROP TABLE IF EXISTS User_Allergens
''')

cur.execute( '''
	DROP TABLE IF EXISTS Recipes
''')

cur.execute( '''
	DROP TABLE IF EXISTS Recipe_Ingredients
''')

cur.execute( '''
	DROP TABLE IF EXISTS Recipe_Allergens
''')

cur.execute( '''
	DROP TABLE IF EXISTS Ingredients
''')
cur.execute( '''
	DROP TABLE IF EXISTS Allergens
''')
print('No more tables')

cur.close()
cnx.close()
                                                                                                                                                                                                                                                                           setup.py                                                                                            0000664 0001750 0001750 00000031227 14612347104 011545  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  #Timestamp: 4/22 6pm

import mysql.connector
#from PopIngredients import popingredients 

"""
BEFORE RUNNING:
Create the owner user: CREATE USER 'root'@'localhost' IDENTIFIED BY 'root1';
Create database: CREATE DATABASE mydatabase;
Give all permissions: GRANT ALL ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
Grant create user: GRANT CREATE USER ON *.* TO 'root'@'localhost';
Grant drop role: GRANT DROP ROLE ON *.* TO 'root'@'localhost';
"""

config = {
	'user': 'root',
	'password': 'root1',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()
#cur.execute("CREATE DATABASE mydatabase")

#User Table
cur.execute( '''
	CREATE TABLE Users (
		Username varchar(50) NOT NULL,
		Password varchar(256) NOT NULL,
  		First_Name varchar(50) NOT NULL,
		Last_Name varchar(100) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#Allergens Table
cur.execute( '''
	CREATE TABLE Allergens (
		Name varchar(50) NOT NULL,
		Primary KEY(Name)
	)
''')

#Ingredients Table
cur.execute('''
	CREATE TABLE Ingredients (
		Name varchar(50) NOT NULL,
		Allergy_Category varchar(50) NULL,
		Category varchar(50) NOT NULL,
		CONSTRAINT fk_all FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT UK_Ingredients UNIQUE KEY (Name, Allergy_Category, Category)
		)
''')

#User Pantry Table
cur.execute( '''
	CREATE TABLE User_Pantry (
		Username varchar(50) NOT NULL,
		Ingredient varchar(50) NOT NULL,
		CONSTRAINT fk_users FOREIGN KEY (Username) REFERENCES Users(Username) ON DELETE CASCADE,
		CONSTRAINT fk_ingr FOREIGN KEY (Ingredient) REFERENCES Ingredients(Name) ON DELETE CASCADE,
		CONSTRAINT PK_UserIng PRIMARY KEY (Username, Ingredient)
	)
''')

#User Allergens Table
cur.execute( '''
	CREATE TABLE User_Allergens (
		Username varchar(50) NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		CONSTRAINT fk_user FOREIGN KEY (Username) REFERENCES Users(Username) ON DELETE CASCADE,
		CONSTRAINT fk_aller FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT UK_UserAllergy UNIQUE KEY (Username, Allergy_Category)
	)
''')

#Recipes Table
cur.execute( '''
	CREATE TABLE Recipes (
		Recipe_ID INT AUTO_INCREMENT,
		Name varchar(50) NOT NULL,
		Category varchar(50) NOT NULL,
  		Description TEXT NULL,
    		Prep_Time INT NULL,
      		Cook_Time INT NULL,
		Instructions TEXT NOT NULL,
		PRIMARY KEY (Recipe_ID)
	)
''')

#Recipe Ingredient Table
cur.execute( '''
	CREATE TABLE Recipe_Ingredients (
		Recipe_ID INT NOT NULL,
		Ingredient varchar(50) NOT NULL,
		Amount varchar(15)  NOT NULL,
		CONSTRAINT fk_RIID FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE,
		CONSTRAINT fk_Ing FOREIGN KEY (Ingredient) REFERENCES Ingredients(Name) ON DELETE CASCADE,
		CONSTRAINT PK_RecipeIng PRIMARY KEY (Recipe_ID, Ingredient, Amount)
	)
''')

#Recipe Allergens Table
cur.execute( '''
	CREATE TABLE Recipe_Allergens (
		Recipe_ID INT NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		CONSTRAINT fk_RID FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE,
		CONSTRAINT fk_allergy FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT UK_RecipeAllergy UNIQUE KEY (Recipe_ID, Allergy_Category)
	)
''')

print('Created tables')

#popingredients()

#do privileges setup
cur.execute("CREATE USER 'group20'@'localhost' IDENTIFIED BY 'group20'")
cur.execute("CREATE ROLE 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipes TO 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Ingredients TO 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Allergens TO 'Guest'")
cur.execute("GRANT SELECT, INSERT ON mydatabase.User_Allergens TO 'Guest'")
cur.execute("GRANT SELECT, INSERT ON mydatabase.Users TO 'Guest'")
cur.execute("GRANT 'Guest' TO 'group20'@'localhost'")
cur.execute("SET DEFAULT ROLE 'Guest' TO 'group20'@'localhost'")

cur.execute("CREATE ROLE 'member'")
cur.execute("GRANT SELECT on mydatabase.Recipes TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Ingredients TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.Ingredients TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.Users TO 'member'")
cur.execute("GRANT UPDATE(Password, First_Name, Last_Name) ON mydatabase.Users TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.User_Pantry TO 'member'")
cur.execute("GRANT Update(Ingredient) ON mydatabase.User_Pantry TO 'member'")
cur.execute("GRANT DELETE ON mydatabase.User_Pantry TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.User_Allergens TO 'member'")
cur.execute("GRANT Update(Allergy_Category) ON mydatabase.User_Allergens TO 'member'")
cur.execute("GRANT DELETE ON mydatabase.User_Pantry TO 'member'")
cur.execute("FLUSH PRIVILEGES")

cur.execute("CREATE ROLE 'admin'")
cur.execute("GRANT SELECT, UPDATE, DELETE ON mydatabase.Users TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Allergens TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Ingredients TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipes TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipe_Ingredients TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipe_Allergens TO 'admin'")
cur.execute("FLUSH PRIVILEGES")

cur.execute("CREATE USER 'mrkrabs'@'localhost' IDENTIFIED BY '35df8167b065b3a7e929a9712fe5164b42282f5edc215fce95baea8ae80fc9df'")
cur.execute("INSERT INTO Users (Username, Password, First_Name, Last_Name) VALUES ('mrkrabs', '35df8167b065b3a7e929a9712fe5164b42282f5edc215fce95baea8ae80fc9df', 'Eugene', 'Krabs')")
cnx.commit()
cur.execute("CREATE ROLE 'owner'")
cur.execute("GRANT ALL ON *.* TO 'owner'")
cur.execute("GRANT ALL ON *.* TO 'mrkrabs'@'localhost'")
cur.execute("GRANT 'owner' TO 'mrkrabs'@'localhost'")
#cur.execute("GRANT 'admin' TO 'mrkrabs'@'localhost' WITH ADMIN OPTION")

cur.execute("FLUSH PRIVILEGES")
print("created roles, owner, and group20")
cnx.commit()


cur.execute("INSERT INTO Allergens(Name) VALUES('eggs'), ('shellfish'), ('peanuts'), ('sesame'), ('soy'), ('fish'), ('treenuts'), ('dairy'), ('gluten'), ('none');")
cnx.commit()

cur.execute("INSERT INTO Ingredients(Name,Allergy_Category,Category) VALUES('egg','eggs','Dairy & Eggs'), ('milk', 'dairy', 'Dairy & Eggs'), ('rice', NULL, 'Grains'), \
																			('bread', 'gluten', 'Carbs'),  ('potato', NULL, 'Vegetables'), ('tomato', NULL, 'Vegetables'), \
																			('lettuce', NULL, 'Vegetables'), ('banana', NULL, 'Fruits'), ('apple', NULL, 'Fruits'), \
																			('chicken', NULL, 'Meat'), ('beef', NULL, 'Meat'), ('salmon', 'fish', 'Seafood'), ('Krabby Patty', 'shellfish', 'Meat'),  \
																			('Secret Patty Formula', 'shellfish', 'Misc'), ('Burger Sauce', NULL, 'Complementary'), ('Pickles', NULL, 'Vegetables'), \
																			('Ketchup', NULL, 'Complementary'), ('Mustard', NULL, 'Complementary'), ('Burger Sauce', NULL, 'Complementary'),\
																			('shrimp', 'shellfish', 'Seafood'),('mayonnaise', NULL, 'instrument'), ('buns', 'gluten', 'Carbs'),\
																			('cheese', 'dairy', 'Dairy & Eggs'), ('almonds', 'treenuts', 'Complementary'), ('soy sauce', 'soy', 'Complementary'), \
																			('peanut butter', 'peanuts', 'Complementary'), ('sesame oil', 'sesame', 'Complementary'), ('olive oil', NULL, 'Complementary'), \
																			('sugar', NULL, 'Misc'), ('salt', NULL, 'Misc'), ('spaghetti', 'gluten', 'Carbs'), \
																			('quinoa', NULL, 'Grains'), ('couscous', NULL, 'Grains'), ('brown rice', NULL, 'Grains'), \
																			('white rice', NULL, 'Grains'), ('sweet potato', NULL, 'Vegetables'), ('onion', NULL, 'Vegetables'), \
																			('garlic', NULL, 'Vegetables'), ('bell pepper', NULL, 'Vegetables'), ('strawberries', NULL, 'Fruits'), \
																			('blueberries', NULL, 'Fruits'), ('peaches', NULL, 'Fruits'), ('kiwi', NULL, 'Fruits'), \
																			('pork', NULL, 'Meat'), ('turkey', NULL, 'Meat'), ('bacon', NULL, 'Meat'), \
																			('lobster', 'shellfish', 'Seafood'), ('crab', 'shellfish', 'Seafood'), ('clams', 'shellfish', 'Seafood'), \
																			('oysters', 'shellfish', 'Seafood'), ('butter', 'dairy', 'Dairy & Eggs'), ('yogurt', 'dairy', 'Dairy & Eggs'), \
																			('cream', 'dairy', 'Dairy & Eggs'), ('eggnog', 'dairy', 'Dairy & Eggs'), ('cashews', 'treenuts', 'Complementary'), \
																			('walnuts', 'treenuts', 'Complementary'), ('hazelnuts', 'treenuts', 'Complementary'), ('edamame', 'soy', 'Complementary'), \
																			('tofu', 'soy', 'Complementary'), ('tempeh', 'soy', 'Complementary'), ('sunflower seeds', NULL, 'Complementary'), \
																			('honey', NULL, 'Misc'), ('maple syrup', NULL, 'Misc'), ('balsamic vinegar', NULL, 'Misc'), \
																			('cinnamon', NULL, 'Misc'), ('cumin', NULL, 'Misc'), ('cucumber', NULL, 'Vegetables'), ('lemon', NULL, 'Fruits');")
cnx.commit()

cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES ('Scrambled Eggs', 'Breakfast', 'Simple and delicious scrambled eggs.', 5, 5, 'Crack eggs into a bowl. \n Beat eggs until well mixed. \nHeat a skillet over medium heat. \nPour beaten eggs into the skillet. \nCook, stirring occasionally, until eggs are set.');")
cnx.commit()

cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient, Amount) VALUES (1, 'egg', '3');")
cnx.commit()


cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES ('Vegetable Stir Fry', 'Dinner', 'An easy at home veggie stir fry.', 15, 10, 'Heat a skillet over medium heat. \n Add olive oil, then add bell pepper, onion, and garlic. Sauté until vegetables are softened. \nAdd sweet potato and stir-fry until tender. \nAdd rice and stir-fry until rice is cooked through. \nStir in soy sauce, sesame oil, and olive oil. \nSeason with salt and pepper to taste.');")
cnx.commit()

cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient, Amount) VALUES (2, 'olive oil', '1'), (2, 'bell pepper', '2'), (2, 'onion', '1'), (2, 'garlic', '3'), (2, 'sweet potato', '1'), (2, 'rice', '2'), (2, 'soy sauce', '1');")
cnx.commit()


cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES ('Chicken Salad', 'Lunch', 'A simple healthy salad with protein.', 5, 1, 'Cook chicken until cooked. \n Cool and shred chicken. \nIn a large bowl, mix shredded chicken with lettuce, tomato, and cucumber. \nDrizzle with olive oil and lemon juice. \nSeason with salt to taste.');")
cnx.commit()

cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient, Amount) VALUES (3, 'chicken', '1'), (3, 'lettuce', '1'), (3, 'tomato', '1'), (3, 'cucumber', '2'), (3, 'olive oil', '1'), (3, 'lemon', '1');")
cnx.commit()

cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES ('Krabby Patty', 'Lunch', 'The famous Krabby Patty from Bikini Bottom.', 20, 15, '1. Prepare the Krabby Patty Patty by mixing the secret ingredients. \n2. Form the mixture into patties and cook on a grill or skillet until cooked through. \n3. Toast the Krabby Patty Bun. \n4. Assemble the Krabby Patty by placing the cooked patty on the bun. \n5. Add lettuce, tomato, onion, pickles, and cheese on top of the patty. \n6. Spread ketchup, mustard, mayonnaise, and burger sauce on the top bun. \n7. Cover the patty with the top bun and serve hot.');")
cnx.commit()

cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient, Amount) VALUES (4, 'Krabby Patty', '1'), (4, 'buns', '1'), (4, 'lettuce', '1'), (4, 'tomato', '1'), (4, 'onion', '1'), (4, 'pickles', '2'), (4, 'ketchup', '1'), (4, 'mustard', '1'), (4, 'mayonnaise', '1'), (4, 'cheese', '1'), (4, 'Burger Sauce', '1');")
cnx.commit()

cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES ('Cucumber Salad', 'Breakfast', 'Yummy cucubmer. Yep, this is a real recipe.', 67, 32, 'Put cucumber into bowl \n Consume ');")
cnx.commit()

cur.execute("INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient, Amount) VALUES (5, 'cucumber', '10001'), (5, 'cucumber', '11'), (5, 'cucumber', '115'), (5, 'cucumber', '15'), (5, 'cucumber', '155'), (4, 'cucumber', '22'),  (4, 'cucumber', '321'), (4, 'cucumber', '344'), (4, 'cucumber', '529'), (4, 'cucumber', '541'), (4, 'cucumber', '41'), (4, 'cucumber', '741'), (4, 'cucumber', '773'), (4, 'cucumber', '94');")
cnx.commit()


# database.commit() unsure if line is needed, i dont think it is
cur.close()
cnx.close()
                                                                                                                                                                                                                                                                                                                                                                         user.py                                                                                             0000664 0001750 0001750 00000023442 14612344660 011367  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
import mysql.connector
import hashlib

secret_key = 'this is our top secret super key that definently isnt going to also be uploaded on our github page'

config = {
    'user': 'group20',
    'password': 'group20',
    'host': 'localhost',
    'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()

user = Blueprint('user', __name__, template_folder='templates')

# ---

def update_config():
    global config
    config = {
        'user': session['username'],
        'password': session['password'],
        'host': 'localhost',
        'database': 'mydatabase',
    }
    global cur
    global cnx
    cnx = mysql.connector.connect(**config)
    cur = cnx.cursor()

# ---

@user.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    update_config()
    try:
        if 'username' not in session:
            return redirect(url_for('login'))  # Redirect to login if user not authenticated

        if request.method == 'GET':
            username = session['username']
            global cur
            global cnx
            cur.execute("SELECT * FROM Users WHERE Username = %s", (username,))
            user_data = cur.fetchone()
            if user_data:
                print(user_data)
                return render_template('userinfo.html', First_Name=user_data[2], Last_Name=user_data[3], Password=user_data[1], Username=user_data[0])
            else:
                return "User not found"
        elif request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            password = request.form['password']
            if password:  # Only hash password if provided

                hashed_password = password + secret_key
                hashed_password = hashlib.sha256(hashed_password.encode())

                password = hashed_password.hexdigest()
                
                config = {
                    'user': 'root',
                    'password': 'root1',
                    'host': 'localhost',
                    'database': 'mydatabase',
                }
                cnx = mysql.connector.connect(**config)
                cur = cnx.cursor(dictionary=True)

                cur.execute("ALTER USER %s@'localhost' IDENTIFIED WITH mysql_native_password BY %s", (session['username'], password))
                cnx.commit() #might not be necessary
                cur.close()
                cnx.close()
                session['password'] = password
                config = {
                    'user': session['username'],
                    'password': session['password'],
                    'host': 'localhost',
                    'database': 'mydatabase',
                }      
                cnx = mysql.connector.connect(**config)
                cur = cnx.cursor(dictionary=True)
                cur.execute("UPDATE Users SET First_Name = %s, Last_Name = %s, Password = %s WHERE Username = %s", (first_name, last_name, password, session['username']))
            else:
                cur.execute("UPDATE Users SET First_Name = %s, Last_Name = %s WHERE Username = %s", (first_name, last_name, session['username']))
            cnx.commit()
            return redirect(url_for('user.user_profile'))
    except mysql.connector.Error as err:
        cnx.rollback()
        return "Error: {}".format(err)
    return redirect(url_for('user.user_profile'))

# ---

@user.route('/admin_panel/update_user')
def update_user_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_user.html')

    message = ''
    return render_template('register.html', message='')

# ---

@user.route('/admin_panel/update_user_function', methods=['GET', 'POST'])
def update_user_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        password = request.form['password']

        # added after safe rbac branch
        global config
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        if password:
            hashed_password = password + secret_key
            hashed_password = hashlib.sha256(hashed_password.encode())

            password = hashed_password.hexdigest()
            
            config = {
                'user': 'root',
                'password': 'root1',
                'host': 'localhost',
                'database': 'mydatabase',
            }
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            cur.execute("ALTER USER %s@'localhost' IDENTIFIED WITH mysql_native_password BY %s", (username, password))
            cnx.commit() #might not be necessary
            cur.close()
            cnx.close()

            config = {
                'user': session['username'],
                'password': session['password'],
                'host': 'localhost',
                'database': 'mydatabase',
            }      
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)      
            cur.execute("UPDATE Users SET Password = %s WHERE Username = %s;", (password, username,))
            cnx.commit() 
            # except:
            #     cnx.rollback()
            #     return render_template('admin_panel/update_user.html', message = "Error. Had to roll back.")
        else:
            pass

        if first_name:
            try:
                cur.execute("UPDATE Users SET First_Name = %s WHERE Username = %s;", (first_name, username,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_user.html', message = "Error. Had to roll back.")
        else:
            pass

        if last_name:
            try:
                cur.execute("UPDATE Users SET Last_Name = %s WHERE Username = %s;", (last_name, username,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_user.html', message = "Error. Had to roll back.")
        else:
            pass



        return render_template('admin_panel/update_user.html', message = "Updated {}".format(username))

    return render_template('login.html', message=msg)

# ---

@user.route('/admin_panel/list_user',methods = ['POST', 'GET'])
def list_user_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:

            # added after safe rbac branch
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Users;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_users.html",rows = rows)
        except:
            return render_template("admin_panel/list_users.html",rows = [])
    return render_template("register.html", message='Not authorized')

@user.route('/admin_panel/delete_user')
def delete_user_page():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_user.html')

    message = ''
    return render_template('register.html', message='')

# ---

@user.route('/admin_panel/delete_user_function', methods=['GET', 'POST'])
def delete_user_function():
    update_config()
    if session['role'] != 'admin' and session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. You are not admin')

    msg = ''
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']

        # added after safe rbac branch
        global config
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        try:
            config = {
                'user': 'root',
                'password': 'root1',
                'host': 'localhost',
                'database': 'mydatabase',
            }
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)

            cur.execute("DROP USER %s@'localhost'", (username,))
            cnx.commit() #might not be necessary
            cur.close()
            cnx.close()

            config = {
                'user': session['username'],
                'password': session['password'],
                'host': 'localhost',
                'database': 'mydatabase',
            }      
            cnx = mysql.connector.connect(**config)
            cur = cnx.cursor(dictionary=True)  
            cur.execute("DELETE FROM Users WHERE Username = %s;", (username,))
            cnx.commit() 
        except:
            cnx.rollback()
            return render_template('admin_panel/delete_user.html', message = "Error. Had to roll back.")

        return render_template('admin_panel/delete_user.html', message = "Deleted {}".format(username))

    return render_template('login.html', message=msg)


# ---
                                                                                                                                                                                                                              templates/                                                                                          0000775 0001750 0001750 00000000000 14612341050 012016  5                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  templates/register.html                                                                             0000664 0001750 0001750 00000006444 14612116440 014543  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Create Account</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <form action="{{ url_for('auth.register') }}" method="post" autocomplete="off">
        <label for="firstName">First Name:</label>
        <input type="text" id="firstName" name="firstName" required>

        <label for="lastName">Last Name:</label>
        <input type="text" id="lastName" name="lastName" required>

        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>

        <label for="password">Password (8 characters minimum):</label>
        <input type="password" id="password" name="password" minlength="8" required>

        <div class="allergy-row">
            <div><input type="checkbox" id="gluten" name="allergies" value="gluten"> <label for="gluten">Gluten</label></div>
            <div><input type="checkbox" id="dairy" name="allergies" value="dairy"> <label for="dairy">Dairy</label></div>
            <div><input type="checkbox" id="treenuts" name="allergies" value="truenuts"> <label for="treenuts">Tree Nuts</label></div>
        </div>
        <div class="allergy-row">
            <div><input type="checkbox" id="fish" name="allergies" value="fish"> <label for="fish">Fish</label></div>
            <div><input type="checkbox" id="soy" name="allergies" value="soy"> <label for="soy">Soy</label></div>
            <div><input type="checkbox" id="sesame" name="allergies" value="sesame"> <label for="sesame">Sesame</label></div>
        </div>
        <div class="allergy-row">
            <div><input type="checkbox" id="peanuts" name="allergies" value="peanuts"> <label for="peanuts">Peanuts</label></div>
            <div><input type="checkbox" id="shellfish" name="allergies" value="shellfish"> <label for="shellfish">ShellFish</label></div>
            <div><input type="checkbox" id="eggs" name="allergies" value="eggs"> <label for="eggs">Eggs</label></div>
        </div>


        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Create Account</button>
    </form>
    <footer>
      <a href="/">Go back to home</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>

<!--shellfish, milk, eggs, soy products, and sesame-->                                                                                                                                                                                                                            templates/guest.html                                                                                0000664 0001750 0001750 00000003432 14612116440 014040  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Welcome Guest</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        .welcome-message {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .redirect form {
            margin-bottom: 10px;
        }

        .guest-button {
            background-color: #d11414;
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .login-button {
            background-color: #4285f4; /* Different color for login button */
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .register-button {
            background-color: #d11414; /* Different color for register button */
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .icon-container {
            display: flex;
            justify-content: space-around;
            width: 200px;
        }
        .icon-container a {
            text-decoration: none;
            color: #333;
        }
        .icon-container img {
            width: 50px;
            height: 50px;
        }
    </style>
</head>
<body>
    <div class="welcome-message">
        Howdy
    </div>
    <footer>
      <a href="/">Go back to home</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                      templates/login.html                                                                                0000664 0001750 0001750 00000004730 14612116440 014023  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Login page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            text-align: center;
            padding-top: 100px;
        }
        h1 {
            color: #333;
        }
        .login-form {
            margin-top: 50px;
        }
        .login-form input[type="text"],
        .login-form input[type="password"] {
            width: 250px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .login-form input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .login-form input[type ="new"]{
            background-color: #2e46af;
            color: white;
            padding: 10px 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .register-button{
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Howdy</h1>
        <div class="login-form">
            <form action="{{ url_for('auth.login') }}" method="post">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <div class="message">{{message}}</div>
                <input type="submit" value="Login">
            </form>
            <!-- <form action="/register_user">
                <input type ="new" value="Create new account">
            </form> -->
        </div>
        <p></p>
        <a href="/register_page">
            <button class="register-button">Create Account</button> 
        </a>
    </div> 
    <footer>
      <a href="/">Go back to home</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                        templates/layout.html                                                                               0000664 0001750 0001750 00000003054 14612116440 014226  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recipe Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f7f7;
        }
        nav {
            background-color: #333;
            color: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin-left: 10px;
        }
        nav h3 {
            margin: 0;
        }
        .content {
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .authenticated .content {
            margin-top: 20px;
        }
    </style>
</head>
<body class="authenticated">
    <nav class="top">
        <div>
            <h3>Recipe Management System:
                <a href="{{ url_for('auth.home') }}">Home</a>
                <a href="{{ url_for('pantry.pantry_page') }}">Pantry</a>
                <a href="{{ url_for('auth.admin_panel_page') }}">Admin Panel</a>
                <a href="/show_recipes">Show Recipes</a>
                <a href="{{ url_for('auth.logout') }}">Log out</a>
                <a href="{{ url_for('user.user_profile') }}">User Info</a>
            </h3>
        </div>
    </nav>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    templates/recipes.html                                                                              0000664 0001750 0001750 00000010663 14612341050 014344  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Add New Recipe</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f7f7;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding-top: 50px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        form {
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 2px 10px 0px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .ingredient-container {
            margin-bottom: 20px;
        }
        .ingredient-container input[type="text"],
        .ingredient-container input[type="number"] {
            width: calc(50% - 5px);
            margin-bottom: 10px;
        }
        .ingredient-container button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        .time-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .time-container input[type="number"] {
            width: calc(10% - 2px);
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Add New Recipe</h1>
        <form action="{{ url_for('recipes.create_recipe_function') }}" method="post">
            <label for="recipeTitle">Recipe Title:</label>
            <input type="text" id="recipeTitle" name="recipeTitle" required>

            <label for="description">Brief Description:</label>
            <textarea id="description" name="description" rows="4" required></textarea>

            <div class="time-container">
                <label for="cook">Cook Time (in minutes):</label>
                <input type="number" id="cook" name="cook" min="1" required>

                <label for="prepTime">Prep Time (in minutes):</label>
                <input type="number" id="prepTime" name="prepTime" min="1" required>
            </div>

            <div class="ingredient-container">
                <label>Ingredients:</label>
                <div id="ingredient-fields">
                    <div>
                        <input type="text" name="ingredients[]" placeholder="Ingredient" required>
                        <input type="text" name="measurements[]" placeholder="Measurement" required>
                    </div>
                </div>
                <button type="button" onclick="addIngredientField()">Add Ingredient</button>
            </div>

            <label for="instructions">Instructions (use bullet points):</label>
            <textarea id="instructions" name="instructions" rows="8" required></textarea>

            <input type="submit" value="Add Recipe">
        </form>
    </div>

    <script>
        function addIngredientField() {
            const ingredientFields = document.getElementById('ingredient-fields');
            const div = document.createElement('div');
            div.innerHTML = `
                <input type="text" name="ingredients[]" placeholder="Ingredient" required>
                <input type="text" name="measurements[]" placeholder="Measurement" required>
            `;
            ingredientFields.appendChild(div);
        }
    </script>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                             templates/home.html                                                                                 0000664 0001750 0001750 00000000217 14612116440 013637  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  {% extends 'layout.html' %}

{% block title%}Home{% endblock %}

{%block content%}
<h2>Home Page</h2>
<p>Ahoy, {{username}}!</p>
{% endblock %}                                                                                                                                                                                                                                                                                                                                                                                 templates/pantrypage.html                                                                           0000664 0001750 0001750 00000006557 14612350255 015102  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pantry</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome for icons (optional) -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f7f7f7;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .category {
            margin-bottom: 20px;
        }
        .ingredient-list {
            list-style-type: none;
            padding: 0;
        }
        .ingredient-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px;
            background-color: #fff;
            border-radius: 8px;
            margin-bottom: 5px;
        }
        .ingredient-item i {
            color: #777;
            cursor: pointer;
        }
        .search-input {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ name }}'s Pantry</h1>
        
        <div class="row">
            <!-- Iterate through categories and display ingredients -->
            {% for category, ingredients in categorized_ingredients.items() %}
            <div class="col-md-6">
                <div class="category">
                    <h2>{{ category }}</h2>
                    <ul class="ingredient-list">
                        {% for ingredient in ingredients %}
                        <li class="ingredient-item">
                            <label><input type="checkbox" name="selected_ingredients" value="{{ ingredient }}" {% if ingredient in selected_ingredients %} checked {% endif %}> {{ ingredient }}</label>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <form method="POST" action="/update_pantry">
            <button type="submit" class="btn btn-primary">Update Pantry</button>
        </form>

        <h2>Recipes</h2>
        <ul>
            {% for recipe in recipes %}
                <li>{{ recipe[0] }}</li>
            {% endfor %}
        </ul>

        <!-- User's Ingredients -->
        <h2>User's Ingredients</h2>
        <ul>
            {% for ingredient in selected_ingredients %}
                <li>{{ ingredient }}</li>
            {% endfor %}
        </ul>

        <!-- Possible Recipes -->
        <h2>Possible Recipes</h2>
        <ul>
            {% for recipe_id, missing_ingredients in missing_ingredients_per_recipe %}
                <li>{{ recipe_id }} - Missing Ingredients: {{ missing_ingredients }}</li>
            {% endfor %}
        </ul>
    </div>

    <footer>
        <a href="/home">Go back to home</a>
        <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                 templates/recipeinfo.html                                                                           0000664 0001750 0001750 00000004622 14612116440 015036  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Recipe Details</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f7f7f7;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        .recipe-details {
            margin-bottom: 30px;
        }
        .recipe-details h2 {
            color: #4CAF50;
            margin-bottom: 10px;
        }
        .ingredients-list {
            margin-bottom: 20px;
        }
        .ingredient-item {
            margin-bottom: 5px;
        }
        .time-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .steps {
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ recipeTitle }}</h1>
        <div class="recipe-details">
            <p><strong>Description:</strong> {{ description }}</p>
            <div class="time-container">
                <p><strong>Cook Time:</strong> {{ cook_time }} minutes</p>
                <p><strong>Prep Time:</strong> {{ prep_time }} minutes</p>
            </div>
            <div class="ingredients-list">
                <h2>Ingredients:</h2>
                <ul>
                    <!-- {% for ingredient, measurement in ingredients %}
                    <li class="ingredient-item">{{ ingredient }} - {{ measurement }}</li>
                    {% endfor %} -->
                    {% for row in ingredients %}
                    <li class="ingredient-item">{{ row["Ingredient"] }} - {{ row["Amount"] }}</li>
                    {% endfor %}
                </ul>
            </div>
            <div class="steps">
                <h2>Instructions:</h2>
                <ol>
                    {% for step in instructions %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
            </div>
        </div>
    </div>
    <footer>
        <a href="/show_recipes">Go back to recipes</a>
        <p>&copy; Group 20 Recipe Management System</p>
      </footer>
</body>
</html>                                                                                                              templates/welcome.html                                                                              0000664 0001750 0001750 00000004141 14612116440 014342  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Welcome to Recipe Management Application</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        .welcome-message {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .redirect form {
            margin-bottom: 10px;
        }

        .guest-button {
            background-color: #d11414;
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .login-button {
            background-color: #4285f4; /* Different color for login button */
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .register-button {
            background-color: #d11414; /* Different color for register button */
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .icon-container {
            display: flex;
            justify-content: space-around;
            width: 200px;
        }
        .icon-container a {
            text-decoration: none;
            color: #333;
        }
        .icon-container img {
            width: 50px;
            height: 50px;
        }
    </style>
</head>
<body>
    <div class="welcome-message">
        Welcome to Recipe Management Application by Group 20
    </div>
    <div class="redirect">
        <a href="/show_recipes">
            <button class="guest-button">Show Recipes</button>
        </a>

        <a href="/login_page">
            <button class="login-button">Login</button>
        </a>
        
        <a href="/register_page">
            <button class="register-button">Register</button>
        </a>

    </div>
    
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                                               templates/admin_panel/                                                                              0000775 0001750 0001750 00000000000 14612341050 014265  5                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  templates/admin_panel/adminpanel.html                                                               0000664 0001750 0001750 00000010156 14612116440 017271  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Admin Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        .welcome-message {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .redirect form {
            margin-bottom: 10px;
        }

        .guest-button {
            background-color: #d11414;
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .login-button {
            background-color: #4285f4; /* Different color for login button */
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .register-button {
            background-color: #d11414; /* Different color for register button */
            color: #ffffff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .icon-container {
            display: flex;
            justify-content: space-around;
            width: 200px;
        }
        .icon-container a {
            text-decoration: none;
            color: #333;
        }
        .icon-container img {
            width: 50px;
            height: 50px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <div class="welcome-message">
        <h1>
            Employees Only
        </h1>
    </div>
    <hr style="width:50%">
    <p></p>
    <div class="redirect">
        <a href="/admin_panel/update_user">
            <button class="guest-button">Update User</button>
        </a>

        <a href="/admin_panel/delete_user">
            <button class="guest-button">Delete User</button>
        </a>
    </div>
    <p></p>
    <hr style="width:50%">
    <p></p>
    <div>
        <a href="/admin_panel/create_ingredient">
            <button class="guest-button">Create Ingredient</button>
        </a>

        <a href="/admin_panel/update_ingredient">
            <button class="guest-button">Update Ingredient</button>
        </a>

        <a href="/admin_panel/delete_ingredients">
            <button class="guest-button">Delete Ingredient</button>
        </a>
    </div>
    <p></p>
    <hr style="width:50%">
    <p></p>
    <div>
        <a href="/admin_panel/create_allergen">
            <button class="guest-button">Create Allergen</button>
        </a>

        <a href="/admin_panel/delete_allergen">
            <button class="guest-button">Delete Allergen</button>
        </a>

    </div>
    <p></p>
    <hr style="width:50%">
    <p></p>
    <div>
        <a href="/admin_panel/create_recipe">
            <button class="guest-button">Create Recipe</button>
        </a>

        <a href="/admin_panel/update_recipe">
            <button class="guest-button">Update Recipe</button>
        </a>

        <a href="/admin_panel/delete_recipe">
            <button class="guest-button">Delete Recipe</button>
        </a>
    </div>
    <p></p>
    <hr style="width:50%">
    <p></p>
    <div>
        <a href="/admin_panel/list_user">
            <button class="guest-button">List Users</button>
        </a>

        <a href="/admin_panel/list_allergens">
            <button class="guest-button">List Allergens</button>
        </a>

        <a href="/admin_panel/list_ingredients">
            <button class="guest-button">List Ingredients</button>
        </a>

        <a href="/admin_panel/list_recipes">
            <button class="guest-button">List Recipes</button>
        </a>

    </div>
    <p></p>
    <hr style="width:50%">
    <p></p>
    <footer>
      <a href="/home">Back to Home</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
    
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                                  templates/admin_panel/list_allergens.html                                                           0000664 0001750 0001750 00000003414 14612116440 020167  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!doctype html>
<html>
   <title>List Allergens</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
   <body>
      <h2>All Allergens</h2>
      <table border = 1>
         <thead>
            <td>Name</td>
         </thead>
         
         {% for row in rows %}
            <tr>
               <td>{{row["Name"]}}</td>	
            </tr>
         {% endfor %}
      </table>
      
      <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
   </body>
</html>
                                                                                                                                                                                                                                                    templates/admin_panel/delete_ingredient.html                                                        0000664 0001750 0001750 00000003740 14612326122 020634  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Delete Ingredient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Delete Ingredient
    </h3>
    <form action="{{ url_for('ingredients.delete_ingredient_function') }}" method="post" autocomplete="off">
        <label for="ingredientName">Delete Which Ingredient:</label>
        <input type="text" id="ingredientName" name="ingredientName" required>

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                templates/admin_panel/list_users.html                                                               0000664 0001750 0001750 00000003761 14612116440 017361  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!doctype html>
<html>
   <title>List Users</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
   <body>
      <h2>All Users</h2>
      <table border = 1>
         <thead>
            <td>Username</td>
            <td>Password</td>
            <td>First Name</td>
            <td>Last Name</td>
         </thead>
         
         {% for row in rows %}
            <tr>
               <td>{{row["Username"]}}</td>
               <td>{{row["Password"]}}</td>
               <td> {{row["First_Name"]}}</td>
               <td>{{row["Last_Name"]}}</td>	
            </tr>
         {% endfor %}
      </table>
      
      <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
   </body>
</html>
               templates/admin_panel/update_user.html                                                              0000664 0001750 0001750 00000004445 14612326122 017505  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Update Account</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>   
    <h3>
        Update User
    </h3>
    <form action="{{ url_for('user.update_user_function') }}" method="post" autocomplete="off">
        <label for="username">Update Which User:</label>
        <input type="text" id="username" name="username" required>

        <label for="firstName">First Name:</label>
        <input type="text" id="firstName" name="firstName">

        <label for="lastName">Last Name:</label>
        <input type="text" id="lastName" name="lastName">

        <label for="password">Password (8 characters minimum):</label>
        <input type="password" id="password" name="password" minlength="1">

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                           templates/admin_panel/delete_recipe.html                                                            0000664 0001750 0001750 00000007446 14612341050 017757  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Delete Ingredient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Delete Ingredient
    </h3>
    <table border = 1>
         <thead>
            <td>ID</td>
            <td>Name</td>
            <td>Category</td>
            <td>Description</td>
            <td>Prep Time</td>
            <td>Cook Time</td>
            <td>Instructions</td>
         </thead>
         
         {% for row in rows %}
            <tr>
               <td>
                  <form id="recipeForm{{row['Recipe_ID']}}" action="/admin_panel/update_recipe_auto_page" method="post">
                  <input type="hidden" id="recipeID" name="recipeID" value="{{row['Recipe_ID']}}">
                  <input type="hidden" id="recipeTitle" name="recipeTitle" value="{{row['Name']}}">
                  <input type="hidden" id="description" name="description" value="{{row['Description']}}">
                  <input type="hidden" id="cook" name="cook" value="{{row['Cook_Time']}}">
                  <input type="hidden" id="prepTime" name="prepTime" value="{{row['Prep_Time']}}">
                  <input type="hidden" id="instructions" name="instructions" value="{{row['Instructions']}}">
                </form>
                <a href="#" onclick="document.getElementById('recipeForm{{row['Recipe_ID']}}').submit(); return false;">{{row["Recipe_ID"]}}</a>
               </td>    
               <td>{{row["Name"]}}</td> 
               <td>{{row["Category"]}}</td> 
               <td>{{row["Description"]}}</td> 
               <td>{{row["Prep_Time"]}}</td> 
               <td>{{row["Cook_Time"]}}</td> 
               <td>{{row["Instructions"]}}</td> 
            </tr>
            <tr>
                {% for ingredient in ingredients %}
                {% if ingredient["Recipe_ID"] == row['Recipe_ID'] %}
                <td>{{ingredient["Ingredient"]}} - {{ingredient["Amount"]}}</td>
                {% endif %}
                {% endfor %}
            </tr>
         {% endfor %}
      </table>
    <form action="{{ url_for('recipes.delete_recipe_function') }}" method="post" autocomplete="off">
        <label for="recipeID">Delete Recipe with ID:</label>
        <input type="text" id="recipeID" name="recipeID" required>

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                          templates/admin_panel/update_ingredient.html                                                        0000664 0001750 0001750 00000004323 14612326122 020652  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Update Ingredient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Update Ingredient
    </h3>
    <form action="{{ url_for('ingredients.update_ingredient_function') }}" method="post" autocomplete="off">
        <label for="ingredientName">Update Which Ingredient:</label>
        <input type="text" id="ingredientName" name="ingredientName" required>

        <label for="allergyCategory">Allergy Category:</label>
        <input type="text" id="allergyCategory" name="allergyCategory">

        <label for="category">Category:</label>
        <input type="text" id="category" name="category">

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                                                             templates/admin_panel/list_recipes.html                                                             0000664 0001750 0001750 00000006572 14612116440 017655  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!doctype html>
<html>
   <title>List Recipes</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
   <body>
      <h2>All Recipes</h2>
      <table border = 1>
         <thead>
            <td>ID</td>
            <td>Name</td>
            <td>Category</td>
            <td>Description</td>
            <td>Prep Time</td>
            <td>Cook Time</td>
            <td>Instructions</td>
         </thead>
         
         {% for row in rows %}
            <tr>
               <td>
                  <form id="recipeForm{{row['Recipe_ID']}}" action="/admin_panel/update_recipe_auto_page" method="post">
                  <input type="hidden" id="recipeID" name="recipeID" value="{{row['Recipe_ID']}}">
                  <input type="hidden" id="recipeTitle" name="recipeTitle" value="{{row['Name']}}">
                  <input type="hidden" id="description" name="description" value="{{row['Description']}}">
                  <input type="hidden" id="cook" name="cook" value="{{row['Cook_Time']}}">
                  <input type="hidden" id="prepTime" name="prepTime" value="{{row['Prep_Time']}}">
                  <input type="hidden" id="instructions" name="instructions" value="{{row['Instructions']}}">
                </form>
                <a href="#" onclick="document.getElementById('recipeForm{{row['Recipe_ID']}}').submit(); return false;">{{row["Recipe_ID"]}}</a>
               </td> 	
               <td>{{row["Name"]}}</td> 
               <td>{{row["Category"]}}</td> 
               <td>{{row["Description"]}}</td> 
               <td>{{row["Prep_Time"]}}</td> 
               <td>{{row["Cook_Time"]}}</td> 
               <td>{{row["Instructions"]}}</td> 
            </tr>
            <tr>
                {% for ingredient in ingredients %}
                {% if ingredient["Recipe_ID"] == row['Recipe_ID'] %}
                <td>{{ingredient["Ingredient"]}} - {{ingredient["Amount"]}}</td>
                {% endif %}
                {% endfor %}
            </tr>
         {% endfor %}
      </table>
      
      <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
   </body>
</html>
                                                                                                                                      templates/admin_panel/delete_user.html                                                              0000664 0001750 0001750 00000003662 14612326122 017465  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Delete Account</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Delete User
    </h3>
    <form action="{{ url_for('user.delete_user_function') }}" method="post" autocomplete="off">
        <label for="username">Delete Which User:</label>
        <input type="text" id="username" name="username" required>

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                              templates/admin_panel/create_allergen.html                                                          0000664 0001750 0001750 00000003712 14612341050 020272  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Create Allergen</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Create Allergen
    </h3>
    <form action="{{ url_for('allergens.create_allergen_function') }}" method="post" autocomplete="off">
        <label for="allergenName">Create Allergen:</label>
        <input type="text" id="allergenName" name="allergenName" required>

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                      templates/admin_panel/create_ingredient.html                                                        0000664 0001750 0001750 00000004335 14612326122 020636  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Create Ingredient</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Create Ingredient
    </h3>
    <form action="{{ url_for('ingredients.create_ingredient_function') }}" method="post" autocomplete="off">
        <label for="ingredientName">Ingredient Name:</label>
        <input type="text" id="ingredientName" name="ingredientName" required>

        <label for="allergyCategory">Allergy Category:</label>
        <input type="text" id="allergyCategory" name="allergyCategory" required>

        <label for="category">Category:</label>
        <input type="text" id="category" name="category" required>

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                                                   templates/admin_panel/list_ingredients.html                                                         0000664 0001750 0001750 00000003702 14612116440 020526  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!doctype html>
<html>
   <title>List Ingredients</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
   <body>
      <h2>All Ingredients</h2>
      <table border = 1>
         <thead>
            <td>Name</td>
            <td>Allergy Category</td>
            <td>Restriction Category</td>
         </thead>
         
         {% for row in rows %}
            <tr>
               <td>{{row["Name"]}}</td>	
               <td>{{row["Allergy_Category"]}}</td> 
               <td>{{row["Category"]}}</td> 
            </tr>
         {% endfor %}
      </table>
      
      <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
   </body>
</html>
                                                              templates/admin_panel/delete_allergen.html                                                          0000664 0001750 0001750 00000003651 14612341050 020273  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Delete Allergen</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Delete Allergen
    </h3>
    <form action="{{ url_for('allergens.delete_allergens_function') }}" method="post" autocomplete="off">
        <label for="allergenName">Delete Allergen:</label>
        <input type="text" id="allergenName" name="allergenName" required>

        <div class="message">{{ message }}</div>
        <button type="submit" value="Register">Submit</button>
    </form>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                       templates/admin_panel/recipe.html                                                                   0000664 0001750 0001750 00000012004 14612341050 016417  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Add New Recipe</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f7f7;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding-top: 50px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        form {
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 2px 10px 0px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .ingredient-container {
            margin-bottom: 20px;
        }
        .ingredient-container input[type="text"],
        .ingredient-container input[type="number"] {
            width: calc(50% - 5px);
            margin-bottom: 10px;
        }
        .ingredient-container button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        .time-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .time-container input[type="number"] {
            width: calc(10% - 2px);
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Add New Recipe</h1>
        <form action="{{ url_for('recipes.create_recipe_function') }}" method="post">
            <label for="recipeTitle">Recipe Title:</label>
            <input type="text" id="recipeTitle" name="recipeTitle" required>

            <label for="description">Brief Description:</label>
            <textarea id="description" name="description" rows="4" required></textarea>

            <div class="time-container">
                <label for="cook">Cook Time (in minutes):</label>
                <input type="number" id="cook" name="cook" min="1" required>

                <label for="prepTime">Prep Time (in minutes):</label>
                <input type="number" id="prepTime" name="prepTime" min="1" required>
            </div>

            <div class="ingredient-container">
                <label>Ingredients:</label>
                <div id="ingredient-fields">
                    <div>
                        <!-- <input type="text" name="ingredients[]" placeholder="Ingredient" required> -->
                        <label for="dropdown">Select an option:</label>
                        <select id="dropdown" name="ingredients[]" placeholder="Ingredient">
                            {% for item in ingredients %}
                                <option>{{ item['Name'] }}</option>
                            {% endfor %}
                        </select>
                        <input type="text" name="measurements[]" placeholder="Measurement" required>
                    </div>
                </div>
                <button type="button" onclick="addIngredientField()">Add Ingredient</button>
            </div>

            <label for="instructions">Instructions (use bullet points):</label>
            <textarea id="instructions" name="instructions" rows="8" required></textarea>

            <input type="submit" value="Add Recipe">
        </form>
    </div>

    <script>
        function addIngredientField() {
            const ingredientFields = document.getElementById('ingredient-fields');
            const div = document.createElement('div');
            div.innerHTML = `
                <label for="dropdown">Select an option:</label>
                <select id="dropdown" name="ingredients[]">
                    {% for item in ingredients %}
                        <option>{{ item['Name'] }}</option>
                    {% endfor %}
                </select>                
                <input type="text" name="measurements[]" placeholder="Measurement" required>
            `;
            ingredientFields.appendChild(div);
        }
    </script>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            templates/admin_panel/update_recipe_auto.html                                                       0000664 0001750 0001750 00000013101 14612341223 021012  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Update Recipe</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f7f7f7;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding-top: 50px;
        }
        h1, h4 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        form {
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 2px 10px 0px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .ingredient-container {
            margin-bottom: 20px;
        }
        .ingredient-container input[type="text"],
        .ingredient-container input[type="number"] {
            width: calc(50% - 5px);
            margin-bottom: 10px;
        }
        .ingredient-container button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
        .time-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .time-container input[type="number"] {
            width: calc(10% - 2px);
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
        input[type="submit"] {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Update Recipe</h1>
        <h4>ID: {{recipe_id}}</h4>
        <form action="{{ url_for('recipes.update_recipe_auto_function') }}" method="post">

            <input type="hidden" id="recipeID" name="recipeID" value="{{recipe_id}}">

            <label for="recipeTitle">Recipe Title:</label>
            <input type="text" id="recipeTitle" name="recipeTitle" value="{{recipe_title}}" required>

            <label for="description">Brief Description:</label>
            <textarea id="description" name="description" rows="4" required>{{desc}}</textarea>

            <div class="time-container">
                <label for="cook">Cook Time (in minutes):</label>
                <input type="number" id="cook" name="cook" value="{{cook_time}}" min="1" required>

                <label for="prepTime">Prep Time (in minutes):</label>
                <input type="number" id="prepTime" name="prepTime" value="{{prep_time}}" min="1" required>
            </div>

            <div class="ingredient-container">
                <label>Ingredients:</label>
                <div id="ingredient-fields">
                    {% for ingr in ingredients %}
                    <div>
                        {% set ingredient_name = ingr['Ingredient'] %}
                        {% set ingredient_amount = ingr['Amount'] %}
                        <!-- <input type="text" name="ingredients[]" value="{{ingr['Ingredient']}}" required> -->
                        <select name="ingredients[]" required>
                            {% for option in all_ingredients %}
                                {% set option_name = option['Name'] %}
                                <option value="{{ option }}" {% if option_name == ingredient_name %}selected{% endif %}>{{ option['Name'] }}</option>
                            {% endfor %}
                        </select>
                        <input type="text" name="measurements[]" value="{{ingredient_amount}}" required>
                    </div>
                    {% endfor %}
                </div>
                <button type="button" onclick="addIngredientField()">Add Ingredient</button>
            </div>

            <label for="instructions">Instructions (Enter after each line):</label>
            <textarea id="instructions" name="instructions" rows="8" required>{{instr}}</textarea>

            <input type="submit" value="Update Recipe">
        </form>
    </div>

    <script>
        function addIngredientField() {
            const ingredientFields = document.getElementById('ingredient-fields');
            const div = document.createElement('div');
            div.innerHTML = `
                <select name="ingredients[]" required>
                    {% for option in all_ingredients %}
                        {% set option_name = option['Name'] %}
                        <option value="{{ option }}" {% if option_name == 'almonds' %}selected{% endif %}>{{ option['Name'] }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="measurements[]" placeholder="Measurement" required>
            `;
            ingredientFields.appendChild(div);
        }
    </script>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                                                                               templates/recipespage.html                                                                          0000664 0001750 0001750 00000007625 14612310017 015204  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Login page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            text-align: center;
            padding-top: 100px;
        }
        h1 {
            color: #333;
        }
        .login-form {
            margin-top: 50px;
        }
        .login-form input[type="text"],
        .login-form input[type="password"] {
            width: 250px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .login-form input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .login-form input[type="new"]{
            background-color: #2e46af;
            color: white;
            padding: 10px 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .register-button{
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .card-title {
            color: #333; /* Default color */
            cursor: pointer; /* Change cursor to pointer */
            transition: color 0.3s ease; /* Smooth transition for color change */
        }

        .card-title:hover {
            color: #4CAF50; /* Change color on hover */
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <h1>Recipes</h1>
    <div class="container">
        {% for recipe in recipes %}
        {% if loop.index0 % 3 == 0 %}
        <div class="row">
        {% endif %}
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">

                        <form id="recipeForm{{recipe['Recipe_ID']}}" action="/info_recipe" method="post">
                        <input type="hidden" id="recipeID" name="recipeID" value="{{recipe['Recipe_ID']}}">
                        <input type="hidden" id="recipeTitle" name="recipeTitle" value="{{recipe['Name']}}">
                        <input type="hidden" id="description" name="description" value="{{recipe['Description']}}">
                        <input type="hidden" id="cook" name="cook" value="{{recipe['Cook_Time']}}">
                        <input type="hidden" id="prepTime" name="prepTime" value="{{recipe['Prep_Time']}}">
                        <input type="hidden" id="instructions" name="instructions" value="{{recipe['Instructions']}}">
                        <!-- <input type="hidden" id="wholerow" name="wholerow" value="{{recipe}}"> -->
                        </form>
                        <!-- <a href="#" onclick="document.getElementById('recipeForm{{recipe['Recipe_ID']}}').submit(); return false;">{{recipe["Name"]}}</a> -->


                        <h5 class="card-title" href="#" onclick="document.getElementById('recipeForm{{recipe['Recipe_ID']}}').submit(); return false;">{{ recipe['Name'] }}</h5>
                        <!-- possibly put picture-->
                    </div>
                </div>
            </div>
        {% if loop.index % 3 == 0 or loop.last %}
        </div>
        {% endif %}
        {% endfor %}
    </div>
    <footer>
        <a href="/">Go back to home</a>
        <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                           templates/userinfo.html                                                                             0000664 0001750 0001750 00000004277 14612252756 014566  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>User Profile</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f7f7f7;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            padding: 10px 20px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>User Profile</h1>
        <form action="{{ url_for('user.user_profile') }}" method="post">
            <label for="first_name">First Name:</label>
            <input type="text" id="first_name" name="first_name" value="{{ First_Name }}" >

            <label for="last_name">Last Name:</label>
            <input type="text" id="last_name" name="last_name" value="{{ Last_Name }}">

            <label for="username">Username:</label>
            <input type="text" id="username" name="username" value="{{ Username }}" readonly>

            <label for="password">New Password:</label>
            <input type="password" id="password" name="password" placeholder="Leave blank to keep current password" 
                    value="{{ Password }}">

            <button type="submit">Update Profile</button>
        </form>
    </div>
    <footer>
        <a href="/home">Go back to home</a>
        <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                                                                                 templates/owner_update_admin.html                                                                   0000664 0001750 0001750 00000004363 14612341050 016556  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<head>
    <title>Update Admins</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            
            margin: 0;
            background-color: #f0f0f0;
        }
        form {
            width: 300px;
            margin: 0 auto;
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input[type="text"], input[type="password"], input[type="email"], input[type="checkbox"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
        }
        button[type="submit"] {
            margin-top: 20px;
            padding: 10px;
            width: 100%;
            background-color: #d11414;
            color: white;
            border: none;
            cursor: pointer;
        }
        button[type="submit"]:hover {
            background-color: #0056b3;
        }
        .allergy-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h2>
        Recipe Management Admin Panel
    </h2>
    <h3>
        Change Admin Status
    </h3>
    <form action="{{ url_for('ownerpanel.revoke_admin') }}" method="post" autocomplete="off">
        <label for="username">Remove Admin Role From User:</label>
        <input type="text" id="username" name="username" required>

        <button type="submit" value="Register">Revoke</button>
    </form>
    <form action="{{ url_for('ownerpanel.grant_admin') }}" method="post" autocomplete="off">
        <label for="username">Give Admin Role To User:</label>
        <input type="text" id="username" name="username" required>

        <button type="submit" value="Register">Grant</button>
    </form>
    <p></p>
    <div class="message">{{ message }}</div>
    <footer>
      <a href="/admin_panel">Back to Admin Panel</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                             templates/test_pantry.html                                                                          0000664 0001750 0001750 00000001630 14612116440 015263  0                                                                                                    ustar   aamir                           aamir                                                                                                                                                                                                                  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Recipe Pantry</title>
    <style type="text/css">
        footer {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
    
</head>
<body>
    <h2>{{name}}'s' Pantry</h2>
    <form action="/update_pantry" method="post">
        {% for ingredient in all_ingredients %}
            <div>
                <input type="checkbox" name="ingredients" value="{{ ingredient }}" {% if ingredient in user_ingredients %}checked{% endif %}>
                <label>{{ ingredient }}</label>
            </div>
        {% endfor %}
        <button type="submit">Update</button>
    </form>
    <footer>
      <a href="/home">Go back to home</a>
      <p>&copy; Group 20 Recipe Management System</p>
    </footer>
</body>
</html>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        