from flask import Flask
import mysql.connector

app = Flask(__name__)

from flask_mysqldb import MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hi'
app.config['MYSQL_DB'] = 'Whats4Database'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
