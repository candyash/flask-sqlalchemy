from datetime import datetime
from flask import request, current_app
from . import db
from hashlib import md5


friend_tag = db.Table('friend_tag', db.Column('user_id', db.Integer,
                      db.ForeignKey('users.id')), db.Column('friend_id',
                      db.Integer, db.ForeignKey('friends.id'), unique=True))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), default="None", nullable=False)
    age = db.Column(db.Integer, default=20, nullable=False)
    email = db.Column(db.String(64),
                      nullable=False, unique=True)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    tag = db.relationship("Friend", secondary=friend_tag,
                          backref=db.backref('friend_tag', lazy='dynamic'),
                          cascade="all, delete-orphan", single_parent=True)

    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return "<User(name = '%s', email = '%s')>" % (self.name, self.email)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() \
            + '?d=monsterid&s=' + str(size)

    def best_f(self):
        b_friend = Friend.best(self.id)
        return b_friend

    def f_count(self):
        friend_count = Friend.for_count(self.id)
        return friend_count
    def f_tag(self,f):
        _tag=self.tag.append(f)
        return _tag
        


class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    friend_account = db.Column(db.Integer)
    approved = db.Column(db.Boolean, default=False)
    bestfriend = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __init__(self, friend_account, approved, bestfriend):
        self.friend_account = friend_account
        self.approved = approved
        self.bestfriend = bestfriend

    def __repr__(self):
        return '<friend account {}'.format(self.friend_account)

    @staticmethod
    def best(id_user):
        f_account = []
        check = Friend.query.join(User.tag).filter(User.id == id_user).\
            filter_by(bestfriend = True)
        if check:
            for i in check:
                f_account.append(i.friend_account)
        m_best = User.query.filter(User.id.in_(f_account)).first()
        return m_best

    @staticmethod
    def for_count(id_user):
        f_count = Friend.query.join(User.tag).filter(User.id == id_user).\
            filter_by(approved = True)
        return f_count
    
