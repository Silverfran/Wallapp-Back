from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(120), nullable=False)
    lastName = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    comment_id = db.relationship('Comment', cascade="all,delete", backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.firstName + " " + self.lastName}>'

    def serialize(self):
        return {
            "id": self.id,
            "firstName": self.firstName,
            "lastName": self.lastName,
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Comment {self.comment}>'
        
    def serialize(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "user_id": self.user_id
        }