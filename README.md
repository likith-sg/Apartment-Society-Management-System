# Apartment Society Management System (ASMS)

## Overview

The Apartment Society Management System (ASMS) is a comprehensive application designed to manage various aspects of apartment living, including user management, tenant and owner interactions, complaint handling, maintenance payments, and reporting functionalities. Built using Python, SQLite, and Tkinter, this system provides an intuitive graphical user interface for different user roles, including Admin, Owner, Tenant, and Employee.

## Features

- **User Authentication:** Secure login for different user roles with unique credentials.
- **Role-Based Dashboards:** Customized dashboards for Admins, Owners, Tenants, and Employees, providing relevant functionalities.
- **Tenant and Owner Management:** Admins can view, create, update, and delete tenant and owner records.
- **Complaint Management:** Tenants can raise complaints, and employees can view and update the status of these complaints.
- **Maintenance Payments:** Tenants can make maintenance payments through various methods.
- **Reporting:** Generate detailed reports of the apartment society, including information about users, owners, tenants, employees, and complaints.
- **Database Setup:** Automatically sets up the SQLite database with necessary tables and sample data.

## Technologies Used

- **Python:** The primary programming language used for development.
- **Tkinter:** A standard GUI toolkit for Python to create the application interface.
- **SQLite:** A lightweight database engine used for data storage.
- **ReportLab:** A library for generating PDF documents.

## Installation

### Clone the Repository:

```bash
git clone https://github.com/yourusername/apartment-society-management-system.git
cd apartment-society-management-system
```

## Install Required Libraries:
Make sure you have Python installed. Then, install the necessary libraries:

```bash
pip install ttkthemes reportlab
```

## Run the Application:
Execute the main application file:

```bashbash
python ASMS.py
```

## Database Setup

The application automatically sets up the SQLite database when it is run for the first time. The `db_setup.py` script creates the following tables:

- **Users:** Stores user information, including username, password, and role.
- **Blocks:** Contains information about different blocks in the apartment.
- **Owners:** Holds details of apartment owners.
- **Tenants:** Contains tenant information.
- **Employees:** Stores employee details.
- **Rooms:** Information about rooms and their associations with owners and tenants.
- **ParkingSlots:** Tracks parking slot allocations.
- **Complaints:** Manages complaints raised by tenants.
- **MaintenancePayments:** Records maintenance payment transactions.
- **SystemLogs:** Logs user actions for auditing purposes.
- **Proof:** Stores proof documents related to tenants and owners.
- **Tenant_Room:** Manages the relationship between tenants and their respective rooms.
- **Admins:** Stores admin details.


## Usage

1. Launch the application.
2. Log in using the provided credentials:
   - **Admin:** username: `admin`, password: `admin123`
   - **Owner:** username: `owner`, password: `owner123`
   - **Tenant:** username: `tenant`, password: `tenant123`
   - **Employee:** username: `employee`, password: `employee123`
3. Navigate through the dashboards and utilize the available functionalities based on your role.


## Contributing
Contributions are welcome! If you have suggestions for improvements or new features, feel free to create an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
