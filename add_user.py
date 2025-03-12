import mysql.connector as mysql
import dbConfig as myDB
import bcrypt

def add_user(username, password, role_id):
    #Add a new user with a hashed password.
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    db = mysql.connect(
        user=myDB.dbConfig["user"],
        password=myDB.dbConfig["password"],
        host=myDB.dbConfig["host"],
        database=myDB.dbConfig["database"]
    )
    cursor = db.cursor()

    query = "INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, hashed_password, role_id))

    db.commit()
    cursor.close()
    db.close()

    print(f"✅ User '{username}' added successfully!")

# Test the function
if __name__ == "__main__":
    new_username = input("Enter new username: ")
    new_password = input("Enter new password: ")
    role = int(input("Enter role ID (1 for Admin, 2 for Viewer): "))

    add_user(new_username, new_password, role)
