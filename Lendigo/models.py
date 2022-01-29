from Lendigo import db
from datetime import datetime


class Item(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    by = db.Column(db.String(150), nullable= True)
    item_hnid = db.Column(db.Float, unique = True, nullable= False)
    title = db.Column(db.String(300))
    time = db.Column(db.DateTime)
    text = db.Column(db.Text)
    item_type = db.Column(db.String(100))
    url = db.Column(db.String(150))
    score = db.Column(db.Integer)
    descendants = db.Column(db.Integer)
    parents = db.Column(db.Integer)
    kids = db.Column(db.String(500))
    deleted = db.Column(db.Boolean)
    dead = db.Column(db.Boolean)
    apiuser_added = db.Column(db.Boolean)

    def __repr__ (self):
        return f"Item ('{self.by}','{self.item_type}', '{self.item_hnid}', '{self.time}')" 