from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Lendigo.config import Config
import pymysql#driver for the sql db

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(Config)
db =  SQLAlchemy(app)

from Lendigo.models import Item
db.create_all()
db.session.commit()

from Lendigo.errors.handlers import errors
app.register_blueprint(errors)

from Lendigo import routes