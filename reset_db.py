#Timestamp: 4/21 7:11pm

import mysql.connector

#change to fit your user, password, and database name
config = {
	'user': 'owner',
	'password': 'owner',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()
cur.execute("SET foreign_key_checks=0")
cur.execute("DROP USER 'group20'@'localhost'")
cur.execute("DROP ROLE 'admin', 'member', 'Guest'")

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
