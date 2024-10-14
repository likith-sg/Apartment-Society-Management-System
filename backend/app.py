from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Setup SQLite database (You can change the URI to MySQL or Postgres as per your requirement)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Login(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('admin', 'resident'), nullable=False)

class Residents(db.Model):
    reg_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    type = db.Column(db.Enum('rental', 'lease', 'buyer'), nullable=False)
    rent_amount = db.Column(db.Numeric(10, 2))
    deposit_amount = db.Column(db.Numeric(10, 2))
    maintenance_price = db.Column(db.Numeric(10, 2), nullable=False)
    house_no = db.Column(db.Integer)

class Homes(db.Model):
    house_no = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.Integer, db.ForeignKey('residents.reg_no'))
    floor = db.Column(db.Integer, nullable=False)

class Payments(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.Integer, db.ForeignKey('residents.reg_no'))
    amount = db.Column(db.Numeric(10, 2))
    payment_date = db.Column(db.Date)
    payment_type = db.Column(db.Enum('rent', 'maintenance', 'service', 'emi'))
    status = db.Column(db.Enum('paid', 'due'))

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = Login.query.filter_by(username=username, password=password).first()
    
    if user:
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid credentials. Please try again.")
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_resident', methods=['GET', 'POST'])
def add_resident():
    if request.method == 'POST':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        type = request.form.get('type')
        rent_amount = request.form.get('rent_amount')
        deposit_amount = request.form.get('deposit_amount')
        maintenance_price = request.form.get('maintenance_price')
        
        new_resident = Residents(name=name, phone_number=phone_number, type=type, 
                                rent_amount=rent_amount, deposit_amount=deposit_amount, 
                                maintenance_price=maintenance_price)
        db.session.add(new_resident)
        db.session.commit()
        flash('Resident added successfully!')
        return redirect(url_for('get_residents'))

    return render_template('add_resident.html')

@app.route('/get_residents')
def get_residents():
    residents = Residents.query.all()
    return render_template('get_residents.html', residents=residents)

@app.route('/update_resident/<int:reg_no>', methods=['GET', 'POST'])
def update_resident(reg_no):
    resident = Residents.query.get_or_404(reg_no)
    
    if request.method == 'POST':
        resident.name = request.form.get('name')
        resident.phone_number = request.form.get('phone_number')
        resident.type = request.form.get('type')
        resident.rent_amount = request.form.get('rent_amount')
        resident.deposit_amount = request.form.get('deposit_amount')
        resident.maintenance_price = request.form.get('maintenance_price')
        
        db.session.commit()
        flash('Resident updated successfully!')
        return redirect(url_for('get_residents'))

    return render_template('update_resident.html', resident=resident)

@app.route('/generate_report')
def generate_report():
    residents = Residents.query.all()
    return render_template('generate_report.html', residents=residents)

if __name__ == '__main__':
    with app.app_context():  # Wrap the create_all call in the app context
        db.create_all()
    app.run(debug=True)
