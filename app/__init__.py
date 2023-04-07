from flask import Flask

from app import config


app = Flask(__name__)
app.secret_key = config.APP_SECRET


from .handlers import api, oauth
