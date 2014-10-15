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
@fast.route("/<int:page>")
def index(page):
    pagination=[]
    user_list=[]
    
    if current_user.is_authenticated():
        """To list all users"""
        page=request.args.get("page", 1, type=int)
        pagination=PersonalInfo.query.join(User.user_info).filter(User.id!=current_user.id).order_by(PersonalInfo.member_since.asc())\
            .paginate(page, per_page=current_app.config["USER_PER_PAGE"],error_out=False)
        user_list=pagination.items
  
      
    
   
    return render_template("fast/index.html",pagination=pagination,user_list=user_list)


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
        return redirect(url_for("fast.profile"))
   
    pagination=PersonalInfo.query.join(User.user_info).filter(User.id!=current_user.id).join(User.tag).filter(User.id==current_user.id).paginate(page, per_page=current_app.config["USER_PER_PAGE"],error_out=False)
    userlist=pagination.items
    
    return render_template("fast/userlist.html",userlist=userlist, pagination=pagination )

@fast.route("/friendadd", methods=["GET","POST"])
def friendadd():
    """accepting friend request"""
    id_friend=request.args.get('id', type=int)
    user_id=current_user.id   
    sql="SELECT * FROM friends JOIN friend_tag ON friends.id=friend_tag.friend_id WHERE user_id=%d AND friend_account=%d"
    q=con.execute(sql%(user_id,id_friend)).first()
   
        
    if q is None:
        current_user.tag.user_id=user_id
        f=Friend(friend_account=id_friend,approved=False,bestfriend=False)
        db.session.add(f)
        db.session.commit()
        currentuser=User.query.get(user_id)
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
            
        sql="WITH f_a As (SELECT friend_tag.user_id FROM friend_tag \
            JOIN friends ON friend_tag.friend_id=friends.id \
            where friends.friend_account =%d and approved=%s) \
                                        select * from user_info where user_id IN (select * from f_a)"
            # q=Friend.query.filter(Friend.approved==False).filter(Friend.user_account==current_user.id).first()
        pinfo=con.execute(sql%(current_user.id,False))
            
    return render_template ("fast/friendrequest.html",pinfo=pinfo)


@fast.route("/confirm", methods=["GET","PUT"])
def confirm():
    
    """friend confirmation"""
    
    id_confirm=request.args.get("id", type=int)
    userid=current_user.id
  
    f_confirm=Friend.query.filter_by(friend_account=userid).filter_by(approved=False).first()
    
    
    if not f_confirm.approved:
        
            trans=con.begin()
            sql="WITH confirm_f AS (SELECT id from friends JOIN friend_tag ON friends.id = friend_tag.friend_id WHERE friend_account=%d AND user_id=%d )\
                UPDATE friends SET approved=%s  WHERE friends.id=(select id from confirm_f)"
            con.execute(sql%(userid,id_confirm, True))
            trans.commit()
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
    sql_a='SELECT * FROM friends JOIN friend_tag ON friends.id=friend_tag.friend_id\
        WHERE friend_account=%d'
    f=con.execute(sql_a%userid).first()

    '''To check best friend check'''
    bfriend=False
    sql_b='SELECT friends.bestfriend FROM friends JOIN friend_tag ON friends.id=friend_tag.friend_id WHERE friend_account=%d'
    befriend=con.execute(sql_b%(userid)).fetchall()
    for i in befriend:
        for j in i:
            if j==True:
                bfriend=True
    
    #f=Friend.query.filter(Friend.user_id==current_user.id).filter(Friend.approved==True).first()
    if f is None:
        flash('Please add monkey! Now you don\'t have friend')
        return redirect(url_for('fast.userlist'))
    sql_c='WITH f_a As (select user_id from friends JOIN friend_tag ON friends.id=friend_tag.friend_id WHERE approved=%s AND friend_account=%d) \
                                        select * from user_info where user_id IN (select * from f_a)'
    accepted_friends=con.execute(sql_c%(True, userid))
    
    '''Accepted from friend side'''
    sql_d='WITH f_a As (select friend_account from friends JOIN friend_tag ON friends.id=friend_tag.friend_id WHERE approved=%s AND user_id=%d) \
                                        select * from user_info where user_id IN (select * from f_a)'
    accepted_other=con.execute(sql_d%(True, userid))

  
      
    return render_template('fast/acceptedFriend.html',accepted_friends=accepted_friends,bfriend=bfriend,accepted_other=accepted_other)
  
@fast.route('/bestFriend', methods=['GET','POST'])
def bestFriend():
    
    """best friend add"""
    
    id_friend=request.args.get('id', type=int)
   
    userid=current_user.id
    sql_a='SELECT friends.bestfriend from friends JOIN friend_tag  ON friends.id=friend_tag.friend_id WHERE friend_tag.user_id=%d AND friends.friend_account=%d'
    q=con.execute(sql_a%(id_friend,userid)).first()
    
    if not q[0] :
       
        
        trans=con.begin()
        sql_b="WITH confirm_f AS (SELECT id from friends JOIN friend_tag ON friends.id = friend_tag.friend_id WHERE friend_account=%d AND user_id=%d )\
                UPDATE friends SET bestfriend=%s  WHERE friends.id=(select id from confirm_f)"
          
        b_account=con.execute(sql_b%(userid,id_friend,True))
        trans.commit()
        flash('Thank You! You are having Best Friend! ')
        
        return redirect(url_for('fast.index'))
   
    else:
        flash('Sorry! you already have one best friend')
        return redirect(url_for('fast.bestFriendList'))

@fast.route('/unFriend',methods=['GET','DELETE'])
def unFriend():
    
    """deleting friend from friendship list"""
    
    id_friend=request.args.get('id', type=int)
    account=User.query.get_or_404(id_friend)
    if account:
        try:
            #faccount=Friend.query.filter(Friend.friend_Account==account.id).filter(Friend.user_account==current_user.id).first()
            #fbest=BestFriend.query.filter(BestFriend.friend_id==faccount)
            trans=con.begin()
            sql_a='delete from friend_tag where friend_id IN (select id from friends join friend_tag ON friends.id=friend_tag.friend_id where user_id=%d and friend_account=%d)'
            
            con.execute(sql_a%(id_friend, current_user.id))
            sql_b='delete from friends where id IN (select id from friends join friend_tag ON friends.id=friend_tag.friend_id where user_id=%d and friend_account=%d)'
            con.execute(sql_b%(id_friend, current_user.id))
            trans.commit()
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
    sql='SELECT friend_account, user_id FROM friends JOIN friend_tag ON friends.id=friend_tag.friend_id WHERE friend_account=%d AND bestfriend=%s'
    best_f=con.execute (sql%(userid,True)).first()
    #best=Friend.query.join (Friend.bestFriend).filter(Friend.user_account==current_user.id).filter(BestFriend.best_friend==True).first()
    if best_f is None :
        flash('Please add Best Friend or add Friend first')
        return redirect(url_for('fast.index'))
      
       
    else:
          #bestList=PersonalInfo.query.join(User.user_info).filter(User.id==best.friend_Account)
          f_id=best_f['user_id']
          sql_b='SELECT * FROM user_info WHERE user_id=%d'
          bestList=con.execute(sql_b%f_id)
    
    return render_template ('fast/bestFriendList.html', bestList=bestList)

@fast.route('/cancel', methods=['GET','POST'])
def cancelbestfriend ():
    
    """deleting best frendship"""
    
    id_friend=request.args.get('id', type=int)
    userid=current_user.id
    trans=con.begin()
    sql="WITH confirm_f AS (SELECT id from friends JOIN friend_tag ON friends.id = friend_tag.friend_id WHERE friend_account=%d AND user_id=%d )\
                UPDATE friends SET bestfriend=%s  WHERE friends.id=(select id from confirm_f)"
    b_account=con.execute(sql%(userid,id_friend,False))
    trans.commit()
    flash('Best Friend deleted!')

    return redirect(url_for('fast.index'))
    
@fast.route('/follower', methods=['GET','POST'])
def follower():
    """adding follower"""
    id_follower=request.args.get('id', type=int)
    userid=current_user.id
    follower=User.query.get(id_follower)
    currentuser=User.query.get(userid)
    sql='SELECT follower_id FROM followers where followed_id=%d'
    if len(q)==0:
        f=follower.followed.append(currentuser)
        db.session.commit()
        flash('Thankyou! you are following {0}'.format(follower.username))
        return redirect(url_for('fast.followerlist'))
    else:
    
        check=False
        for i in q:
            
            
            if id_follower!=i[0] :
                check=True
        
        if check or q is None:
            f=follower.followed.append(currentuser)
            db.session.commit()
            flash('Thankyou! you are following {0}'.format(follower.username))
            return redirect(url_for('fast.followerlist'))
    flash('Sorry! You are already following {0}'.format(follower.username))
    return redirect(url_for('fast.index'))

@fast.route('/followerlist', methods=['GET','POST'])
def followerlist():
    
    """"follower list"""
    sql='With f_a AS (SELECT follower_id FROM followers where followed_id=%d) SELECT users.id, users.username, users.email FROM users WHERE users.id IN (SELECT * FROM f_a)'
    f_list=con.execute(sql%(current_user.id))
    return render_template('fast/follow.html',f_list=f_list)
    
@fast.route('/unfollow', methods=['GET','DELETE'])
def unfollow():
    """"Unfollow"""
    id_follower=request.args.get('id', type=int)
    userid=current_user.id
    follower=User.query.get(id_follower)
    currentuser=User.query.get(userid)
    sql='SELECT follower_id FROM followers where followed_id=%d'
    q=con.execute(sql%(userid ))
    check=False
    for i in q:
        
        if id_follower==i[0]:
            check=True
    
    if check:
        f=follower.followed.remove(currentuser)
        db.session.commit()
        flash('You are unfollow {0}'.format(current_user.username))
        return redirect(url_for('fast.followerlist'))
    
    



    






    
    
    
   
    
    
    
    
    
    
