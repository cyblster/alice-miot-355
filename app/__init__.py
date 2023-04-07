from flask import Flask

from app import config


app = Flask(__name__)


from .handlers import api, oauth
