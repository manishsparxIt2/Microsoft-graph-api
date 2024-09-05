import os
from urllib import parse
password = 'admin@123'
DB_USER =  'postgres'
DB_PASSWORD =parse.quote(password)
DB='postgres'
DB_URL ='localhost'

DB_CONNECT = 'postgresql+pg8000://{username}:{password}@{localhost}/{dbname}'.format(username=DB_USER,password=DB_PASSWORD,localhost=DB_URL,dbname=DB)
print(DB_CONNECT)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI =DB_CONNECT
SQLALCHEMY_TRACK_MODIFICATIONS = False
search_words = ["payment" ,"investmen" ,"cover up" ,"write off" ,"grey area" ,"special fees" ,"no inspection" ,"do not volunteer information"]
threshold =  80