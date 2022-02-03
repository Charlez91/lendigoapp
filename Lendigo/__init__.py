from flask import Flask
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from Lendigo.config import Config
import pymysql
from Lendigo.flask_celery import make_celery
pymysql.install_as_MySQLdb()

    
app = Flask(__name__)
app.config.from_object(Config)
db =  SQLAlchemy(app)
celery = make_celery(app)



from Lendigo.models import Item #after running on first instance these can be deleted
db.create_all()
db.session.commit()

from Lendigo.errors.handlers import errors
app.register_blueprint(errors)

from Lendigo import routes