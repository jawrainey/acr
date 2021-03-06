from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'allthedata.db'
app.debug = True
app.config['SECRET_KEY'] = 'supersecretpasswordfromtheotherside'

db = SQLAlchemy(app)

from app import views, models, api
