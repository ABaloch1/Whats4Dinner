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
    return redirect(url_for('login'))


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
    return redirect(url_for('auth.login'))


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
                return redirect(url_for('auth.login'))
            except:
                cnx.rollback()
                msg = 'Something happenend. Database rolling back.'
            # --

            msg = 'Success! Account registered!'
            return redirect(url_for('auth.home'))

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