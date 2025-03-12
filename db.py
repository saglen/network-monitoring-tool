import mysql.connector as mysql                                                 # Import MySQL connector and rename it as 'mysql'
import dbConfig as myDB                                                           # Import database configuration from dbConfig.py


# Connect to MySQL database and return the connection object.
def connect_to_db():
    try:                                                             #The try block attempts to establish a connection to the MySQL database.
        connection = mysql.connect(                                  #mysql.connect() uses database credentials from dbConfig.py to connect dynamically.
            user=myDB.dbConfig["user"],
            password=myDB.dbConfig["password"],
            host=myDB.dbConfig["host"],
            database=myDB.dbConfig["database"]
        )
        return connection                                               #If successful, the connection object is returned so other scripts can use it.
    
    except mysql.Error as err:                                          #The except block catches database connection errors and prints a message.
        print(f"❌ Database connection error: {err} ❌")                   #This prevents crashes by handling errors gracefully.
        return None                                                     #Instead of stopping execution, the function returns None, allowing the program to continue.

# Test the connection
if __name__ == "__main__":                                              #condition ensures this code only runs if the script is executed directly, not when imported.
    db = connect_to_db()
    if db:
        print("✅ Connection to the Database is a sucess! ✅")
        db.close()
        print("🔒 Connection closed. 🔒")                                   #It tests the database connection, prints success if it works, and closes the connection properly.
