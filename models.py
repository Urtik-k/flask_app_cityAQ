from database import db

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(30), nullable = False)
    pm2 = db.Column(db.Float)
    pm10 = db.Column(db.Float)
    no2 = db.Column(db.Float)
    co = db.Column(db.Float)
    o3 = db.Column(db.Float)
    so3 = db.Column(db.Float)
