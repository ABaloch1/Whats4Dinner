#need to run "pip install flask mysql-connector-python"
import mysql.connector

#change to fit your user, password, and database name
config = {
	'user': 'group20',
	'password': 'group20',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS mydatabase")

#User Table
cur.execute( '''
	DROP TABLE IF EXISTS Users
''')

cur.execute( '''
	DROP TABLE IF EXISTS User_Pantry
''')

cur.execute( '''
	DROP TABLE IF EXISTS User_Allergens
''')

cur.execute( '''
	DROP TABLE IF EXISTS Recipes
''')

cur.execute( '''
	DROP TABLE IF EXISTS Recipe_Ingredients
''')

cur.execute( '''
	DROP TABLE IF EXISTS Recipe_Allergens
''')

cur.execute( '''
	DROP TABLE IF EXISTS Ingredients
''')

print('No more tables')

cur.close()
cnx.close()
