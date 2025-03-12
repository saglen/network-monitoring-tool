import mysql.connector as mysql
import dbConfig as myDB

def get_all_devices():                                          #Fetch all devices from the database, including device type and status."""
    db = mysql.connect(
        user=myDB.dbConfig["user"],
        password=myDB.dbConfig["password"],
        host=myDB.dbConfig["host"],
        database=myDB.dbConfig["database"]
    )
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT 
            devices.id, 
            device_types.type_name AS device_type, 
            devices.device_address, 
            devices.device_netmask, 
            devices.device_gateway, 
            device_status.status
        FROM devices
        LEFT JOIN device_types ON devices.device_type_id = device_types.id
        LEFT JOIN device_status ON devices.id = device_status.device_id;
    """
    
    cursor.execute(query)
    devices = cursor.fetchall()

    cursor.close()
    db.close()

    return devices



# Test function
if __name__ == "__main__":
    devices = get_all_devices()  # Call function to fetch devices
    if devices:  # Check if there are devices in the database
        print("\n--- Network Devices ---")  # Print a header
        for device in devices:  # Loop through each device in the list
            print(f"{device['id']}: {device['device_type']} - {device['device_address']} (Added by: {device['added_by']})")
    else:
        print("❌ No devices found in the database.")  # Print message if no devices are found
