from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request, current_app
from flask.ext.login import UserMixin
from . import db, login_manager
from hashlib import md5
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper



Base = declarative_base()


class User(UserMixin, db.Model,Base):
    __tablename__ = 'users'

    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),
                      nullable=False, unique=True, index=True)
    username = db.Column(db.String(64),
                         nullable=False, unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    user_info=db.relationship('PersonalInfo' ,uselist=False,backref='users')
    friends=db.relationship('Friend', lazy='dynamic', backref='friends')
    
    def for_approval(self, admin=False):
        if admin :
            return Friend.for_approval(self.id)
    def approved(self):
        return self.friend.filter_by(approved=True)
    def get_api_token(self,expiration=5000 ):
        s=Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user':self.id}).decode('utf-8')
    def validate_api_token(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return None
        id=data.get('user')
        if id:
            return User.query.get(id)
        return
    def friend_status(self, fid):
        return Friend.friendStatus(self.id,fid)
    
    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.username)
    
    
        
 
    
    @property
    def password(self):
        raise AttributeError('password is not a readable')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
  
class PersonalInfo(db.Model, Base):
    __tablename__= 'user_info'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(30))
    last_name=db.Column(db.String(30))
    age=db.Column(db.Integer)
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
   
     
    
class Friend(db.Model, Base):
    __tablename__ = 'friends'
    id=db.Column(db.Integer,primary_key=True )
    user_account=db.Column(db.Integer)
    friend_account=db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved=db.Column(db.Boolean, default=False)
    status=db.Column(db.Boolean, default=False)
    bestFriend=db.relationship('BestFriend' ,uselist=False, lazy='joined', backref='bestfriend', cascade="all, delete, delete-orphan")
    
    
    @staticmethod
    def for_approval(userId):
        return Friend.query.filter(Friend.approved==False).filter(Friend.friend_account==userId)
    @staticmethod
    def friendStatus(userId, fid):
        return Friend.query.filter(Friend.status==True).filter(Friend.approved==True).\
        filter(Friend.user_account==userId).filter(Friend.friend_account==fid)
    
class BestFriend(db.Model, Base):
    __tablename__ = 'bestfriend'
    id=db.Column(db.Integer,primary_key=True )
    best_friend=db.Column(db.Boolean, default=False)
    friend_id=db.Column(db.Integer, db.ForeignKey('friends.id'))
    
    
    
    


    
    

    


   

    


 

  

