from flask import Flask
import mysql.connector

app = Flask(__name__)

from flask_mysqldb import MySQL

config = {
	'user': 'rose',
	'password': 'rose',
	'host': 'localhost',
	'database': 'mydatabase',
}

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
