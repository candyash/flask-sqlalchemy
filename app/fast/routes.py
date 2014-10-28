from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask.ext.login import login_required, current_user
from ..import db
from ..models import User, PersonalInfo, Friend
from . import fast
from .forms import ProfileForm, PresenterCommentForm, CommentForm, RegisterForm
from config import Config
from flask.ext.sqlalchemy import Pagination
from app.connection import con


@fast.route("/", defaults={"page": 1})
@fast.route("/")
def index():
  
    if current_user.is_authenticated():
        """To list all users"""
      
        page=request.args.get("page", 1, type=int)
        pagination=PersonalInfo.query.join(User.user_info).filter(User.id!=current_user.id).order_by(PersonalInfo.member_since.asc())\
            .paginate(page, per_page=current_app.config["USER_PER_PAGE"],error_out=False)
        user_list=pagination.items
   
    return render_template("fast/index.html",pagination=pagination,user=user_list)


@fast.route("/user/<username>")
def user(username):
    
    """initializing presonalinfo for the current user"""
    user=User.query.get(current_user.id)
    personal=PersonalInfo.query.filter(PersonalInfo.user_id==current_user.id).first()
   
    
    if personal is None:   
        userinfo=PersonalInfo(first_name='***',last_name='***',age=0,location='***',bio='**',user_id=current_user.id)
        db.session.add(userinfo)
        db.session.commit()
        flash("Please update your profile")
        return redirect(url_for("fast.profile"))
    
    return render_template('fast/user.html', user=user,personal=personal)

@fast.route("/Register", methods=["GET","POST"])
def Register():
    """Register a new user."""
    form=RegisterForm()
   
        
    try:
            
        if request.method=="POST" and form.validate_on_submit():
            email=form.email.data
            username=form.username.data
            password=form.password.data
            user=User(email=email,username=username,is_admin=False,password=password)
            db.session.add (user)
            db.session.commit()
            flash("User {0} was registered successfully.".format(username))
        
        
            return redirect(url_for("auth.login"))
    except:
        flash("Error is found. The user already registerd to the system!")
    return render_template("fast/Register.html",form=form)

@fast.route('/profile', methods=['GET','POST'])
@login_required
def profile():

   
    form =ProfileForm()
   
    
    if form.validate_on_submit():
        
        
        current_user.user_info.first_name=form.firstName.data
        current_user.user_info.last_name=form.lastName.data
        current_user.user_info.age=form.Age.data
        current_user.user_info.location=form.location.data
        current_user.user_info.bio=form.bio.data
        current_user.user_info.user_id=current_user.id
        db.session.add(current_user.user_info)
        db.session.commit()
        flash("You have been updated your profile")
     
        return redirect(url_for('fast.user', username=current_user.username))
    
    if current_user.user_info:
        form.firstName.data=current_user.user_info.first_name
        form.lastName.data=current_user.user_info.last_name
        form.location.data=current_user.user_info.location
        form.Age.data=current_user.user_info.age
        form.bio.data=current_user.user_info.bio
            
            
            
            
    return render_template('fast/profile.html', form=form)

@fast.route("/userlist", defaults={"page": 1})
@fast.route("/userlist", methods=['GET','POST'])

def userlist():
    """user list in the system"""
    page=request.args.get("page", 1, type=int)
    if current_user.user_info is None:
        flash("Please update your profile to see more Monkeys!")
        return redirect(url_for("fast.index"))
   
    pagination=PersonalInfo.query.join(User.user_info).filter(User.id!=current_user.id).join(User.tag).filter(User.id==current_user.id).paginate(page, per_page=current_app.config["USER_PER_PAGE"],error_out=False)
    userlist=pagination.items
    
    return render_template("fast/userlist.html",userlist=userlist, pagination=pagination )

@fast.route("/friendadd", methods=["GET","POST"])
def friendadd():
    """accepting friend request"""
    id_friend=request.args.get('id', type=int)
    userid=current_user.id   
   
    q=Friend.query.join(User.tag).filter(Friend.friend_account==id_friend).filter(User.id==userid).first()

        
    if q is None:
       
        f=Friend(friend_account=id_friend,approved=False,bestfriend=False)
        db.session.add(f)
        db.session.commit()
        
        tag=current_user.tag.append(f)
     
        db.session.commit()
        
        flash("Thank you! You sent friend request!!")
        return redirect(url_for("fast.index"))
    else:
              
        flash("Remember you sent friend request!")
            
        return redirect(url_for("fast.userlist")) 

@fast.route("/friendrequest")
@login_required
def friendrequest():
  

    if current_user.is_authenticated:
            
  
        pinfo=PersonalInfo.query.join(User.user_info).join(User.tag).filter(Friend.friend_account==current_user.id).filter(Friend.approved==False)
        
    return render_template ("fast/friendrequest.html",pinfo=pinfo)


@fast.route("/confirm", methods=["GET","PUT"])
def confirm():
    
    """friend confirmation"""
    
    id_confirm=request.args.get("id", type=int)
    userid=current_user.id
  
    f_confirm=Friend.query.filter(Friend.friend_account==userid).filter(Friend.approved==False).filter(User.id==id_confirm).first()
    
    
    if not f_confirm.approved:
        
            f_confirm.approved=True
            db.session.add(f_confirm)
            db.session.commit()
            flash("Thank you accepting the friend request!")
            return redirect(url_for('fast.index'))
    
            flash('Error! Nothing added to the database!')
        
        
    else:
        flash("your friendship confirmed")
    return redirect(url_for("fast.index"))

@fast.route("/delete/<int:id>", methods=["GET","DELETE"])
def delete(id):
    
    """rejecting friend request"""
    user=User.query.get_or_404(id)
    q=Friend.query.join(User.tag).filter(User.id==id).filter(Friend.friend_account==current_user.id).first()
   
    try:
        if q:
           
            db.session.delete(q)
            db.session.commit()
            flash("YOU REJECT THE FRIENDSHIP REQUEST!")
            return redirect(url_for("fast.index"))
    except:
        flash("database missing \n")
    return redirect(url_for("fast.friendrequest"))

    
@fast.route("/acceptedFriend", methods=["GET","POST"])
def acceptedFriend():
    
    """accepted friend list"""
    
    userid=current_user.id
    
    f=User.query.join(User.tag).first()
    
    if f is None:
        flash('Please add monkey! Now you don\'t have friend')
        return redirect(url_for('fast.userlist'))
  
    
    '''To check best friend check'''
    bfriend=False
    befriend=Friend.query.join(User.tag).filter(Friend.friend_account==userid).filter(Friend.bestfriend==True)

    for i in befriend:
        if i.bestfriend:
            bfriend=True
    accepted_friends=PersonalInfo.query.join(User.user_info).join(User.tag).filter(Friend.friend_account==userid).filter(Friend.approved==True).filter(Friend.bestfriend==False).all()
 
    #accepted_other=PersonalInfo.query.join(User.user_info).join(User.tag).filter(User.id==userid).filter(Friend.approved==True).all()
    accepted_other=[] 
    return render_template('fast/acceptedFriend.html',accepted_friends=accepted_friends,bfriend=bfriend,accepted_other=accepted_other)
  
@fast.route('/bestFriend', methods=['GET','POST'])
def bestFriend():
    
    """best friend add"""
    
    id_friend=request.args.get('id', type=int)
   
    userid=current_user.id
    q=Friend.query.join(User.tag).filter(Friend.friend_account==userid).filter(User.id==id_friend).first()
   
    if q.bestfriend:
        
        flash('Sorry! you already have one best friend')
        return redirect(url_for('fast.bestFriendList'))
    else:
        q.bestfriend=True
        db.session.add(q)
        db.session.commit()
        flash('Thank You! You are having Best Friend! ')
        
        return redirect(url_for('fast.index'))

@fast.route('/unFriend',methods=['GET','DELETE'])
def unFriend():
    
    """deleting friend from friendship list"""
   
    id_friend=request.args.get('id', type=int)
    account=User.query.get_or_404(id_friend)
    if account:
        try:
            f_account=Friend.query.join(User.tag).filter(Friend.friend_account==current_user.id).filter(User.id==id_friend).first()
            db.session.delete(f_account)
            db.session.commit()
            flash('You are Unfriend!')
        except:
            flash("database missing!! \n")
        return redirect(url_for('fast.acceptedFriend'))
    else:
        flash('User not found!')
        return redirect(url_for('fast.acceptedFriend'))
    return redirect(url_for('fast.index'))   
      
@fast.route('/bestFriendList')
def bestFriendList():
    
    """best friend list if there is best friend for the current user """
    
    userid=current_user.id
    
    best_f=User.query.join (User.tag).filter(Friend.friend_account==userid).filter(Friend.bestfriend==True).first()
   
    if best_f is None:
        flash('Please add Best Friend or add Friend first')
        return redirect(url_for('fast.index'))
      
       
    else:
        userid=best_f.id
        bestList=PersonalInfo.query.join(User.user_info).filter(PersonalInfo.user_id==userid)
       
          
    
    return render_template ('fast/bestFriendList.html', bestList=bestList)

@fast.route('/cancel', methods=['GET','POST'])
def cancelbestfriend ():
    
    """deleting best frendship"""

    id_friend=request.args.get('id', type=int)
    userid=current_user.id
    best_f=Friend.query.join (User.tag).filter(Friend.friend_account==userid).filter(Friend.bestfriend==True).first()
    best_f.bestfriend=False
    db.session.add(best_f)
    db.session.commit()
    flash('Best Friend canceled!')

    return redirect(url_for('fast.index'))
    
@fast.route('/follower', methods=['GET','POST'])
def follower():
    """adding follower"""
  
    id_follower=request.args.get('id', type=int)
    userid=current_user.id
    follower=User.query.get(id_follower)
    currentuser=User.query.get(userid)
    
    q=follower.followed.filter(User.id==userid).first()
    
    
    if q is None:
        f=follower.followed.append(currentuser)
        db.session.commit()
        flash('Thankyou! you are following {0}'.format(follower.username))
        return redirect(url_for('fast.followerlist'))
    else:
    
        flash('Sorry! You are already following {0}'.format(follower.username))
        return redirect(url_for('fast.followerlist'))
   
    return redirect(url_for('fast.index'))

@fast.route('/followerlist', methods=['GET','POST'])
def followerlist():
    
    """"follower list"""
  
    userid=current_user.id
    follower=User.query.get(userid)
    f_list=f=follower.followed.all()
    
    return render_template('fast/follow.html',f_list=f_list)
    
@fast.route('/unfollow', methods=['GET','DELETE'])
def unfollow():
    """"Unfollow"""
    id_follower=request.args.get('id', type=int)
    userid=current_user.id
    follower=User.query.get(userid)
    currentuser=User.query.get(id_follower)
    
    f_list=f=follower.followed.all()
    
    check=False
    for i in f_list:
        flash('{0}'.format(i.id))
        if id_follower==i.id:
            check=True
    
    if check:
        f=follower.followed.remove(currentuser)
        db.session.commit()
        flash('You are unfollow {0}'.format(currentuser.username))
        return redirect(url_for('fast.followerlist'))
    return redirect(url_for('fast.index'))
    



    






    
    
    
   
    
    
    
    
    
    
