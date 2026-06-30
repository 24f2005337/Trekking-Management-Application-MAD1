from datetime import datetime
from .database import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='trekker')  
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    staff_profile = db.relationship('StaffProfile', backref='user_identity', uselist=False, cascade="all, delete-orphan")
    
    bookings = db.relationship('Booking', backref='trekker', cascade="all, delete-orphan")


class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    contact_details = db.Column(db.String(15), nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)  

    assigned_treks = db.relationship('Trek', backref='assigned_staff')


class Trek(db.Model):
    __tablename__ = 'treks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  
    duration = db.Column(db.Integer, nullable=False)  
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    staff_id = db.Column(db.Integer, db.ForeignKey('staff_profiles.id'), nullable=True)
    bookings = db.relationship('Booking', backref='trek_details', cascade="all, delete-orphan")


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='Booked', nullable=False)  