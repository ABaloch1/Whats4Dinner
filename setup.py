#need to run "pip install flask mysql-connector-python"
import mysql.connector

database = mysql.connector.connect(
	host = 'localhost',
	user = 'root',
	password = 'hi',
	database = 'Whats4Database'
)
print ('Opened database successfully')
cursor = database.cursor()

#User Table
cursor.execute( '''
	CREATE TABLE Users (
		Username varchar(50) NOT NULL,
		Ingredient_Name varchar(50) NOT NULL,
		Recipe_Name varchar(50) NOT NULL,
		Email varchar(50) NOT NULL,
		Password varchar(50) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#Recipe Table
cursor.execute( '''
	CREATE TABLE Recipes (
		Recipe_Name varchar(50) NOT NULL,
		Username varchar(50) NOT NULL,
		Ingredient_Name varchar(50) NOT NULL,
		Category varchar(50) NOT NULL,
		PRIMARY KEY (Recipe_Name)
	)
''')

#Ingredient Table
cursor.execute( '''
	CREATE TABLE Recipes (
		Ingredient_Name varchar(50) NOT NULL,
		Recipe_Name varchar(50) NOT NULL,
		Username varchar(50) NOT NULL,
		Food_Category varchar(50) NOT NULL,
		PRIMARY KEY (Ingredient_Name)
	)
''')

print('Created tables')

database.commit()
cursor.close()
database.close()

