from flask import Flask, render_template, request, redirect, session, url_for, flash  # Import Flask and helper modules
import bcrypt                                                                           # Import bcrypt for password hashing
import mysql.connector                                                                  # MySQL connector for database interaction
from auth import authenticate_user                                                      # Import authentication function
from fetch_devices import get_all_devices                                               # Import function to get all devices
from delete_device import delete_device                                                 # Import function to delete a device
from db import connect_to_db, myDB                                                      # Import function to connect to MySQL
import nmap                                                                             # Import nmap for network scanning          
from scan_network import scan_network
from passive_scan import init_scheduler                                                 # Import the scheduler setup function
from scan_network import scan_network
from key import secretkey



                                         

app = Flask(__name__)                                                   # Create the Flask app instance
app.secret_key = secretkey  
print("Flask app is starting")                                          # Debugging Prints
init_scheduler(app)                                          


# Function to check MySQL connection
def test_db_connection():
    try:
        db = connect_to_db()                                # Connect to the database
        if db:
            print("Successfully connected to MySQL!")
            db.close()                                      # Close connection if successful
        else:
            print("Failed to connect to MySQL.")
    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")          # Print error if connection fails



# Route to manage users (Admin Only)
@app.route("/manage_users")
def manage_users():
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: Only Admins can manage users.", "danger")
        return redirect(url_for("dashboard"))

    db = connect_to_db()
    cursor = db.cursor(dictionary=True)

    # Get all users
    cursor.execute("""
        SELECT users.id, users.username, roles.role_name 
        FROM users JOIN roles ON users.role_id = roles.id
    """)
    users = cursor.fetchall()

    # Get available roles
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("manage_users.html", users=users, roles=roles)




# Route to add a new user (Admin Only)
@app.route("/add_user", methods=["POST"])
def add_user():
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: Only Admins can add users.", "danger")
        return redirect(url_for("manage_users"))

    username = request.form["username"]
    password = request.form["password"]
    role_id = request.form["role_id"]

    # Hash password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    db = connect_to_db()
    cursor = db.cursor()

    # Check if username already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    if cursor.fetchone()[0] > 0:
        flash("❌ Username already exists.", "danger")
        cursor.close()
        db.close()
        return redirect(url_for("manage_users"))

    # Insert new user
    cursor.execute("INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)", 
                   (username, hashed_password.decode("utf-8"), role_id))
    db.commit()
    cursor.close()
    db.close()

    flash(f"✅ User '{username}' added successfully!", "success")
    return redirect(url_for("manage_users"))



# Route to delete a user (Admin Only)
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: Only Admins can delete users.", "danger")
        return redirect(url_for("manage_users"))

    db = connect_to_db()
    cursor = db.cursor()

    # Prevent Admin from deleting themselves
    if session["user_id"] == user_id:
        flash("❌ You cannot delete yourself!", "danger")
        return redirect(url_for("manage_users"))

    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()

    flash("✅ User deleted successfully!", "success")
    return redirect(url_for("manage_users"))



# Route to delete a device (Admin Only)
@app.route("/delete_device/<int:device_id>")
def delete_device_route(device_id):
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: Only Admins can delete devices.", "danger")
        return redirect(url_for("dashboard"))

    delete_device(device_id, session["role"])
    flash("✅ Device deleted successfully!", "success")
    return redirect(url_for("dashboard"))




# Route to add a device (Admin Only)
@app.route("/add_device", methods=["GET", "POST"])
def add_device():
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: Only Admins can add devices", "danger")
        return redirect(url_for("dashboard"))

    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM device_types")  # Fetch available device types
    device_types = cursor.fetchall()
    cursor.close()
    db.close()

    if request.method == "POST":
        device_type_id = request.form.get("device_type_id")
        device_address = request.form.get("device_address")
        device_netmask = request.form.get("device_netmask")
        device_gateway = request.form.get("device_gateway")
        status = request.form.get("status")

        if not all([device_type_id, device_address, device_netmask, device_gateway, status]):
            flash("❌ All required fields must be filled.")
            return redirect(url_for("add_device"))

        db = connect_to_db()
        cursor = db.cursor()

        # Insert into devices table
        query = """
            INSERT INTO devices 
            (device_type_id, device_address, device_netmask, device_gateway, user_id) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (device_type_id, device_address, device_netmask, device_gateway, session["user_id"]))

        # Get the last inserted device ID
        device_id = cursor.lastrowid

        # Insert into device_status table
        cursor.execute("INSERT INTO device_status (device_id, status) VALUES (%s, %s)", (device_id, status))

        db.commit()
        cursor.close()
        db.close()

        flash("✅ Device added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_device.html", device_types=device_types)






#Edit device route
@app.route("/edit_device/<int:device_id>", methods=["GET", "POST"])
def edit_device(device_id):
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: Only Admins can edit devices.", "danger")
        return redirect(url_for("dashboard"))

    db = connect_to_db()
    cursor = db.cursor(dictionary=True)

    # Fetch device details
    cursor.execute("""
        SELECT devices.*, device_status.status 
        FROM devices 
        LEFT JOIN device_status ON devices.id = device_status.device_id
        WHERE devices.id = %s
    """, (device_id,))
    device = cursor.fetchone()

    # Fetch device types for dropdown
    cursor.execute("SELECT * FROM device_types")
    device_types = cursor.fetchall()

    if not device:
        flash("❌ Device not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        device_type_id = request.form["device_type_id"]
        device_address = request.form["device_address"]
        device_netmask = request.form["device_netmask"]
        device_gateway = request.form["device_gateway"]
        status = request.form.get("status")

        # Update device details
        update_query = """
            UPDATE devices 
            SET device_type_id=%s, device_address=%s, device_netmask=%s, device_gateway=%s
            WHERE id=%s
        """
        cursor.execute(update_query, (device_type_id, device_address, device_netmask, device_gateway, device_id))

        # Update device_status
        cursor.execute("UPDATE device_status SET status=%s WHERE device_id=%s", (status, device_id))

        db.commit()
        cursor.close()
        db.close()

        flash("✅ Device updated successfully!", "success")
        return redirect(url_for("dashboard"))

    cursor.close()
    db.close()
    
    return render_template("edit_device.html", device=device, device_types=device_types)


#scan network route
@app.route("/scan_network", methods=["GET", "POST"])
def scan_network_route():
    if "user_id" not in session or session["role"] != "Admin":
        flash("❌ Access Denied: only Admins can start a scan","danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        target_ip = request.form.get("target_ip")
        ports = request.form.get("ports")

        if not target_ip:
            flash("Please enter a target IP")
            return redirect(url_for("scan_network_route"))

        
        scan_results = scan_network(target_ip, ports, session["user_id"])                   #Pass user_id as a parameter

        if not scan_results:
            flash("No open ports found or scan failed ")

        return redirect(url_for("scan_history"))                                            # Redirect to scan history page

    return render_template("scan_network.html")                                             # Render scan form



#scan history route
@app.route("/scan_history")
def scan_history():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT scan_results.ip_address, scan_results.port, scan_results.protocol, 
           scan_results.state, scan_results.service, scan_results.scan_time, users.username
    FROM scan_results
    JOIN users ON scan_results.user_id = users.id
    ORDER BY scan_results.scan_time DESC
    """


    cursor.execute(query)
    past_scans = cursor.fetchall()

    cursor.close()
    db.close()

    print("DEBUG: Past Scans Fetched:")
    for scan in past_scans:
        print(scan)

    return render_template("scan_history.html", past_scans=past_scans)



# Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    devices = get_all_devices()
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        devices=devices,
    )

#Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = authenticate_user(username, password)

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role_name"]
            return redirect(url_for("dashboard"))

        flash("Wrong username or password.")
    return render_template("login.html")


# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))





if __name__ == "__main__":
    print("Flask server is running")
    test_db_connection()                                                # Test MySQL connection before starting Flask
    app.run(debug=True, host="0.0.0.0")

