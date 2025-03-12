CREATE DATABASE theoffice;

USE theoffice;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
);

CREATE TABLE device_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_type_id INT,
    device_address VARCHAR(50) NOT NULL,
    device_netmask VARCHAR(50) NOT NULL,
    device_gateway VARCHAR(50) NOT NULL,
    user_id INT,
    FOREIGN KEY (device_type_id) REFERENCES device_types(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);


CREATE TABLE device_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    status ENUM('Online', 'Offline') DEFAULT 'Offline',
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE port_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique ID for each scan entry
    device_id INT,                      -- Links to the scanned device
    port INT NOT NULL,                   -- The scanned port number (e.g., 22, 80)
    protocol ENUM('TCP', 'UDP') NOT NULL, -- Protocol type
    state ENUM('Open', 'Closed', 'Filtered') NOT NULL, -- Port state
    service VARCHAR(100),                -- Service running on the port (e.g., HTTP, SSH)
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When the scan was done
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE -- Links to the Devices table
);

CREATE TABLE scan_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(50) NOT NULL,
    port INT NOT NULL,
    protocol ENUM('TCP', 'UDP') NOT NULL,
    state VARCHAR(20) NOT NULL,
    service VARCHAR(100),
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE scan_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scanned_ip VARCHAR(50) NOT NULL,
    scanned_ports VARCHAR(100) NOT NULL,
    scanned_by INT NOT NULL,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scanned_by) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO roles (role_name) VALUES ('Admin'), ('Viewer');

INSERT INTO users (username, password, role_id) VALUES 
('admin_user', '--N0r0ffN1S', 1),
('viewer_user', 'Noroff123&?', 2); 

INSERT INTO device_types (type_name) VALUES ('Router'), ('Switch'), ('PC'),('HUB');

INSERT INTO devices (device_type_id, device_address, device_netmask, device_gateway, user_id)
VALUES 
(3, '192.168.68.52', '255.255.255.0', '192.168.68.1', 1);

INSERT INTO device_status (device_id, status) VALUES 
(1, 'Online');



SELECT * FROM scan_results ORDER BY scan_time DESC;
