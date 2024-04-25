from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
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
    cur = cnx.cursor()

@ownerpanel.route('/owner/update_admin_page')
def update_admin_page():
	update_config()
    if session['role'] != 'owners':
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

        return render_template('owner_update_admin.html')

    return render_template('/')








@ownerpanel.route('/owner/revoke_admin', methods=['GET', 'POST'])
def revoke_admin():
	update_config()
	if session['role'] != 'owner':
        return render_template('home.html', username=session['username']+'. Not Owner. You must be a Eugene imposter')
    
    if request.method == 'POST' and 'username' in request.form:
    	username = request.form['username']

        global config
        cnx = mysql.connector.connect(**config)
        cur = cnx.cursor(dictionary=True)

        cur.execute("REVOKE 'admin' FROM %s@'localhost';", (username,))
        cnx.commit() 

        cur.execute("FLUSH PRIVILEGES;")
        cnx.commit()

        return render_template('owner_update_admin.html')

    return render_template('/')