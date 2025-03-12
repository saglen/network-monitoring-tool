import bcrypt                                                                    # Import bcrypt for secure password hashing
import mysql.connector as mysql                                                      # Import MySQL connector to interact with the database
import dbConfig as myDB                                                  # Import database credentials from dbConfig.py

def hash_password(plain_text_password):                                 #Hashes a password using bcrypt to ensure security
    salt = bcrypt.gensalt()                                             # Generate a unique salt for additional security
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)   # Hash the password using bcrypt
    return hashed                                                       # Return the hashed password


db = mysql.connect(
    user=myDB.dbConfig["user"],                                         # Get MySQL username from dbConfig.py
    password=myDB.dbConfig["password"],                                 # Get MySQL password from dbConfig.py
    host=myDB.dbConfig["host"],                                         # Get MySQL host (e.g., localhost)
    database=myDB.dbConfig["database"]                                  # Specify the database to connect to
)
cursor = db.cursor()                                                       #Create a cursor to interact with the database

cursor.execute("SELECT id, username, password FROM users")              # Retrieve user IDs, usernames, and passwords
users = cursor.fetchall()                                               # Get all rows from the query result


for user in users:                                                      # Loop through each user and hash their password
    user_id, username, plain_text_password = user                       # Extract user details
    hashed_password = hash_password(plain_text_password)                # Hash the password using the hash_password function

    update_query = "UPDATE users SET password = %s WHERE id = %s"         # SQL query to update user password
    cursor.execute(update_query, (hashed_password, user_id))              # Execute the query with hashed password and user ID

db.commit()                                                             # Save the changes in the database
cursor.close()                                                          # Close the cursor to free resources
db.close()                                                              # Close the database connection

print("All passwords successfully hashed and updated!")              # Confirmation message for successful hashing
