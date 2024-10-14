CREATE DATABASE Apartment;
USE Apartment;

CREATE TABLE Login (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    role ENUM('admin', 'resident') NOT NULL
);

CREATE TABLE Residents (
    reg_no INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    type ENUM('rental', 'lease', 'buyer') NOT NULL,
    rent_amount DECIMAL(10, 2),
    deposit_amount DECIMAL(10, 2),
    maintenance_price DECIMAL(10, 2) NOT NULL,
    house_no INT
);

CREATE TABLE Homes (
    house_no INT PRIMARY KEY,
    reg_no INT,
    floor INT NOT NULL,
    CONSTRAINT fk_resident FOREIGN KEY (reg_no) REFERENCES Residents (reg_no) ON DELETE SET NULL,
    UNIQUE (reg_no)
);

CREATE TABLE VisitorLog (
    visitor_id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100),
    house_no INT,
    visit_date DATE,
    visit_duration DECIMAL(5, 2),
    CONSTRAINT fk_house FOREIGN KEY (house_no) REFERENCES Homes(house_no)
);

CREATE TABLE Services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE ResidentServices (
    reg_no INT,
    service_id INT,
    CONSTRAINT fk_service FOREIGN KEY (service_id) REFERENCES Services(service_id),
    CONSTRAINT fk_resident_service FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

CREATE TABLE Payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    amount DECIMAL(10, 2),
    payment_date DATE,
    payment_type ENUM('rent', 'maintenance', 'service', 'emi'),
    status ENUM('paid', 'due'),
    CONSTRAINT fk_resident_payment FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

CREATE TABLE Complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    complaint_date DATE,
    complaint_details TEXT,
    status ENUM('open', 'in progress', 'closed'),
    CONSTRAINT fk_complaint_resident FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

CREATE TABLE ServiceUsage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    service_id INT,
    usage_date DATE,
    usage_count INT,
    CONSTRAINT fk_usage_service FOREIGN KEY (service_id) REFERENCES Services(service_id),
    CONSTRAINT fk_usage_resident FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

CREATE TABLE Notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    message VARCHAR(255),
    notification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Parking (
    parking_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    slot_number VARCHAR(10),
    vehicle_number VARCHAR(20),
    vehicle_type VARCHAR(20),
    FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

CREATE VIEW AvailableParkingSlots AS
SELECT slot_number FROM Parking
WHERE reg_no IS NULL;

CREATE TABLE ServiceStaff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    job_title VARCHAR(255),
    contact_no VARCHAR(15),
    shift_time VARCHAR(50),
    assigned_building INT
);

CREATE TABLE LeaseAgreements (
    agreement_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    lease_start DATE,
    lease_end DATE,
    FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

CREATE TABLE Buyers (
    buyer_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no INT,
    purchase_type ENUM('full_payment', 'down_payment') NOT NULL,
    total_amount DECIMAL(15, 2),
    down_payment_amount DECIMAL(15, 2),
    emi_amount DECIMAL(10, 2),
    next_emi_due_date DATE,
    FOREIGN KEY (reg_no) REFERENCES Residents(reg_no)
);

DELIMITER $$

CREATE TRIGGER notify_emi_due
BEFORE UPDATE ON Buyers
FOR EACH ROW
BEGIN
    IF NEW.purchase_type = 'down_payment' AND NEW.next_emi_due_date <= CURDATE() THEN
        INSERT INTO Notifications (reg_no, message)
        VALUES (NEW.reg_no, 'Your EMI is due!');
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE NotifyLeaseExpiry()
BEGIN
    DECLARE today DATE DEFAULT CURDATE();

    INSERT INTO Notifications (reg_no, message)
    SELECT reg_no, CONCAT('Your lease expires on ', lease_end)
    FROM LeaseAgreements
    WHERE DATEDIFF(lease_end, today) <= 30;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER notify_rent_due
BEFORE UPDATE ON Payments
FOR EACH ROW
BEGIN
    IF NEW.status = 'due' AND NEW.payment_type = 'rent' THEN
        INSERT INTO Notifications (reg_no, message) 
        VALUES (NEW.reg_no, 'Your rent is due!');
    END IF;
END $$

DELIMITER ;