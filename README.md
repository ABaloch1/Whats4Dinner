# Recipe Management System with User Pantry

## Description:
    This project is a web application for managing recipes and utilizing a user pantry to filter possible 
    recipes based on available ingredients. Users can browse, search, and save recipes, as well as manage 
    their pantry inventory. The system also considers allergies and dietary restrictions when providing
    recipe recommendations.

## Problem Statement:
    Cooking enthusiasts often struggle to find recipes based on the ingredients they have on hand, while 
    also considering allergies and dietary restrictions. A recipe management system with a user pantry feature 
    addresses this challenge by providing personalized recipe recommendations that take into account available
    ingredients, allergies, and dietary preferences.

## Division of Labor:
    Ryan Fontaine - User authentication and admin control flask implementations and html testing/debugging 
    Aamir Baloch - All other html, recipe info flask implementation and program testing/debugging
    Kathryn Trescott - Database setup, roll-based access setup and program testing/debugging
    Joshua Krug - Pantry flask implementation, ingredient, and user flask functions, testing/debugging
    
## User Roles:
    Owner: The owner has the highest level of access and can grant admin privileges to other users.
    Admin: Admin users have administrative privileges and can manage users, recipes, and ingredients.
    User: Regular users can browse, search, and filter recipes, manage their pantry inventory, and set 
            allergies and dietary restrictions.
    Guest: Guests have limited access and can only view recipes.
    
## User Interface Instructions:
    Login: Users must authenticate themselves by logging in with their credentials.
    User Profile: After logging in, users can manage their profile settings, view their pantry inventory, 
                    and set their allergies and dietary restrictions.
    Recipe Browse/Search: Users can browse recipes, search for specific recipes, and view detailed recipe information.
    Pantry Management: Users can add or remove items in their pantry inventory.
    Filter Recipes by Pantry: Users can filter recipes based on the ingredients available in their pantry, 
                                while also considering allergies and dietary restrictions.

## Libraries Used:
    Flask: A micro web framework for Python used for developing web applications.
    mysql-connector-python: A MySQL database connector for Python, used for database operations.
    hashlib: A library for secure hash and message digest algorithms, used for password hashing.

## Database:
    MySQL Database: The project uses a MySQL database for storing user information, recipes, pantry inventory,
    allergies, and dietary restrictions. Ensure MySQL server is running and properly configured.

## Extra Features Implemented:
    Pantry Integration: Users can manage their pantry inventory and filter recipes based on available ingredients, 
                            allergies, and dietary restrictions.
    Error Handling: Comprehensive error handling to manage exceptions and provide meaningful error messages to users.
    Session Management: User sessions are managed to authenticate users and restrict access to profile pages.
