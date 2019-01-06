from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# the main document store
class Document(db.Model):

    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    document_filename = db.Column(db.Text)
    thumbnail_filename = db.Column(db.Text)
    original_filename = db.Column(db.Text)
    status = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<document %r>' % self.title


class Tag(db.Model):

    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag = db.Column(db.Text)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<tag %r>' % self.tag
