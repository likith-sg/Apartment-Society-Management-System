import sqlite3

def setup_database():
    conn = sqlite3.connect("apartment_management.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('Admin', 'Owner', 'Tenant', 'Employee')) NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Blocks (
            block_no INTEGER PRIMARY KEY,
            block_name TEXT,
            complaints TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Owners (
            owner_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            contact_info TEXT,
            address TEXT,
            associated_room_id INTEGER,
            FOREIGN KEY (associated_room_id) REFERENCES Rooms(room_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tenants (
            tenant_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            dob DATE,
            associated_room_id INTEGER,
            FOREIGN KEY (associated_room_id) REFERENCES Rooms(room_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT,
            contact_info TEXT,
            age INTEGER,
            block_no INTEGER,
            FOREIGN KEY (block_no) REFERENCES Blocks(block_no)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rooms (
            room_id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            tenant_id INTEGER,
            room_number TEXT NOT NULL,
            floor INTEGER,
            FOREIGN KEY (owner_id) REFERENCES Owners(owner_id),
            FOREIGN KEY (tenant_id) REFERENCES Tenants(tenant_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ParkingSlots (
            slot_id INTEGER PRIMARY KEY,
            room_id INTEGER,
            allotted_to INTEGER,
            FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
            FOREIGN KEY (allotted_to) REFERENCES Tenants(tenant_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Complaints (
            complaint_id INTEGER PRIMARY KEY,
            room_id INTEGER,
            tenant_id INTEGER,
            description TEXT,
            status TEXT CHECK(status IN ('Pending', 'In Progress', 'Resolved')) NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_by INTEGER,
            FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
            FOREIGN KEY (tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY (resolved_by) REFERENCES Employees(employee_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MaintenancePayments (
            payment_id INTEGER PRIMARY KEY,
            tenant_id INTEGER,
            amount REAL NOT NULL,
            date_paid DATETIME DEFAULT CURRENT_TIMESTAMP,
            payment_method TEXT,
            FOREIGN KEY (tenant_id) REFERENCES Tenants(tenant_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SystemLogs (
            log_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            action TEXT CHECK(action IN ('login', 'logout')) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Proof (
            proof_id INTEGER PRIMARY KEY,
            tenant_id INTEGER,
            owner_id INTEGER,
            proof TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY (owner_id) REFERENCES Owners(owner_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tenant_Room (
            tenant_id INTEGER,
            room_no INTEGER,
            date_of_joining DATE,
            monthly_rent REAL,
            PRIMARY KEY (tenant_id, room_no),
            FOREIGN KEY (tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY (room_no) REFERENCES Rooms(room_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Admins (
            admin_id INTEGER PRIMARY KEY,
            admin_name TEXT NOT NULL,
            admin_pass TEXT NOT NULL,
            block_no INTEGER,
            FOREIGN KEY (block_no) REFERENCES Blocks(block_no)
        )
    ''')

    try:
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', 'admin123', 'Admin'))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role) VALUES (?, ?, ?)",
                       ('owner', 'owner123', 'Owner'))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role) VALUES (?, ?, ?)",
                       ('tenant', 'tenant123', 'Tenant'))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role) VALUES (?, ?, ?)",
                       ('employee', 'employee123', 'Employee'))
    
        cursor.execute("INSERT OR IGNORE INTO Blocks (block_no, block_name, complaints) VALUES (?, ?, ?)",
                       (1, 'Block A', 'No complaints'))
        cursor.execute("INSERT OR IGNORE INTO Blocks (block_no, block_name, complaints) VALUES (?, ?, ?)",
                       (2, 'Block B', 'One complaint about parking'))

        cursor.execute("INSERT OR IGNORE INTO Owners (name, contact_info, address, associated_room_id) VALUES (?, ?, ?, ?)",
                       ('John Owner', '+1234567890', '123 Main St', 1))
        cursor.execute("INSERT OR IGNORE INTO Owners (name, contact_info, address, associated_room_id) VALUES (?, ?, ?, ?)",
                       ('Jane Owner', '+1234567891', '456 Elm St', 2))

        cursor.execute("INSERT OR IGNORE INTO Tenants (name, age, dob, associated_room_id) VALUES (?, ?, ?, ?)",
                       ('Tom Tenant', 30, '1993-05-15', 1))
        cursor.execute("INSERT OR IGNORE INTO Tenants (name, age, dob, associated_room_id) VALUES (?, ?, ?, ?)",
                       ('Sara Tenant', 28, '1995-08-20', 2))

        cursor.execute("INSERT OR IGNORE INTO Employees (name, position, contact_info, age, block_no) VALUES (?, ?, ?, ?, ?)",
                       ('Mike Worker', 'Maintenance', '+1234567892', 35, 1))
        cursor.execute("INSERT OR IGNORE INTO Employees (name, position, contact_info, age, block_no) VALUES (?, ?, ?, ?, ?)",
                       ('Lisa Worker', 'Security', '+1234567893', 40, 2))

        cursor.execute("INSERT OR IGNORE INTO Rooms (owner_id, tenant_id, room_number, floor) VALUES (?, ?, ?, ?)",
                       (1, 1, '101', 1))
        cursor.execute("INSERT OR IGNORE INTO Rooms (owner_id, tenant_id, room_number, floor) VALUES (?, ?, ?, ?)",
                       (2, 2, '102', 1))

        cursor.execute("INSERT OR IGNORE INTO ParkingSlots (room_id, allotted_to) VALUES (?, ?)",
                       (1, 1))
        cursor.execute("INSERT OR IGNORE INTO ParkingSlots (room_id, allotted_to) VALUES (?, ?)",
                       (2, 2))

        cursor.execute("INSERT OR IGNORE INTO Complaints (room_id, tenant_id, description, status) VALUES (?, ?, ?, ?)",
                       (1, 1, 'Noise complaint', 'Pending'))
        cursor.execute("INSERT OR IGNORE INTO Complaints (room_id, tenant_id, description, status) VALUES (?, ?, ?, ?)",
                       (2, 2, 'Parking space issue', 'Resolved'))

        cursor.execute("INSERT OR IGNORE INTO MaintenancePayments (tenant_id, amount, payment_method) VALUES (?, ?, ?)",
                       (1, 500.0, 'Cash'))
        cursor.execute("INSERT OR IGNORE INTO MaintenancePayments (tenant_id, amount, payment_method) VALUES (?, ?, ?)",
                       (2, 500.0, 'Card'))

        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

setup_database()
