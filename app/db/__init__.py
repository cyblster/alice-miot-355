from flask_sqlalchemy import SQLAlchemy
from app import app, config


app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
db = SQLAlchemy(app)
