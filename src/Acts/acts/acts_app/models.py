from acts_app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True, unique = True)
    acts = db.relationship('Act', backref = 'curr_category', lazy = 'dynamic')

    def __repr__(self):
        return 'Id: {}, CategoryName: {}'.format(self.id, self.name)

class Act(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    caption = db.Column(db.String(128))
    upvotes = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return 'ActId: {}, User: {}, CategoryName: {}, Caption: {}, upvotes: {}'.format(self.id, self.username, self.curr_category, self.caption, self.upvotes)
