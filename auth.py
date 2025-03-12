import mysql.connector as mysql     # Import MySQL connector to interact with the database
import dbConfig as myDB             # Import database credentials from dbConfig.py
import bcrypt                       # Import bcrypt for password hashing and verification


def authenticate_user(username, password):                                  # Function to authenticate a user and return their details if successful
    db = mysql.connect(
        user=myDB.dbConfig["user"],                                         # MySQL username
        password=myDB.dbConfig["password"],                                 # MySQL password
        host=myDB.dbConfig["host"],                                         # Database host (localhost in this case)
        database=myDB.dbConfig["database"]                                  # The name of the database
    )

    cursor = db.cursor(dictionary=True)                                     # Create a cursor to interact with the database, dictionary=True makes results return as dictionaries instead of tuples

    
    query = """
    SELECT users.id, users.username, users.password, roles.role_name 
    FROM users 
    JOIN roles ON users.role_id = roles.id
    WHERE users.username = %s
    """
    
    cursor.execute(query, (username,))                                          # Execute the query with the provided username
    user = cursor.fetchone()                                                    # Fetch one matching user record

    cursor.close()                                                              # Close the cursor
    db.close()                                                                  # Close the database connection

    if user:                                                                                    # Verify password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            return user                                                                         # If the password is correct, return the user details
        else:
            print("Wrong Password")                                                     # Print error if password doesn't match
            return None                                                                         # Return None if authentication fails
    else:
        print("User not found!")                                                             # Print error if username doesn't exist in the database
        return None                                                                                 # Return None if user is not found

# Test the authentication function if the script is run directly
if __name__ == "__main__":
    username = input("Enter username: ")  # Ask for the username
    password = input("Enter password: ")  # Ask for the password

    user = authenticate_user(username, password)  # Call the authentication function
    
    if user:
        print(f"✅ Login successful! Welcome {user['username']} - Role: {user['role_name']}")
    else:
        print("❌ Invalid credentials. Try again.")  # Print an error message if login fails
