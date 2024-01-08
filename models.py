from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Donor(db.Model):
    __tablename__ = 'donor'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    bloodtype = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(50), nullable=False)
    phoneNumber = db.Column(db.String(15), nullable=False)
    photoPath = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)  

class AvailableBlood(db.Model):
    __tablename__ = 'available_blood'
    id = db.Column(db.Integer, primary_key=True)
    bloodtype = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(50), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'))
    donor = db.relationship('Donor', backref='available_blood')

