#Timestamp: 4/22 6pm

import mysql.connector
#from PopIngredients import popingredients 

"""
BEFORE RUNNING:
Create the owner user: CREATE USER 'root'@'localhost' IDENTIFIED BY 'root1';
Create database: CREATE DATABASE mydatabase;
Give all permissions: GRANT ALL ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
Grant create user: GRANT CREATE USER ON *.* TO 'root'@'localhost';
Grant drop role: GRANT DROP ROLE ON *.* TO 'root'@'localhost';
"""

config = {
	'user': 'root',
	'password': 'root1',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()
#cur.execute("CREATE DATABASE mydatabase")

#User Table
cur.execute( '''
	CREATE TABLE Users (
		Username varchar(50) NOT NULL,
		Password varchar(256) NOT NULL,
  		First_Name varchar(50) NOT NULL,
		Last_Name varchar(100) NOT NULL,
		PRIMARY KEY (Username)
	)
''')

#Allergens Table
cur.execute( '''
	CREATE TABLE Allergens (
		Name varchar(50) NOT NULL,
		Primary KEY(Name)
	)
''')

#Ingredients Table
cur.execute('''
	CREATE TABLE Ingredients (
		Name varchar(50) NOT NULL,
		Allergy_Category varchar(50) NULL,
		Category varchar(50) NOT NULL,
		CONSTRAINT fk_all FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT UK_Ingredients UNIQUE KEY (Name, Allergy_Category, Category)
		)
''')

#User Pantry Table
cur.execute( '''
	CREATE TABLE User_Pantry (
		Username varchar(50) NOT NULL,
		Ingredient varchar(50) NOT NULL,
		CONSTRAINT fk_users FOREIGN KEY (Username) REFERENCES Users(Username) ON DELETE CASCADE,
		CONSTRAINT fk_ingr FOREIGN KEY (Ingredient) REFERENCES Ingredients(Name) ON DELETE CASCADE,
		CONSTRAINT PK_UserIng PRIMARY KEY (Username, Ingredient)
	)
''')

#User Allergens Table
cur.execute( '''
	CREATE TABLE User_Allergens (
		Username varchar(50) NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		CONSTRAINT fk_user FOREIGN KEY (Username) REFERENCES Users(Username) ON DELETE CASCADE,
		CONSTRAINT fk_aller FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT UK_UserAllergy UNIQUE KEY (Username, Allergy_Category)
	)
''')

#Recipes Table
cur.execute( '''
	CREATE TABLE Recipes (
		Recipe_ID INT AUTO_INCREMENT,
		Name varchar(50) NOT NULL,
		Category varchar(50) NOT NULL,
  		Description TEXT NULL,
    		Prep_Time INT NULL,
      		Cook_Time INT NULL,
		Instructions TEXT NOT NULL,
		PRIMARY KEY (Recipe_ID)
	)
''')

#Recipe Ingredient Table
cur.execute( '''
	CREATE TABLE Recipe_Ingredients (
		Recipe_ID INT NOT NULL,
		Ingredient varchar(50) NOT NULL,
		Amount varchar(15)  NOT NULL,
		CONSTRAINT fk_RIID FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE,
		CONSTRAINT fk_Ing FOREIGN KEY (Ingredient) REFERENCES Ingredients(Name) ON DELETE CASCADE,
		CONSTRAINT PK_RecipeIng PRIMARY KEY (Recipe_ID, Ingredient, Amount)
	)
''')

#Recipe Allergens Table
cur.execute( '''
	CREATE TABLE Recipe_Allergens (
		Recipe_ID INT NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		CONSTRAINT fk_RID FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE,
		CONSTRAINT fk_allergy FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT UK_RecipeAllergy UNIQUE KEY (Recipe_ID, Allergy_Category)
	)
''')

print('Created tables')

#popingredients()

#do privileges setup
cur.execute("CREATE USER 'group20'@'localhost' IDENTIFIED BY 'group20'")
cur.execute("CREATE ROLE 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipes TO 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Ingredients TO 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Allergens TO 'Guest'")
cur.execute("GRANT SELECT, INSERT ON mydatabase.User_Allergens TO 'Guest'")
cur.execute("GRANT SELECT, INSERT ON mydatabase.Users TO 'Guest'")
cur.execute("GRANT 'Guest' TO 'group20'@'localhost'")
cur.execute("SET DEFAULT ROLE 'Guest' TO 'group20'@'localhost'")

cur.execute("CREATE ROLE 'member'")
cur.execute("GRANT SELECT on mydatabase.Recipes TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Ingredients TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Allergens TO 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Users TO 'member'")
cur.execute("GRANT UPDATE(Password, First_Name, Last_Name) ON mydatabase.Users TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.User_Pantry TO 'member'")
cur.execute("GRANT Update(Ingredient) ON mydatabase.User_Pantry TO 'member'")
cur.execute("GRANT DELETE ON mydatabase.User_Pantry TO 'member'")
cur.execute("GRANT SELECT ON mydatabase.User_Allergens TO 'member'")
cur.execute("GRANT Update(Allergy_Category) ON mydatabase.User_Allergens TO 'member'")
cur.execute("GRANT DELETE ON mydatabase.User_Pantry TO 'member'")

cur.execute("CREATE ROLE 'admin'")
cur.execute("GRANT SELECT, UPDATE, DELETE ON mydatabase.Users TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Allergens TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Ingredients TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipes TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipe_Ingredients TO 'admin'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipe_Allergens TO 'admin'")

cur.execute("CREATE USER 'mrkrabs'@'localhost' IDENTIFIED BY '35df8167b065b3a7e929a9712fe5164b42282f5edc215fce95baea8ae80fc9df'")
cur.execute("INSERT INTO Users (Username, Password, First_Name, Last_Name) VALUES ('mrkrabs', '35df8167b065b3a7e929a9712fe5164b42282f5edc215fce95baea8ae80fc9df', 'Eugene', 'Krabs')")
cur.execute("GRANT ALL ON mydatabase.* TO 'mrkrabs'@'localhost'")
cur.execute("GRANT 'admin' TO 'mrkrabs'@'localhost' WITH ADMIN OPTION")

cur.execute("FLUSH PRIVILEGES")
print("created roles, owner, and group20")
cnx.commit()
# database.commit() unsure if line is needed, i dont think it is
cur.close()
cnx.close()
