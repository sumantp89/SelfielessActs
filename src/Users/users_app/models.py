from users_app import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True, unique = True)

    def __repr__(self):
        return 'Id: {}, CategoryName: {}'.format(self.id, self.name)