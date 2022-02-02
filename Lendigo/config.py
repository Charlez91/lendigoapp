import os
from dotenv import load_dotenv

load_dotenv()


class Config:
	SECRET_KEY = os.getenv('SECRET_KEY')
	#SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
	CELERY_BROKER_URL = 'redis://:pb3305f7b66504d9e8999ff6a3838fad816a3a8f6644b267a4ee62408387353c2@ec2-34-250-150-188.eu-west-1.compute.amazonaws.com:8620'
	CELERY_RESULT_BACKEND = 'db+mysql://root:charles@127.0.0.1/lendigo_async'
