#need to run "pip install flask mysql-connector-python"
import mysql.connector

#change to fit your user, password, and database name
config = {
	'user': 'rose',
	'password': 'rose',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS mydatabase")

#User Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS Users (
		Username varchar(50) NOT NULL,
		Ingredient_Name varchar(50) NOT NULL,
		Recipe_Name varchar(50) NOT NULL,
		Email varchar(50) NOT NULL,
		Password varchar(50) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#Recipe Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS Recipes (
		Recipe_Name varchar(50) NOT NULL,
		Username varchar(50) NOT NULL,
		Ingredient_Name varchar(50) NOT NULL,
		Category varchar(50) NOT NULL,
		PRIMARY KEY (Recipe_Name)
	)
''')

#Ingredient Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS Recipes (
		Ingredient_Name varchar(50) NOT NULL,
		Recipe_Name varchar(50) NOT NULL,
		Username varchar(50) NOT NULL,
		Food_Category varchar(50) NOT NULL,
		PRIMARY KEY (Ingredient_Name)
	)
''')

print('Created tables')
# database.commit() unsure if line is needed, i dont think it is
cur.close()
cnx.close()
