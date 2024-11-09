import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3
from datetime import datetime
from ttkthemes import ThemedTk
from tkinter import simpledialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from db_setup import setup_database

class ApartmentManagementSystem:
    def create_login_window(self):
        self.root = ThemedTk(theme="classic")
        self.root.title("Apartment Management System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True)

        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=20)

        title = ttk.Label(title_frame, text="APARTMENT MANAGEMENT SYSTEM",
                          font=("Helvetica", 24, "bold"))
        title.pack()

        subtitle = ttk.Label(title_frame, text="Login to continue",
                             font=("Helvetica", 12))
        subtitle.pack()

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, font=("Helvetica", 12))
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", font=("Helvetica", 12))
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        login_btn = ttk.Button(btn_frame, text="Login", command=self.login)
        login_btn.pack(pady=10, fill='x')

        exit_btn = ttk.Button(btn_frame, text="Exit", command=self.root.quit)
        exit_btn.pack(pady=5, fill='x')

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()

            if user:
                self.root.withdraw()  
                role = user[3]  
                self.open_dashboard(role, user)
            else:
                messagebox.showerror("Error", "Invalid credentials")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()

    def logout(self, dashboard):
        dashboard.destroy()
        self.root.deiconify()

    def open_dashboard(self, role, user):
        dashboard = Toplevel(self.root)
        dashboard.title(f"{role} Dashboard")
        dashboard.geometry("1000x700")
        dashboard.resizable(True, True)

        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill="both", expand=True)

        header_frame = ttk.Frame(dashboard)
        header_frame.pack(fill="x", pady=10)

        ttk.Label(header_frame, text=f"Welcome, {user[1]}", 
                  font=("Helvetica", 16, "bold")).pack(side="left", padx=10)
        
        ttk.Button(header_frame, text="Logout", 
                  command=lambda: self.logout(dashboard)).pack(side="right", padx=10)

        if role == "Admin":
            self.create_admin_dashboard(notebook, user)
        elif role == "Owner":
            self.create_owner_dashboard(notebook, user)
        elif role == "Tenant":
            self.create_tenant_dashboard(notebook, user)
        elif role == "Employee":
            self.create_employee_dashboard(notebook, user)

    # --------------------- Admin Dashboard ---------------------
    def create_admin_dashboard(self, notebook, user):
        admin_tab = ttk.Frame(notebook)
        notebook.add(admin_tab, text="Admin Panel")

        button_frame = ttk.Frame(admin_tab)
        button_frame.pack(side="left", fill="y", padx=10, pady=10)

        functions = [
            ("View Tenants", self.view_tenants),
            ("View Owners", self.view_owners),
            ("Create Owner", self.create_owner),
            ("Update Owner", self.update_owner),
            ("Delete Owner", self.delete_owner),
            ("Generate Report", self.generate_report),
        ]

        for text, command in functions:
            btn = ttk.Button(button_frame, text=text, command=lambda cmd=command: cmd())
            btn.pack(fill='x', pady=5)

        self.admin_data_frame = ttk.Frame(admin_tab)
        self.admin_data_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def view_tenants(self):
        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tenants")
        tenants = cursor.fetchall()
        conn.close()

        self.display_data(self.admin_data_frame, tenants, 
                         ["Tenant ID", "Name", "Age", "DOB", "Room No", "Parking Slot", "Owner ID", "Contact Info"])

    def view_owners(self):
        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Owners")
        owners = cursor.fetchall()
        conn.close()

        self.display_data(self.admin_data_frame, owners, 
                         ["Owner ID", "Name", "Contact Info", "Address", "Associated Room ID"])

    def create_owner(self):
        self.open_owner_form()

    def update_owner(self):
        owner_id = simpledialog.askinteger("Update Owner", "Enter Owner ID:")
        if owner_id:
            self.open_owner_form(owner_id)

    def delete_owner(self):
        owner_id = simpledialog.askinteger("Delete Owner", "Enter Owner ID:")
        if owner_id:
            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Owners WHERE owner_id = ?", (owner_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Owner deleted successfully.")

    def generate_report(self):
        report_path = os.path.join(os.path.expanduser("~"), "Downloads", "apartment_management_report.pdf")
        c = canvas.Canvas(report_path, pagesize=letter)
        c.drawString(100, 750, "Apartment Management System Report")
        c.drawString(100, 730, "-----------------------------------")

        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Admins")
        admins = cursor.fetchall()
        c.drawString(100, 700, "Admins:")
        y = 680
        for admin in admins:
            c.drawString(100, y, f"ID: {admin[0]}, Name: {admin[1]}, Contact: {admin[3]}")
            y -= 20

        cursor.execute("SELECT * FROM Owners")
        owners = cursor.fetchall()
        c.drawString(100, y, "Owners:")
        y -= 20
        for owner in owners:
            c.drawString(100, y, f"ID: {owner[0]}, Name: {owner[1]}, Contact: {owner[2]}")
            y -= 20

        cursor.execute("SELECT * FROM Tenants")
        tenants = cursor.fetchall()
        c.drawString(100, y, "Tenants:")
        y -= 20
        for tenant in tenants:
            c.drawString(100, y, f"ID: {tenant[0]}, Name: {tenant[1]}, Room No: {tenant[4]}")
            y -= 20

        cursor.execute("SELECT * FROM Employees")
        employees = cursor.fetchall()
        c.drawString(100, y, "Employees:")
        y -= 20
        for employee in employees:
            c.drawString(100, y, f"ID: {employee[0]}, Name: {employee[1]}, Position: {employee[2]}")
            y -= 20

        cursor.execute("SELECT * FROM Complaints")
        complaints = cursor.fetchall()
        c.drawString(100, y, "Complaints:")
        y -= 20
        for complaint in complaints:
            c.drawString(100, y, f"ID: {complaint[0]}, Tenant ID : {complaint[2]}, Status: {complaint[4]}")
            y -= 20

        conn.close()
        c.save()
        messagebox.showinfo("Success", f"Report generated and saved to {report_path}")

    # --------------------- Owner Dashboard ---------------------
    def create_owner_dashboard(self, notebook, user):
        owner_tab = ttk.Frame(notebook)
        notebook.add(owner_tab, text="Owner Panel")

        button_frame = ttk.Frame(owner_tab)
        button_frame.pack(side="left", fill="y", padx=10, pady=10)

        functions = [
            ("View My Tenants", lambda: self.view_owner_tenants(user[0])),
            ("Create Tenant", lambda: self.create_tenant(user[0])),
            ("Update Tenant", lambda: self.update_tenant(user[0])),
            ("Delete Tenant", lambda: self.delete_tenant(user[0])),
        ]

        for text, command in functions:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(fill='x', pady=5)

        self.owner_data_frame = ttk.Frame(owner_tab)
        self.owner_data_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def view_owner_tenants(self, owner_id):
        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tenants WHERE associated_room_id IN (SELECT room_id FROM Rooms WHERE owner_id = ?)", (owner_id,))
        tenants = cursor.fetchall()
        conn.close()

        self.display_data(self.owner_data_frame, tenants, 
                         ["Tenant ID", "Name", "Age", "DOB", "Room No", "Contact Info"])

    def create_tenant(self, owner_id):
        self.open_tenant_form(owner_id)

    def update_tenant(self, owner_id):
        tenant_id = simpledialog.askinteger("Update Tenant", "Enter Tenant ID:")
        if tenant_id:
            self.open_tenant_form(owner_id, tenant_id)

    def delete_tenant(self, owner_id):
        tenant_id = simpledialog.askinteger("Delete Tenant", "Enter Tenant ID:")
        if tenant_id:
            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Tenants WHERE tenant_id = ?", (tenant_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Tenant deleted successfully.")

    # --------------------- Tenant Dashboard ---------------------
    def create_tenant_dashboard(self, notebook, user):
        tenant_tab = ttk.Frame(notebook)
        notebook.add(tenant_tab, text="Tenant Panel")

        info_frame = ttk.LabelFrame(tenant_tab, text="Your Information")
        info_frame.pack(fill="x", padx=10, pady=10)
        button_frame = ttk.Frame(tenant_tab)
        button_frame.pack(fill="x", padx=10, pady=10)

        functions = [
            ("Pay Maintenance", lambda: self.pay_maintenance(user[0])),
            ("Raise Complaint", lambda: self.raise_complaint(user[0])),
            ("View My Complaints", lambda: self.view_tenant_complaints(user[0])),
        ]

        for text, command in functions:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side="left", padx=5, pady=5)

        self.tenant_data_frame = ttk.Frame(tenant_tab)
        self.tenant_data_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.view_tenant_complaints(user[0])  

    def view_tenant_complaints(self, tenant_id):
        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT complaint_id, description, status, date_created FROM Complaints
            WHERE tenant_id = ?
        """, (tenant_id,))
        complaints = cursor.fetchall()
        conn.close()

        print("Complaints fetched:", complaints)
        
        self.display_data(self.tenant_data_frame, complaints,
                          ["Complaint ID", "Description", "Status", "Date Created"])


    def pay_maintenance(self, tenant_id):
        form = tk.Toplevel(self.root)
        form.title("Pay Maintenance")
        form.geometry("400x300")
        form.resizable(False, False)

        ttk.Label(form, text="Amount:").pack(pady=5)
        amount_var = tk.DoubleVar()
        ttk.Entry(form, textvariable=amount_var).pack(pady=5)

        ttk.Label(form, text="Payment Method:").pack(pady=5)
        payment_method_var = tk.StringVar()
        payment_methods = ["Cash", "Credit Card", "Bank Transfer", "Cheque"]
        payment_method_menu = ttk.Combobox(form, textvariable=payment_method_var, values=payment_methods)
        payment_method_menu.pack(pady=5)

        def submit_payment():
            amount = amount_var.get()
            payment_method = payment_method_var.get()

            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than zero.")
                return
            if not payment_method:
                messagebox.showerror("Error", "Please select a payment method.")
                return

            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO MaintenancePayments (tenant_id, amount, payment_method)
                           VALUES (?, ?, ?)
                           """, (tenant_id, amount, payment_method))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Payment made successfully.")
            form.destroy()

        ttk.Button(form, text="Submit Payment", command=submit_payment).pack(pady=20)


    def raise_complaint(self, tenant_id):
        form = tk.Toplevel(self.root)
        form.title("Raise Complaint")
        form.geometry("400x300")
        form.resizable(False, False)

        ttk.Label(form, text="Description:").pack(pady=5)
        description_var = tk.StringVar()
        ttk.Entry(form, textvariable=description_var).pack(pady=5)

        def submit_complaint():
            description = description_var.get()
            if not description:
                messagebox.showerror("Error", "Description cannot be empty.")
                return

            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Complaints (tenant_id, description, status, date_created)
                VALUES (?, ?, 'Pending', ?)
            """, (tenant_id, description, datetime.now()))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Complaint raised successfully.")
            form.destroy()
            self.view_tenant_complaints(tenant_id)  

        ttk.Button(form, text="Submit", command=submit_complaint).pack(pady=20)
    # --------------------- Employee Dashboard ---------------------
    def create_employee_dashboard(self, notebook, user):
        employee_tab = ttk.Frame(notebook)
        notebook.add(employee_tab, text="Employee Panel")

        button_frame = ttk.Frame(employee_tab)
        button_frame.pack(side="left", fill="y", padx=10, pady=10)

        functions = [
            ("View All Complaints", self.view_all_complaints),
            ("Update Complaint Status", self.update_complaint_status),
            ("View Total Complaints", self.view_total_complaints),
        ]

        for text, command in functions:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(fill='x', pady=5)

        self.employee_data_frame = ttk.Frame(employee_tab)
        self.employee_data_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def view_all_complaints(self):
        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Complaints.complaint_id, Tenants.name, Complaints.description, Complaints.status, Complaints.date_created
            FROM Complaints
            JOIN Tenants ON Complaints.tenant_id = Tenants.tenant_id
        """)
        complaints = cursor.fetchall()
        conn.close()

        self.display_data(self.employee_data_frame, complaints, 
                         ["Complaint ID", "Tenant Name", "Description", "Status", "Date Created"])

    def update_complaint_status(self):
        complaint_id = simpledialog.askinteger("Update Complaint", "Enter Complaint ID:")
        if complaint_id:
            new_status = simpledialog.askstring("Update Status", "Enter new status (Pending/Resolved):")
            if new_status in ["Pending", "Resolved"]:
                conn = sqlite3.connect("apartment_management.db")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Complaints SET status = ?
                    WHERE complaint_id = ?
                """, (new_status, complaint_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Complaint status updated successfully.")
            else:
                messagebox.showerror("Error", "Invalid status entered.")

    def view_total_complaints(self):
        conn = sqlite3.connect("apartment_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Complaints")
        total_complaints = cursor.fetchone()[0]
        conn.close()

        stats_text = f"Total Complaints: {total_complaints}"
        self.display_text(self.employee_data_frame, stats_text)

    # --------------------- Helper Methods ---------------------
    def display_data(self, frame, data, headers):
        for widget in frame.winfo_children():
            widget.destroy()

        tree = ttk.Treeview(frame, columns=headers, show='headings')
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, anchor="center")

        for row in data:
            tree.insert("", tk.END, values=row)

        tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def display_text(self, frame, text):
        for widget in frame.winfo_children():
            widget.destroy()
        text_widget = tk.Text(frame, wrap="word", font=("Helvetica", 12))
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

    def open_owner_form(self, owner_id=None):
        form = Toplevel(self.root)
        form.title("Create/Update Owner")
        form.geometry("400x400")
        form.resizable(False, False)

        ttk.Label(form, text="Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form, textvariable=name_var).pack(pady=5)

        ttk.Label(form, text="Contact Info:").pack(pady=5)
        contact_var = tk.StringVar()
        ttk.Entry(form, textvariable=contact_var).pack(pady=5)

        ttk.Label(form, text="Address:").pack(pady=5)
        address_var = tk.StringVar()
        ttk.Entry(form, textvariable=address_var).pack(pady=5)

        if owner_id:
            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Owners WHERE owner_id = ?", (owner_id,))
            owner = cursor.fetchone()
            conn.close()

            if owner:
                name_var.set(owner[1])
                contact_var.set(owner[2])
                address_var.set(owner[3])

        def submit_owner():
            name = name_var.get()
            contact = contact_var.get()
            address = address_var.get()

            if not all([name, contact, address]):
                messagebox.showerror("Error", "All fields are required.")
                return

            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            try:
                if owner_id:
                    cursor.execute("""
                        UPDATE Owners SET name = ?, contact_info = ?, address = ?
                        WHERE owner_id = ?
                    """, (name, contact, address, owner_id))
                else:
                    cursor.execute("""
                        INSERT INTO Owners (name, contact_info, address)
                        VALUES (?, ?, ?)
                    """, (name, contact, address))
                conn.commit()
                messagebox.showinfo("Success", "Owner saved successfully.")
                form.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Owner already exists.")
            finally:
                conn.close()

        ttk.Button(form, text="Submit", command=submit_owner).pack(pady=20)

    def open_tenant_form(self, owner_id, tenant_id=None):
        form = Toplevel(self.root)
        form.title("Create/Update Tenant")
        form.geometry("400x500")
        form.resizable(False, False)

        ttk.Label(form, text="Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form, textvariable=name_var).pack(pady=5)

        ttk.Label(form, text="Age:").pack(pady=5)
        age_var = tk.IntVar()
        ttk.Entry(form, textvariable=age_var).pack(pady=5)

        ttk.Label(form, text="DOB (YYYY-MM-DD):").pack(pady=5)
        dob_var = tk.StringVar()
        ttk.Entry(form, textvariable=dob_var).pack(pady=5)

        ttk.Label(form, text="Room No:").pack(pady=5)
        room_no_var = tk.IntVar()
        ttk.Entry(form, textvariable=room_no_var).pack(pady=5)

        ttk.Label(form, text="Contact Info:").pack(pady=5)
        contact_var = tk.StringVar()
        ttk.Entry(form, textvariable=contact_var).pack(pady=5)

        if tenant_id:
            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Tenants WHERE tenant_id = ?", (tenant_id,))
            tenant = cursor.fetchone()
            conn.close()

            if tenant:
                name_var.set(tenant[1])
                age_var.set(tenant[2])
                dob_var.set(tenant[3])
                room_no_var.set(tenant[4])
                contact_var.set(tenant[6])

        def submit_tenant():
            name = name_var.get()
            age = age_var.get()
            dob = dob_var.get()
            room_no = room_no_var.get()
            contact = contact_var.get()

            if not all([name, age, dob, room_no, contact]):
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                datetime.strptime(dob, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "DOB must be in YYYY-MM-DD format.")
                return

            conn = sqlite3.connect("apartment_management.db")
            cursor = conn.cursor()
            try:
                if tenant_id:
                    cursor.execute("""
                        UPDATE Tenants SET name = ?, age = ?, dob = ?, associated_room_id = ?, contact_info = ?
                        WHERE tenant_id = ?
                    """, (name, age, dob, room_no, contact, tenant_id))
                else:
                    cursor.execute("""
                        INSERT INTO Tenants (name, age, dob, associated_room_id, contact_info)
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, age, dob, room_no, contact))
                conn.commit()
                messagebox.showinfo("Success", "Tenant saved successfully.")
                form.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Room number already exists.")
            finally:
                conn.close()

        ttk.Button(form, text="Submit", command=submit_tenant).pack(pady=20)

# --------------------- Main Execution ---------------------
if __name__ == "__main__":
    setup_database()
    app = ApartmentManagementSystem()
    app.create_login_window()
    app.root.mainloop()