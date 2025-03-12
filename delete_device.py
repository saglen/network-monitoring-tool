import mysql.connector as mysql
import dbConfig as myDB

def delete_device(device_id, user_role):
    """Allows only Admin users to delete a device from the database."""
    if user_role != "Admin":
        print("❌ Access Denied: Only Admins can delete devices.")
        return

    db = mysql.connect(
        user=myDB.dbConfig["user"],
        password=myDB.dbConfig["password"],
        host=myDB.dbConfig["host"],
        database=myDB.dbConfig["database"]
    )
    cursor = db.cursor()

    # Check if the device exists before deleting
    cursor.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
    device = cursor.fetchone()

    if device:
        cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        db.commit()
        print(f"✅ Device with ID {device_id} has been deleted.")
    else:
        print(f"❌ No device found with ID {device_id}.")

    cursor.close()
    db.close()

# Test function
if __name__ == "__main__":
    user_role = input("Enter your role (Admin/Viewer): ")
    device_id = input("Enter Device ID to delete: ")

    if device_id.isdigit():
        delete_device(int(device_id), user_role)
    else:
        print("❌ Invalid device ID. Must be a number.")
