#Timestamp: 4/21 8:16pm

import mysql.connector

#change to fit your user, password, and database name
config = {
	'user': 'root',
	'password': 'root1',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor(dictionary=True)
cur.execute("SET foreign_key_checks=0")
cur.execute("DROP USER IF EXISTS 'group20'@'localhost'")
cur.execute("DROP USER IF EXISTS 'mrkrabs'@'localhost'")
cur.execute("DROP ROLE IF EXISTS 'admin'")
cur.execute("DROP ROLE IF EXISTS 'member'")
cur.execute("DROP ROLE IF EXISTS'Guest'")
cur.execute("SELECT Username FROM Users")
users = cur.fetchall()
for user in users:
	cur.execute("DROP USER IF EXISTS %s@'localhost'", (user['Username'],))


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
cur.execute( '''
	DROP TABLE IF EXISTS Allergens
''')
print('No more tables')

cur.close()
cnx.close()
