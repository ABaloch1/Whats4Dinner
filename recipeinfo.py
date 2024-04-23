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

@recipesinfo.route('/recipesinfo', methods=['GET', 'POST'])
def recipesinfo_page():
    if request.method == "POST":
        
