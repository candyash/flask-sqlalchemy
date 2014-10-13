from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request, current_app
from flask.ext.login import UserMixin
from . import db
from hashlib import md5


friend_tag = db.Table('friend_tag',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('friends.id'), unique=True)
)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)



class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),
                      nullable=False, unique=True, index=True)
    username = db.Column(db.String(64),
                         nullable=False, unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    user_info=db.relationship('PersonalInfo' ,uselist=False,backref='users')
    last_seen = db.Column(db.DateTime)
    tag = db.relationship("Friend",
                secondary=friend_tag,
                backref=db.backref('friend_tag', lazy='dynamic'),
                lazy='dynamic',cascade="save-update, merge, delete"
                
                )
    
    followed = db.relationship('User', 
                               secondary=followers, 
                               primaryjoin=(followers.c.follower_id == id), 
                               secondaryjoin=(followers.c.followed_id == id), 
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')
    
    
    def __init__(self, email, username, is_admin,password):
        self.email=email
        self.username=username
        self.is_admin=is_admin
        self.password_hash=generate_password_hash(password)
   
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == users.id).count() > 0
        
       
    
      
    def __repr__(self):
        return "<User(email='%s', username='%s')>" %(self.email, self.username)
    

    
    
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

  
class PersonalInfo(db.Model):
    __tablename__= 'user_info'
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(30))
    last_name=db.Column(db.String(30))
    age=db.Column(db.Integer)
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
   

      
    def __repr__(self):
        return "<User Info(FirstName='%s', LastName='%s')>" %(self.first_name, self.last_name)
   
     
    
class Friend(db.Model):
    __tablename__ = 'friends'
    id=db.Column(db.Integer,primary_key=True )
    friend_account=db.Column(db.Integer)
    approved=db.Column(db.Boolean, default=False)
    bestfriend=db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
   
    
    def __init__(self, friend_account,approved,bestfriend):
        self.friend_account=friend_account
        self.approved=approved
        self.bestfriend=bestfriend
    def __repr__(self):
        return '<sent request {}'.format(self.friend_account)
    
    @staticmethod
    def for_approval(userId):
        return Friend.query.filter(Friend.approved==False).filter(Friend.friend_account==userId)
    
    

    
    
    
    


    
    

    


   

    


 

  

