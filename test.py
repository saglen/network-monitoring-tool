import nmap

nm = nmap.PortScanner()
target_ip = "192.168.68.0/24"
ports = "20-1000"

print("Starting manual Nmap Scan...")
nm.scan(hosts=target_ip, arguments=f"-p {ports} -sV --open", timeout=60)
print(nm.all_hosts())

for host in nm.all_hosts():
    print(f"Host: {host}")
    for proto in nm[host].all_protocols():
        for port, details in nm[host][proto].items():
            print(f"Port: {port}, State: {details['state']}, Service: {details.get('name', 'Unknown')}")