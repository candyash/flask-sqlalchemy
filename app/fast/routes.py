from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask.ext.login import login_required, current_user
from ..import db
from ..models import User, PersonalInfo, Friend,BestFriend
from . import fast
from .forms import ProfileForm, PresenterCommentForm, CommentForm, RegisterForm
from sqlalchemy.orm import sessionmaker
from config import Config
from flask.ext.sqlalchemy import Pagination
from app.connection import con


@fast.route('/', defaults={'page': 1})
@fast.route('/<int:page>')
def index(page):
    try:
    
        page=request.args.get('page', 1, type=int)
        pagination=PersonalInfo.query.order_by(PersonalInfo.member_since.asc())\
        .paginate(page, per_page=current_app.config['USER_PER_PAGE'],error_out=False)
        #if current_user.is_authenticated():
          # user_list= con.execute('select * from user_info where id!=%d'%current_user.id )
          # return render_template('fast/index.html',pagination=pagination,user_list=user_list)
        #user_list= con.execute('select * from user_info')
        #pagination=Pagination(userlist,page, per_page=current_app.config['USER_PER_PAGE'],error_out=False) 
        user_list=pagination
    except:
        flash('data not found')
    
   
   
    
   
    return render_template('fast/index.html',pagination=pagination,user_list=user_list)


@fast.route('/user/<username>')
def user(username):
    user=[]
    personal=[]
    try:
        
        user=User.query.filter_by(username=username).first_or_404()
        personal=PersonalInfo.query.filter_by(user_id=user.id).first()
        
       
        if personal is None:
            
            flash('Please update your profile')
            return redirect(url_for('fast.profile'))
    except:
        flash("Error found!")
        
  
    
    return render_template('fast/user.html', user=user,personal=personal)

@fast.route('/Register', methods=['GET','POST'])
def Register():
    """Register a new user."""
    form=RegisterForm()
    if request.method=='POST' and form.validate_on_submit():
        
        try:
            email=form.email.data
            username=form.username.data
            password=form.password.data
            user=User(email=email,username=username,is_admin=False,password=password)
            db.session.add(user)
            db.session.commit()
            flash('User {0} was registered successfully.'.format(username))
        
            return redirect(url_for('fastlog.login'))
        except:
            flash('Error is found. The user already registerd to the system!')
    return render_template('fast/Register.html',form=form)

@fast.route('/profile', methods=['GET','POST'])
@login_required

def profile():
    form =ProfileForm()
    
    if form.validate_on_submit():
        try:

            first_name=form.firstName.data
            last_name=form.lastName.data
            age=form.Age.data
            location=form.location.data
            bio=form.bio.data
            user_id=current_user.id
            profile=PersonalInfo(first_name,last_name,age,location,bio,user_id)
            db.session.add(profile)
            db.session.commit()
        except:
            flash("Error! User is not registred!")

        return redirect(url_for('fast.user', username=current_user.username))
        #data=PersonalInfo.query(user_id=current_user.id).first()
      
        form.firstName.data=first_name
        form.lastName.data=last_name
        form.Age.data=age
        form.location.data=location
        form.bio.data=bio
    return render_template('fast/profile.html', form=form)
@fast.route('/userlist', methods=['GET','POST'])

def userlist():
    
    if current_user.user_info is None:
        flash('Please update your profile to see more Monkeys!')
        return redirect(url_for('fast.profile'))
    sql='WITH u_info AS (SELECT friend_account FROM friends  WHERE user_id=%d AND approved=%s)\
        SELECT * FROM user_info WHERE user_id IN(SELECT * FROM u_info)'
    #userlist=PersonalInfo.query.join(User.user_info).join(User.friend).filter(Friend.status==False).filter(User.id!=current_user.id)
    userl= con.execute(sql%(current_user.id,False ))
    sql_b='SELECT * FROM user_info WHERE user_id!=%d'
    userlist=con.execute(sql_b%current_user.id)
    
    return render_template('fast/userlist.html',userlist=userlist )

@fast.route('/friendadd', methods=['GET','POST'])
def friendadd():
    id_friend=request.args.get('id', type=int)
    user_id=current_user.id
    try: 
        #retrive user information
        s='SELECT first_name, last_name FROM user_info WHERE user_id=%d'
        user_add=con.execute(s%(user_id)).first()
        
        #q=Friend.query.filter(Friend.friend_Account==user.id).filter(Friend.user_id==current_user.id).first()
        sql="SELECT friends.id FROM friends WHERE ( user_account=%d) AND (friend_account=%d)"
    
        q= con.execute(sql%(user_id,id_friend)).first()
        
      
        
        if q is None:
    
            f=Friend()
            f.user_account=current_user.id
            f.friend_account=id_friend
            f.user_id=current_user.id
            f.approved=False
            f.status=True      
            db.session.add(f)
            db.session.commit()
            flash('Thank you! You sent friend request!!')
        else:
              
            flash('Remember you sent friend request!')
            #q=Friend.query.filter(Friend.friend_Account==user.id).filter(Friend.user_id==current_user.id).filter(Friend.status==1).first()
         
      
        add_friend=con.execute('select user_info.user_id, user_info.first_name, user_info.last_name, user_info.age FROM user_info \
                               JOIN friends ON user_info.user_id=friends.user_id where friends.user_account=%d'%id_friend)
    

        return render_template('fast/friend_add.html',add_friend=add_friend)
    except:
        flash('Error')
        return redirect(url_for('fast.index'))


@fast.route('/friendrequest')
@login_required
def friendrequest():
  
  

    if current_user.is_authenticated:
            
        sql='WITH f_a As (select user_id from friends where friend_account =%d and approved=%s) \
                                        select * from user_info where user_id IN (select * from f_a)'
            # q=Friend.query.filter(Friend.approved==False).filter(Friend.user_account==current_user.id).first()
        pinfo=con.execute(sql%(current_user.id,False))
        #for i in pinfo.:
           # flash('{0}'.format(pinfo))
            
    
  
    return render_template ('fast/friendrequest.html',pinfo=pinfo)


@fast.route('/confirm', methods=['GET','PUT'])
def confirm():
    id_confirm=request.args.get('id', type=int)
    userid=current_user.id
    sql='SELECT * FROM friends WHERE user_id=%d AND friend_account=%d'
    f_confirm=con.execute(sql%(current_user.id, id_confirm)).fetchone()

    
    
    
    if f_confirm is None:
        
        try: 
            sql="UPDATE friends SET approved=%s WHERE user_id=%d AND friend_account=%d"
            con.execute(sql%(True,userid, id_confirm))
            flash('Thank you accepting the friend request!')
            return redirect(url_for('fast.index'))
        except:
            flash('Error! Nothing added to the database!')
        
        
    else:
        flash('your friendship confirmed')
        return redirect(url_for('fast.index'))
    
@fast.route('/delete/<int:id>', methods=['GET','DELETE'])
def delete(id):
    account=Friend.query.get_or_404(id)
    try:
        if account.approved:
            flash('The account is Deleted!!!')
            return redirect(url_for('fast.index'))
        account.approved=False
        db.session.delete(account)
        db.session.commit()
        flash('YOU REJECT THE FRIENDSHIP REQUEST!')
    except sqlite3.OperationalError:
        flash("database missing \n")
    return redirect(url_for('fast.friendrequest'))
@fast.route('/acceptedFriend', methods=['GET','POST'])
def acceptedFriend():
    userid=current_user.id
    sql='SELECT friend_account FROM friends WHERE user_id=%d'
    f=con.execute(sql%userid).first()
    
    #f=Friend.query.filter(Friend.user_id==current_user.id).filter(Friend.approved==True).first()
    if f is None:
        flash('Please add monkey! Now you don\'t have friend')
        return redirect(url_for('fast.userlist'))
    sql='WITH f_a As (select friend_account from friends where user_id =%d and approved=%s) \
                                        select * from user_info where user_id IN (select * from f_a)'
    accepted_friends=con.execute(sql%(userid,True))
    
    
      
    return render_template('fast/acceptedFriend.html',accepted_friends=accepted_friends)
  
@fast.route('/bestFriend', methods=['GET','POST'])
def bestFriend():
    id_friend=request.args.get('id', type=int)
    #user=User.query.get_or_404(id)
    #d=Friend.query.filter(Friend.friend_Account==user.id).filter(Friend.user_id==current_user.id).first()
    #faccount=Friend.query.join(Friend.bestFriend).filter(BestFriend.best_friend==True).filter(Friend.user_account==current_user.id).filter(Friend.friend_Account==user.id).first()
    sql='SELECT friends.id,bestfriend.best_friend FROM bestfriend JOIN friends ON bestfriend.friend_id=friends.id WHERE friend_account=%d'
    best_f=con.execute (sql%id_friend).first()
    #lash('{0}'.format(best_f.best_friend))
   
    
    if not best_f :
       
        try:   
            sql_b='UPDATE  bestfriend SET best_friend =%s WHERE friend_id=%d'
            b_account=con.execute(sql_b%(True, best_f.id))
            flash('Now you are best friend with him/her')
      
            sql_bf='SELECT * FROM user_info WHERE user_id=%d'
            bestList=con.execute(sql_bf%id_friend)
       
           
        except:
            flash('Error!')
        
        return redirect(url_for('fast.bestFriendList'))
   
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
    except Sqlite.OperationalError:
        flash("database missing!! \n")
    return redirect(url_for('fast.acceptedFriend'))
    
      
@fast.route('/bestFriendList')
def bestFriendList():
    userid=current_user.id
    sql='SELECT bestfriend.best_friend, bestfriend.friend_id FROM bestfriend JOIN friends ON bestfriend.friend_id=friends.friend_account WHERE user_id=%d'
    best_f=con.execute (sql%userid).first()
    #best=Friend.query.join (Friend.bestFriend).filter(Friend.user_account==current_user.id).filter(BestFriend.best_friend==True).first()
    if best_f is None :
        flash('Please add Best Friend or add Friend first')
        return redirect(url_for('fast.acceptedFriend'))
      
       
    else:
          #bestList=PersonalInfo.query.join(User.user_info).filter(User.id==best.friend_Account)
          f_id=best_f.friend_id
          sql_b='SELECT * FROM user_info WHERE user_id=%d'
          bestList=con.execute(sql_b%f_id)
        
        
    
    
    return render_template ('fast/bestFriendList.html', bestList=bestList)
    
    



    






    
    
    
   
    
    
    
    
    
    
