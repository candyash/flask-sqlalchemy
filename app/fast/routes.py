from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask.ext.login import login_required, current_user
from ..import db
from ..models import User, PersonalInfo, Friend
from . import fast
from .forms import ProfileForm, PresenterCommentForm, CommentForm, RegisterForm
from sqlalchemy.orm import sessionmaker
from config import Config
from flask.ext.sqlalchemy import Pagination
from app.connection import con


@fast.route("/", defaults={"page": 1})
@fast.route("/<int:page>")
def index(page):
    
    try:
    
        page=request.args.get("page", 1, type=int)
        pagination=PersonalInfo.query.order_by(PersonalInfo.member_since.asc())\
        .paginate(page, per_page=current_app.config["USER_PER_PAGE"],error_out=False)
        #if current_user.is_authenticated():
          # user_list= con.execute('select * from user_info where id!=%d'%current_user.id )
          # return render_template('fast/index.html',pagination=pagination,user_list=user_list)
        #user_list= con.execute('select * from user_info')
        #pagination=Pagination(userlist,page, per_page=current_app.config['USER_PER_PAGE'],error_out=False) 
        user_list=pagination.items
    except:
        flash("data not found")
    
   
    return render_template("fast/index.html",pagination=pagination,user_list=user_list)


@fast.route("/user/<username>")
def user(username):
    
        
    user=User.query.filter_by(username=username).first_or_404()
    personal=PersonalInfo.query.filter_by(user_id=user.id).first()
        
       
    if personal is None:
            
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
            db.session.add(user)
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
    profileInfo=PersonalInfo()
    if form.validate_on_submit():
        
        profileInfo.first_name=form.firstName.data
        profileInfo.last_name=form.lastName.data
        profileInfo.age=form.Age.data
        profileInfo.location=form.location.data
        profileInfo.bio=form.bio.data
        user_id=current_user.id
        
        db.session.add(profileInfo)
        db.session.commit()
        return redirect(url_for('fast.user', username=current_user.username))
    if current_user.is_authenticated():
        p=PersonalInfo.query.filter_by(user_id=current_user.id).first()
        if p:
        
            form.firstName.data=p.first_name
            form.lastName.data=p.last_name
            form.Age.data=p.age
            form.location.data=p.location
            form.bio.data=p.bio
    return render_template('fast/profile.html', form=form)

@fast.route("/userlist", defaults={"page": 1})
@fast.route("/userlist", methods=['GET','POST'])

def userlist():
    page=request.args.get("page", 1, type=int)
    if current_user.user_info is None:
        flash("Please update your profile to see more Monkeys!")
        return redirect(url_for("fast.profile"))
   
    pagination=PersonalInfo.query.join(User.user_info).filter(User.id!=current_user.id).paginate(page, per_page=current_app.config["USER_PER_PAGE"],error_out=False)
    userlist=pagination.items
    
    return render_template("fast/userlist.html",userlist=userlist, pagination=pagination )

@fast.route("/friendadd", methods=["GET","POST"])
def friendadd():
    id_friend=request.args.get('id', type=int)
    user_id=current_user.id
   
        
    q=Friend.query.get(id_friend)
        
    if q is None:
        f=Friend(approved=False,bestfriend=False,friend_account=id_friend)
        db.session.add(f)
        db.session.commit()
        currentuser=User.query.get(user_id)
        tag=currentuser.tag.append(f)
     
        db.session.commit()
        
        flash("Thank you! You sent friend request!!")
        return redirect(url_for("fast.userlist"))
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
    id_confirm=request.args.get("id", type=int)
    userid=current_user.id
  
    f_confirm=Friend.query.get(id_confirm)
    
    
    if f_confirm is None:
        
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
    account=Friend.query.get_or_404(id)
    try:
        if account.approved:
            flash("The account is Deleted!!!")
            return redirect(url_for("fast.index"))
        account.approved=False
        db.session.delete(account)
        db.session.commit()
        flash("YOU REJECT THE FRIENDSHIP REQUEST!")
    except sqlite3.OperationalError:
        flash("database missing \n")
    return redirect(url_for("fast.friendrequest"))
@fast.route("/acceptedFriend", methods=["GET","POST"])
def acceptedFriend():
    userid=current_user.id
    sql='SELECT * FROM friends JOIN friend_tag ON friends.id=friend_tag.friend_id\
        WHERE friend_account=%d'
    f=con.execute(sql%userid).first()
   
    
    #f=Friend.query.filter(Friend.user_id==current_user.id).filter(Friend.approved==True).first()
    if f is None:
        flash('Please add monkey! Now you don\'t have friend')
        return redirect(url_for('fast.userlist'))
    sql='WITH f_a As (select user_id from friends JOIN friend_tag ON friends.id=friend_tag.friend_id WHERE approved=%s AND friend_account=%d) \
                                        select * from user_info where user_id IN (select * from f_a)'
    accepted_friends=con.execute(sql%(True, userid))

  
      
    return render_template('fast/acceptedFriend.html',accepted_friends=accepted_friends)
  
@fast.route('/bestFriend', methods=['GET','POST'])
def bestFriend():
    id_friend=request.args.get('id', type=int)
    userid=current_user.id
    user=User.query.get_or_404(id_friend)
    sql='SELECT bestfriend, friend_id FROM friends JOIN friend_tag ON friends.id=friend_tag.friend_id \
        WHERE friend_account=%d AND user_id=%d'
    best_f=con.execute (sql%(id_friend,userid)).first()
    flash('{0}'.format(best_f))
   
    
    if  best_f is None:
       
        
        trans=con.begin()
        sql="WITH confirm_f AS (SELECT id from friends JOIN friend_tag ON friends.id = friend_tag.friend_id WHERE friend_account=%d AND user_id=%d )\
                UPDATE friends SET bestfriend=%s  WHERE friends.id=(select id from confirm_f)"
          
        b_account=con.execute(sql%(userid,id_friend,True))
        trans.commit()
        flash('Now you are best friend with him/her')
        
        return redirect(url_for('fast.index'))
   
    else:
        flash('Sorry! you already have one best friend')
        return redirect(url_for('fast.bestFriendList'))

@fast.route('/unFriend',methods=['GET','DELETE'])
def unFriend():
    id=request.args.get('id', type=int)
    account=User.query.get_or_404(id)
    try:
        faccount=Friend.query.filter(Friend.friend_Account==account.id).filter(Friend.user_account==current_user.id).first()
        fbest=BestFriend.query.filter(BestFriend.friend_id==faccount)
        
        db.session.delete(faccount)
        db.session.commit()
        flash('You are Unfriend!')
    except:
        flash("database missing!! \n")
    return redirect(url_for('fast.acceptedFriend'))
    
      
@fast.route('/bestFriendList')
def bestFriendList():
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
    id_friend=request.args.get('id', type=int)
    userid=current_user.id
    trans=con.begin()
    sql="WITH confirm_f AS (SELECT id from friends JOIN friend_tag ON friends.id = friend_tag.friend_id WHERE friend_account=%d AND user_id=%d )\
                UPDATE friends SET bestfriend=%s  WHERE friends.id=(select id from confirm_f)"
    b_account=con.execute(sql%(userid,id_friend,False))
    trans.commit()
    flash('Now you don\'t have best friend!')

    return redirect(url_for('fast.index'))
    

    
    



    






    
    
    
   
    
    
    
    
    
    
