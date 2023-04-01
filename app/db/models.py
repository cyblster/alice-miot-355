from app import app
from . import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    hashed_password = db.Column(db.String(60))
    code = db.Column(db.UUID, unique=True)
    refresh_token = db.Column(db.Text, unique=True)


with app.app_context():
    db.create_all()
