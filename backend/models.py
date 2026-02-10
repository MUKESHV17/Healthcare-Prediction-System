from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    password = db.Column(db.String(200)) # Hashed
    role = db.Column(db.String(20), default='patient')
    address = db.Column(db.Text)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    profile_pic = db.Column(db.Text)
    is_verified = db.Column(db.Integer, default=0) # 0 or 1
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    gender = db.Column(db.String(20), default='Male')

    # Relationships
    doctors = db.relationship('Doctor', backref='user', uselist=False)
    appointments = db.relationship('Appointment', backref='patient', foreign_keys='Appointment.patient_id')
    reports = db.relationship('Report', backref='user')
    notifications = db.relationship('Notification', backref='user')

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    _departments = db.Column('departments', db.Text) # JSON string

    @property
    def departments(self):
        return json.loads(self._departments) if self._departments else []

    @departments.setter
    def departments(self, value):
        self._departments = json.dumps(value)

    doctors = db.relationship('Doctor', backref='hospital')
    appointments = db.relationship('Appointment', backref='hospital')

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    department = db.Column(db.String(100))
    specialty = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    _availability = db.Column('availability', db.Text) # JSON string

    @property
    def availability(self):
        return json.loads(self._availability) if self._availability else []

    @availability.setter
    def availability(self, value):
        self._availability = json.dumps(value)

    appointments = db.relationship('Appointment', backref='doctor', foreign_keys='Appointment.doctor_id')

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    date = db.Column(db.String(20))
    time_slot = db.Column(db.String(20))
    status = db.Column(db.String(50), default='Pending Confirmation')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    is_read = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    disease_type = db.Column(db.String(100))
    prediction = db.Column(db.String(100))
    risk_level = db.Column(db.String(50))
    date = db.Column(db.String(50))
    pdf_path = db.Column(db.Text)

class OTP(db.Model):
    __tablename__ = 'otp_codes'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20))
    otp = db.Column(db.String(10))
    expires_at = db.Column(db.Integer)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(50)) # unique room per appointment or doctor-patient pair
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    deleted_for_sender = db.Column(db.Boolean, default=False)
    deleted_for_all = db.Column(db.Boolean, default=False)
