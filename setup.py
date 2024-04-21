#need to run "pip install flask mysql-connector-python"
import mysql.connector
"""
BEFORE RUNNING:
Create the owner user: CREATE USER 'owner'@'localhost' IDENTIFIED BY 'owner';
"""
#change to fit your user, password, and database name
config = {
	'user': 'owner',
	'password': 'owner',
	'host': 'localhost',
	'database': 'mydatabase',
}

cnx = mysql.connector.connect(**config)
cur = cnx.cursor()
cur.execute("CREATE DATABASE mydatabase")
cur.execute("GRANT ALL ON mydatabase.* TO 'owner'@'localhost'")

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
		PRIMARY KEY(Name)
	)
''')

#Ingredients Table
cur.execute('''
	CREATE TABLE Ingredients (
		Name varchar(50) NOT NULL,
		Allergy_Category varchar(50) NOT NULL,
		Category varchar(50) NOT NULL,
		CONSTRAINT fk_all FOREIGN KEY (Allergy_Category) REFERENCES Allergens(Name) ON DELETE CASCADE,
		CONSTRAINT PK_Ingredients PRIMARY KEY (Name, Allergy_Category, Category)
		)
''')

#User Pantry Table
cur.execute( '''
	CREATE TABLE User_Pantry (
		Username varchar(50) NOT NULL,
		Ingredient varchar(50) NOT NULL,
		CONSTRAINT fk_users FOREIGN KEY (Username) REFERENCES Users(Username) ON DELETE CASCADE,
		CONSTRAINT fk_ing FOREIGN KEY (Ingredient) REFERENCES Ingredients(Name) ON DELETE CASCADE,
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
		CONSTRAINT PK_UserAllergy PRIMARY KEY (Username, Allergy_Category)
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
		CONSTRAINT PK_RecipeAllergy PRIMARY KEY (Recipe_ID, Allergy_Category)
	)
''')

print('Created tables')

#do privileges and guest setup
cur.execute("CREATE USER 'group20'@'localhost' IDENTIFIED BY 'group20'")
cur.execute("CREATE ROLE 'Guest'")
cur.execute("GRANT SELECT ON mydatabase.Recipes TO 'group20'@'localhost'")
cur.execute("GRANT SELECT ON mydatabase.Recipe_Ingredients TO 'group20'@'localhost'")
cur.execute("SET DEFAULT ROLE 'Guest' TO 'group20'@'localhost'")
cur.execute("CREATE ROLE 'admin'")
cur.execute("GRANT SELECT, UPDATE, DELETE ON mydatabase.Users TO 'admin'@'localhost'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Allergens TO 'admin'@'localhost'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Ingredients TO 'admin'@'localhost'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipes TO 'admin'@'localhost'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipe_Ingredients TO 'admin'@'localhost'")
cur.execute("GRANT SELECT, UPDATE, INSERT, DELETE ON mydatabase.Recipe_Allergens TO 'admin'@'localhost'")
cur.execute("GRANT ‘admin’@’localhost’ TO ‘owner’@’localhost’ WITH ADMIN OPTION")


# database.commit() unsure if line is needed, i dont think it is
cur.close()
cnx.close()
