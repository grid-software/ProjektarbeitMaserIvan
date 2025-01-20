import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/dbname'  # Ersetzen Sie dies mit Ihren MySQL-Zugangsdaten
    SQLALCHEMY_TRACK_MODIFICATIONS = False