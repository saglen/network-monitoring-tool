import nmap
import mysql.connector as mysql
from db import connect_to_db  

#Scans a network for open ports and saves results to the database.

def scan_network(target_ip, ports, user_id):                            
    
    nm = nmap.PortScanner()
    scan_results = []

    try:
        print(f"Starting scan on {target_ip} with ports {ports}")  
        nm.scan(hosts=target_ip, arguments=f"-p {ports} -sV --open")
        print("Scan completed!")  

        db = connect_to_db()
        cursor = db.cursor()

        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port, details in nm[host][proto].items():
                    state = details['state']
                    service = details.get('name', 'Unknown')

                    
                    cursor.execute("""
                        INSERT INTO scan_results (ip_address, port, protocol, state, service, scan_time, user_id)
                        VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                    """, (host, port, proto.upper(), state, service, user_id))

                    print(f"DEBUG: Saving scan -> IP: {host}, Port: {port}, State: {state}, Service: {service}, User ID: {user_id}")

                    scan_results.append({
                        "ip_address": host,
                        "port": port,
                        "protocol": proto.upper(),
                        "state": state,
                        "service": service,
                        "scan_time": "Now"
                    })

        db.commit()
        cursor.close()
        db.close()

        return scan_results

    except Exception as e:
        print(f"❌ Error during scanning: {e} ❌ ")  
        return []
