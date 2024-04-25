from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
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
            cur = cnx.cursor(dictionary=True)

            cur.execute("SELECT FROM_USER FROM mysql.role_edges WHERE TO_USER = %s", (session['username'],))
            role = cur.fetchone()
            session['role'] = role['FROM_USER']
            print(session['role'])
            cur.close()
            cnx.close()

            config = {
                'user': session['username'],
                'password': password,
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

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    if 'loggedin' in session:
        return render_template('admin_panel/adminpanel.html')

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/list_recipes',methods = ['POST', 'GET'])
def list_recipes_page():
    if session['role'] != 'admin':
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

@auth.route('/admin_panel/create_recipe')
def create_recipe_page():
    if session['role'] != 'admin':
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


@auth.route('/admin_panel/create_recipe_function', methods=['GET', 'POST'])
def create_recipe_function():
    if session['role'] != 'admin':
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


@auth.route('/admin_panel/update_recipe_auto_page', methods=['GET', 'POST'])
def update_recipe_auto_page():
    if session['role'] != 'admin':
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

@auth.route('/admin_panel/update_recipe_auto_function', methods=['GET', 'POST'])
def update_recipe_auto_function():
    if session['role'] != 'admin':
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

@auth.route('/admin_panel/update_recipe')
def update_recipe_page():
    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return redirect( url_for('auth.list_recipes_page'))

    message = ''
    return render_template('register.html', message='')


@auth.route('/admin_panel/delete_recipe')
def delete_recipe_page():
    if session['role'] != 'admin':
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

@auth.route('/admin_panel/delete_recipe_function', methods=['GET', 'POST'])
def delete_recipe_function():
    if session['role'] != 'admin':
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

    return render_template('login.html', message=msg)

# ---
