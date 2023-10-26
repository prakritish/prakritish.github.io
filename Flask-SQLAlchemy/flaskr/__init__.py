from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# Required for DB Migration
from flask_migrate import Migrate
# SQLALCHEMY_DATABASE_URI is defined in 'flaskr/config.py'
from flaskr.config import SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()

def create_app(test_config=None):
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
  db.init_app(app)
  Migrate(app, db)
  # Import model classes. I have my models.py with 3 clasess in folder flaskr
  #from flaskr.models import Author, Book, Store
  with app.app_context():
    from . import models  # Import models
    from . import routes  # Import routes
  return app