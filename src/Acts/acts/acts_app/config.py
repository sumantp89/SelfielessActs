import os

base_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.join(os.path.join(base_dir, '..'), '..')
migrations_dir = os.path.join(root_dir, 'db_migrations')

class Config(object):
    # app.db is created in db_migrations folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(migrations_dir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
