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
cur = cnx.cursor()

user = Blueprint('user', __name__, template_folder='templates')

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

@user.route('/admin_panel/update_user')
def update_user_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/update_user.html')

    message = ''
    return render_template('register.html', message='')

@user.route('/admin_panel/update_user_function', methods=['GET', 'POST'])
def update_user_function():

    if session['role'] != 'admin':
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

@user.route('/admin_panel/delete_user')
def delete_user_page():

    if session['role'] != 'admin':
        return render_template('home.html', username=session['username']+'. You are not admin')

    # If the user is already logged in, redirect
    if 'loggedin' in session:
        return render_template('admin_panel/delete_user.html')

    message = ''
    return render_template('register.html', message='')


@user.route('/admin_panel/delete_user_function', methods=['GET', 'POST'])
def delete_user_function():

    if session['role'] != 'admin':
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
