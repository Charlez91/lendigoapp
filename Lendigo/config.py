import os
from dotenv import load_dotenv

load_dotenv()


class Config:
	SECRET_KEY = os.getenv('SECRET_KEY')
	#SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
	CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
	CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
