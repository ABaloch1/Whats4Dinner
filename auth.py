from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
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

        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password,))

        account = cur.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['Username']

            try:
                cur.execute(
                    "SELECT First_Name, Last_Name FROM Users WHERE Username = %s", (session['username'],))
                row = cur.fetchone()
                session['firstName'] = row['First_Name']
                session['lastName'] = row['Last_Name']
            except:
                session['firstName'] = 'ERROR'
                session['lastName'] = 'ERROR'

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
    return render_template('login.html') #redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

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

            try:
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

                msg = 'Success! Account registered!'
                return render_template('login.html', message=msg) #redirect(url_for('auth.login'))
            except:
                cnx.rollback()
                msg = 'Something happenend. Database rolling back.'
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

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/adminpanel.html')

    message = ''
    return render_template('register.html', message='')

# ---

@auth.route('/admin_panel/update_user')
def update_user_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_user.html')

    message = ''
    return render_template('register.html', message='')

@auth.route('/admin_panel/update_user_function', methods=['GET', 'POST'])
def update_user_function():

    msg = ''
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        password = request.form['password']

        cur = cnx.cursor(dictionary=True)

        if password:
            hashed_password = password + secret_key
            hashed_password = hashlib.sha256(hashed_password.encode())

            password = hashed_password.hexdigest()

            try:
                cur.execute("UPDATE Users SET Password = %s WHERE Username = %s;", (password, username,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_user.html', message = "Error. Had to roll back.")
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

@auth.route('/admin_panel/delete_user')
def delete_user_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_user.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/delete_user_function', methods=['GET', 'POST'])
def delete_user_function():

    msg = ''
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']

        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("DELETE FROM Users WHERE Username = %s;", (username,))
            cnx.commit() 
        except:
            cnx.rollback()
            return render_template('admin_panel/delete_user.html', message = "Error. Had to roll back.")

        return render_template('admin_panel/delete_user.html', message = "Deleted {}".format(username))

    return render_template('login.html', message=msg)


# ---

@auth.route('/admin_panel/create_ingredient')
def create_ingredient_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/create_ingredient.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/create_ingredient_function', methods=['GET', 'POST'])
def create_ingredient_function():

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        restriction_category = request.form['category']

        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("INSERT INTO Ingredients (Name, Allergy_Category, Category) VALUES (%s, %s, %s);", (ingredient_name, allergy_category, restriction_category))
            cnx.commit()        
        except:
            cnx.rollback()
            return render_template('admin_panel/create_ingredient.html', message = "Duplicate entry.")

        return render_template('/admin_panel/create_ingredient.html', message = "Added {}".format(ingredient_name))

    return render_template('login.html', message=msg)


# ---

@auth.route('/admin_panel/update_ingredient')
def update_ingredient_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_ingredient.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/update_ingredient_function', methods=['GET', 'POST'])
def update_ingredient_function():

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        restriction_category = request.form['category']

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

        if restriction_category:
            try:
                cur.execute("UPDATE Ingredients SET Category = %s WHERE Name = %s;", (restriction_category, ingredient_name,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass



        return render_template('admin_panel/update_ingredient.html', message = "Updated {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---


@auth.route('/admin_panel/delete_ingredients')
def delete_ingredients_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_ingredient.html')

    message = ''
    return render_template('register.html', message='')

@auth.route('/admin_panel/delete_ingredient_function', methods=['GET', 'POST'])
def delete_ingredient_function():

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']

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

@auth.route('/admin_panel/create_allergen')
def create_allergens_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/create_allergen.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/create_allergen_function', methods=['GET', 'POST'])
def create_allergen_function():

    msg = ''
    if request.method == 'POST' and 'allergenName' in request.form:
        allergen_name = request.form['allergenName']

        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("INSERT INTO Allergens (Name) VALUES (%s);", (allergen_name,))
            cnx.commit()        
        except:
            cnx.rollback()
            return render_template('admin_panel/create_allergen.html', message = "Error. Had to roll back.")


        return render_template('/admin_panel/create_allergen.html', message = "Craeted {}".format(allergenName))

    return render_template('login.html', message=msg)

# ---

@auth.route('/admin_panel/delete_allergen')
def delete_allergens_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_allergen.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/delete_allergen_function', methods=['GET', 'POST'])
def delete_allergens_function():

    msg = ''
    if request.method == 'POST' and 'allergenName' in request.form:
        allergen_name = request.form['allergenName']

        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("DELETE FROM Allergens WHERE Name = %s;", (allergen_name,))
            cnx.commit() 
        except:
            cnx.rollback()
            return render_template('admin_panel/delete_allergen.html', message = "Error. Had to roll back.")

        return render_template('admin_panel/delete_allergen.html', message = "Deleted {}".format(allergen_name))

    return render_template('login.html', message=msg)

# ---

@auth.route('/admin_panel/list_user',methods = ['POST', 'GET'])
def list_user_page():
    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:

            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Users;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_users.html",rows = rows)
        except:
            return render_template("admin_panel/list_users.html",rows = [])
    return render_template("register.html", message='Not authorized')



@auth.route('/admin_panel/list_allergens',methods = ['POST', 'GET'])
def list_allergens_page():
    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:

            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Allergens;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_allergens.html",rows = rows)
        except:
            return render_template("admin_panel/list_allergens.html",rows = [])
    return render_template("register.html", message='Not authorized')




@auth.route('/admin_panel/list_ingredients',methods = ['POST', 'GET'])
def list_ingredients_page():
    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:

            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Ingredients;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_ingredients.html",rows = rows)
        except:
            return render_template("admin_panel/list_ingredients.html",rows = [])
    return render_template("register.html", message='Not authorized')




@auth.route('/admin_panel/list_recipes',methods = ['POST', 'GET'])
def list_recipes_page():
    # If the user is already logged in, redirect
    if 'loggedin' in session:
        try:

            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Recipes;")
            rows = cur.fetchall()

            return render_template("admin_panel/list_recipes.html",rows = rows)
        except:
            # return render_template("admin_panel/list_recipes.html",rows = [])
            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT * FROM Recipes;")
            rows = cur.fetchall()
            return render_template("admin_panel/list_recipes.html",rows = rows)
    return render_template("register.html", message='Not authorized')


# ---

@auth.route('/admin_panel/create_recipe')
def create_recipe_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('recipe.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/create_recipe_function', methods=['GET', 'POST'])
def create_recipe_function():

    if request.method == 'POST' and 'recipeTitle' in request.form:
        # print(request)
        recipeTitle = request.form['recipeTitle']
        description = request.form['description']
        cook_time = request.form['cook']
        prep_time = request.form['prepTime']
        instructions = request.form['instructions']

        ingredients = request.form.getlist('ingredients[]')
        measurements = request.form.getlist('measurements[]')

        cur = cnx.cursor(dictionary=True)

        try:
            cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions VALUES (%s, %s, %s, %s, %s, %s);", (recipeTitle, "Temp", description, prep_time, cook_time, instructions))
            cnx.commit()        
        except:
            # cnx.rollback()
            # return redirect('/admin_panel/create_recipe')
            cur.execute("INSERT INTO Recipes (Name, Category, Description, Prep_Time, Cook_Time, Instructions) VALUES (%s, %s, %s, %s, %s, %s);", (recipeTitle, "Temp", description, prep_time, cook_time, instructions))
            cnx.commit()  

        return redirect('/admin_panel/list_recipes')

    msg = ''
    return render_template('login.html', message=msg)


@auth.route('/admin_panel/update_recipe_auto_page', methods=['GET', 'POST'])
def update_recipe_auto_page():
    if request.method == 'POST' and 'recipeTitle' in request.form:
        recipe_title = request.form['recipeTitle']
        description = request.form['description']
        cook_time = request.form['cook']
        prep_time = request.form['prepTime']
        instructions = request.form['instructions']

        recipe_id = request.form['recipeID']

        return render_template('/admin_panel/update_recipe_auto.html', recipe_title=recipe_title, desc=description, cook_time=cook_time, prep_time=prep_time, instr=instructions, recipe_id=recipe_id)
    else:
        # Return a response indicating that the request was not processed as expected
        return "Something went wrong", 400

@auth.route('/admin_panel/update_recipe_auto_function', methods=['GET', 'POST'])
def update_recipe_auto_function():
    if request.method == 'POST' and 'recipeTitle' in request.form:
        recipe_title = request.form['recipeTitle']
        description = request.form['description']
        cook_time = request.form['cook']
        prep_time = request.form['prepTime']
        instructions = request.form['instructions']

        recipe_id = request.form['recipeID']

        cur = cnx.cursor(dictionary=True)

        if description and cook_time and prep_time and instructions:
            try:
                cur.execute("UPDATE Recipes SET Name = %s, Description = %s, Cook_Time = %s, Prep_Time = %s, Instructions = %s WHERE Recipe_ID = %s;", (recipe_title, description, cook_time, prep_time, instructions, recipe_id))
                cnx.commit()
                return redirect('/admin_panel/list_recipes')
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass


        return render_template('/admin_panel/update_recipe_auto.html', recipe_title=recipe_title, desc=description, cook_time=cook_time, prep_time=prep_time, instr=instructions)
    else:
        # Return a response indicating that the request was not processed as expected
        return "Something went wrong", 400



# ---

@auth.route('/admin_panel/update_recipe')
def update_recipe_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_ingredient.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/update_recipe_function', methods=['GET', 'POST'])
def update_recipe_function():

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']
        allergy_category = request.form['allergyCategory']
        restriction_category = request.form['category']

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

        if restriction_category:
            try:
                cur.execute("UPDATE Ingredients SET Category = %s WHERE Name = %s;", (restriction_category, ingredient_name,))
                cnx.commit() 
            except:
                cnx.rollback()
                return render_template('admin_panel/update_ingredient.html', message = "Error. Had to roll back.")
        else:
            pass



        return render_template('admin_panel/update_ingredient.html', message = "Updated {}".format(ingredient_name))

    return render_template('login.html', message=msg)

# ---


@auth.route('/admin_panel/delete_recipe')
def delete_recipe_page():

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_ingredient.html')

    message = ''
    return render_template('register.html', message='')

@auth.route('/admin_panel/delete_recipe_function', methods=['GET', 'POST'])
def delete_recipe_function():

    msg = ''
    if request.method == 'POST' and 'ingredientName' in request.form:
        ingredient_name = request.form['ingredientName']

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