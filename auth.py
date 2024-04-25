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
        owner = False
        if session['role'] == 'owner':
            owner = True
        return render_template('admin_panel/adminpanel.html', owner=owner)

    message = ''
    return render_template('register.html', message='')

# ---
