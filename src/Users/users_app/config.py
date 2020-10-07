import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join( os.path.join(base_dir, '..'), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
