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

user = Blueprint('user', __name__, template_folder='templates')

@user.route('/user_profile', methods=['GET', 'POST'])
def user_profile(name):
    try:
        if request.method == 'GET':
            cur.execute("SELECT * FROM Users WHERE Username = ?", (session[username],))
            user_data = cur.fetchone()
            return render_template('profile.html', user_data=user_data)
        elif request.method == 'POST':
            first_name = request.form['first_name'],
            last_name = request.form['last_name']
            password = request.form['password']

            hashed_password = password + secret_key
            hashed_password = hashlib.sha256(hashed_password.encode())
            password = hashed_password.hexdigest()

            cur.execute("UPDATE Users SET First_Name = %s, Last_Name = %s, password = %s",(first_name, last_name, password))
            cnx.commit()
    except:
        cnx.rollback()
        return render_template('profile.html')
    return redirect(url_for('user_profile'))
