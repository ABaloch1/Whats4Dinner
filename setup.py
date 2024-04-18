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
	CREATE TABLE IF NOT EXISTS Users (
		Username varchar(50) NOT NULL,
		Password varchar(256) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#User Pantry Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS User_Pantry (
		Username varchar(50) NOT NULL,
		Ingredient varchar(50) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#User Allergens Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS User_Allergens (
		Username varchar(50) NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#Recipes Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS Recipes (
		ID INT AUTO_INCREMENT,
		Name varchar(50) NOT NULL,
		Category varchar(50) NOT NULL,
		PRIMARY KEY (ID)
	)
''')

#Recipe Ingredient Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
		ID INT NOT NULL,
		Ingredient varchar(50) NOT NULL,
		Amount INT NOT NULL,
		PRIMARY KEY (ID)
	)
''')

#Recipe Allergens Table
cur.execute( '''
	CREATE TABLE IF NOT EXISTS Recipe_Allergens (
		ID INT NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		PRIMARY KEY (ID)
	)
''')

# #Recipe Table
# cur.execute( '''
# 	CREATE TABLE IF NOT EXISTS Recipes (
# 		Recipe_Name varchar(50) NOT NULL,
# 		Username varchar(50) NOT NULL,
# 		Ingredient_Name varchar(50) NOT NULL,
# 		Category varchar(50) NOT NULL,
# 		PRIMARY KEY (Recipe_Name)
# 	)
# ''')

# #Ingredient Table
# cur.execute( '''
# 	CREATE TABLE IF NOT EXISTS Recipes (
# 		Ingredient_Name varchar(50) NOT NULL,
# 		Recipe_Name varchar(50) NOT NULL,
# 		Username varchar(50) NOT NULL,
# 		Food_Category varchar(50) NOT NULL,
# 		PRIMARY KEY (Ingredient_Name)
# 	)
# ''')


print('Created tables')
# database.commit() unsure if line is needed, i dont think it is
cur.close()
cnx.close()
