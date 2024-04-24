from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
import mysql.connector
import hashlib

secret_key = 'this is our top secret super key that definitely isn\'t going to be uploaded to our GitHub page'

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
                hashed_password = hashlib.sha256((password + secret_key).encode()).hexdigest()
                cur.execute("UPDATE Users SET First_Name = %s, Last_Name = %s, Password = %s WHERE Username = %s", (first_name, last_name, hashed_password, session['username']))
            else:
                cur.execute("UPDATE Users SET First_Name = %s, Last_Name = %s WHERE Username = %s", (first_name, last_name, session['username']))
            cnx.commit()
            return redirect(url_for('user.user_profile'))
    except mysql.connector.Error as err:
        cnx.rollback()
        return "Error: {}".format(err)
    return redirect(url_for('user.user_profile'))
