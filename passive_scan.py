import nmap
from db import connect_to_db                                                                # Ensure DB connection function
from flask_apscheduler import APScheduler
from scan_network import scan_network                                                       # Import your scanning function
                                                               
scheduler = APScheduler()                                                                   # Create the scheduler instance

def scheduled_scan():                                                                       # Function to perform scheduled scanning
    target_ip = "192.168.68.0/24"                                                           # Network range of the "theoffice"
    ports = "20-1000"                                                                       # Port range
    user_id = 1                                                                             # admin user 1

    print("🔄 Scheduled scan started 🔄")

    scan_results = scan_network(target_ip, ports, user_id)

    if scan_results:
        print(f"📝{len(scan_results)} new scan results saved to the database 📝")
    else:
        print("⚠️ No open ports found ⚠️")

def init_scheduler(app):                                                                        #Initialize the scheduler with Flask.
    app.config["SCHEDULER_API_ENABLED"] = True
    scheduler.init_app(app)
    scheduler.start()

  
    scheduler.add_job(id="PassiveScan", func=scheduled_scan, trigger="interval", minutes=120)     # Scheduled scanning job
    print("⏰ Passive scanning is now scheduled every 3 minutes ⏰")

