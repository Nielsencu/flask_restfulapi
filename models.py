import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    dob = db.Column(db.String(50)) #Date format of YYYY-MM-DD
    updated_at = db.Column(db.String(50))