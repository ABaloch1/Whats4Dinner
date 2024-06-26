# WHATS4DINNER 
## Recipe Management System with User Pantry

### Description:
    This project is a web application for managing recipes and utilizing a user pantry to filter possible 
    recipes based on available ingredients. Users can browse, search, and manage 
    their pantry inventory. The system also considers allergies and dietary restrictions when providing
    recipe recommendations.

### Problem Statement:
    Cooking enthusiasts often struggle to find recipes based on the ingredients they have on hand, while 
    also considering allergies and dietary restrictions. A recipe management system with a user pantry feature 
    addresses this challenge by providing personalized recipe recommendations that take into account available
    ingredients, allergies, and dietary preferences.

### Division of Labor:
    Ryan Fontaine - User authentication and admin control flask implemtations testing/debugging 
    Aamir Baloch - All html, recipe info and pantry flask integration and program testing/debugging
    Kathryn Trescott - Database setup, role-based access setup and program testing/debugging
    Joshua Krug - Pantry implementation, recipes, ingredients and users flask functions, testing/debugging
    
### Libraries Used:
    Flask: A micro web framework for Python used for developing web applications.
    mysql-connector-python: A MySQL database connector for Python, used for database operations.
    hashlib: A library for secure hash and message digest algorithms, used for password hashing.

### Database:
    MySQL Database: The project uses a MySQL database for storing user information, recipes, pantry inventory,
    allergies, and dietary restrictions. Ensure MySQL server is running and properly configured.

### Installation Instructions:
    Run the following commands to download needed librarys:
    1. apt install mysql-client-core-8.0
    2. pip install flask mysql-connector-python
    3. python3 -m pip install mysql-connector-python
    4. apt-get install mysql-server
    5. apt-get install libmysqlclient-dev

    Then run the following in MySQL before running setup.py:
    1. CREATE USER 'root'@'localhost' IDENTIFIED BY 'root1';
    2. CREATE DATABASE mydatabase;
    3. GRANT ALL ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
    4. GRANT CREATE USER ON *.* TO 'root'@'localhost';
    5. GRANT DROP ROLE ON *.* TO 'root'@'localhost';
    
### User Roles:
    Owner: The owner has the highest level of access and can grant admin privileges to other users.
    Admin: Admin users have administrative privileges and can manage users, recipes, and ingredients.
    User: Regular users can browse, search, and filter recipes, manage their pantry inventory, and set 
     allergies and dietary restrictions.
    Guest: Guests have limited access and can only view recipes.
    
### User Interface:
    Login: Users must authenticate themselves by logging in with their credentials.
    User Profile: After logging in, users can manage their profile settings, view their pantry inventory, 
     and set their allergies and dietary restrictions.
    Recipe Browse/Search: Users can browse recipes, search for specific recipes, and view detailed recipe information.
    Pantry Management: Users can add or remove items in their pantry inventory.
    Filter Recipes by Pantry: Users can filter recipes based on the ingredients available in their pantry, 
     while also considering allergies and dietary restrictions.

### Known Bugs:
    1. Button to submit pantry is not working, it doesn't save the user's pantry, 
        leading to no recipes being suggested.
    2. Selecting Tree Nuts allergy may break something
     
### Extra Features Implemented:
    Session Management: User sessions are managed to authenticate users and restrict access to certain pages,
    such as the admin page or the profiles page.
    
### Setup.py and Reset_db.py
    We have some hardcoded users and values written into the tables in the setup.py in order to make testing our 
    website easier. We have an owner-'mrkrabs', and a guest-'group20'. Reset_db.py is created for the convenience 
    of clearing out the users, tables, and roles that were created in the setup.py or in the website.
    
## Notes 
    If you navigate to the "Show Recipes" page at the top of the navigation ribbon as a logged in user, the 
    "Go back to home page" takes you back to the home page for a guest. If you click "login", it'll take you 
    back to your logged in home page.
    
