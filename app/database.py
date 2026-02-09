"""
database.py

This module sets up the database connection and defines the main tables
for the Financial Transaction Engine project.

Module Purpose:
Establish a connection to the database.
Define all necessary tables for the project.
Provide a clear structure for managing users, financial data, transaction history, and security.
Tables:

Users:
    The primary table in the system.
    Stores essential user information: ID, name, surname, email, and phone.
    Other tables reference Users to link data to specific users.

Finances:
    Stores user financial data, such as account balances and transactions.
    Connected to the Users table to identify the owner of the data.
    Useful for tracking and reporting financial activity.

History:
    Logs all transactions and actions performed in the system.
    Each entry usually references a user and a transaction.
    Helps with auditing and maintaining accountability.

Security:
    Stores security-related data such as hashed passwords, login attempts, and authentication tokens.
    Ensures user accounts are protected and system integrity is maintained.
    Crucial for login and access control mechanisms.


Notes for Developers:
Users is the main table; other tables should reference it whenever possible.
Keep this documentation updated when adding new tables or fields.
Ensure consistency of relationships between tables when modifying schema.
"""


from app.config import mydb



mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE Financial_Transaction_Engine_System")

mycursor.execute("USE Financial_Transaction_Engine_System")
mycursor.execute("CREATE TABLE users("
                    "id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,"
                    "name VARCHAR(50) NOT NULL,"
                    "surname VARCHAR(50) NOT NULL,"
                    "birth_date VARCHAR(20),"
                    "email VARCHAR(50) NOT NULL,"
                    "phone VARCHAR(15) NOT NULL,"
                    "role VARCHAR(15) DEFAULT 'user' "
                 ");"
                 )
mycursor.execute("CREATE TABLE finances("
                    "id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,"
                    "user_id INT NOT NULL,"
                    "card_number BIGINT NOT NULL,"
                    "balance BIGINT DEFAULT 0,"
                    "FOREIGN KEY (user_id) REFERENCES users(id)"
                 ");"
                 )

mycursor.execute("CREATE TABLE security("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "user_id INT NOT NULL,"
                    "salt VARCHAR(100),"
                    "hash_password CHAR(255),"
                    "last_login VARCHAR(25),"
                    "failed_attempts INT DEFAULT 0,"  # There is a count of how many times user failed logining
                    "account_locked BOOLEAN DEFAULT 0,"         # This shows if the account blocked or not                    #BUGGG default 0
                    "FOREIGN KEY (user_id) REFERENCES users(id)"
                 ");"
                 )

mycursor.execute("CREATE TABLE history("
                 "id INT AUTO_INCREMENT PRIMARY KEY,"
                 "user_id INT NOT NULL,"
                 "FromCard VARCHAR(25),"              
                 "ToCard VARCHAR(25),"                
                 "amount VARCHAR(25) NOT NULL,"
                 "date DATETIME,"
                 "FOREIGN KEY (user_id) REFERENCES users(id) "
                 ");"
                 )
