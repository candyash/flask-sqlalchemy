from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask.ext.login import login_required, current_user

from ..import db
from ..models import User, PersonalInfo, Friend,BestFriend
from . import fast
from .forms import ProfileForm, PresenterCommentForm, CommentForm, RegisterForm

@fast.route('/')
def index():
    page=request.args.get('page', 1, type=int)
    pagination=PersonalInfo.query.join(User.user_info).join(User.friend).order_by(Friend.timestamp.asc()).paginate(page, per_page=current_app.config['USER_PER_PAGE'],error_out=False)
    user_list=pagination.items
    return render_template('fast/index.html',pagination=pagination, user_list=user_list)


@fast.route('/user/<username>')
def user(username):
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
            user=User(email=email,username=username,password=password)
            personal=PersonalInfo()
            db.session.add(user)
            db.session.commit()
            flash('User {0} was registered successfully.'.format(username))
        except sqlite3.OperationalError:
            flash ("you don't have database")
        return redirect(url_for('fastlog.login'))
    return render_template('fast/Register.html',form=form)

@fast.route('/profile', methods=['GET','POST'])
@login_required

def profile():
    form =ProfileForm()
    profileInfo=PersonalInfo(users=current_user)
    if form.validate_on_submit():
        try:
        
            current_user.user_info.firstName=form.firstName.data
            current_user.user_info.lastName=form.lastName.data
            current_user.user_info.Age=form.Age.data
            current_user.user_info.location=form.location.data
            current_user.user_info.bio=form.bio.data
            db.session.add(current_user.user_info)
            db.session.commit()
        except sqlite3.OperationalError:
            flash("database missing!!")

        return redirect(url_for('fast.user', username=current_user.username))
    if current_user.is_authenticated():
        p=current_user.user_info.query.filter_by(user_id=current_user.id)
        for j in p:
            form.firstName.data=j.firstName
            form.lastName.data=j.lastName
            form.Age.data=j.Age
            form.location.data=j.location
            form.bio.data=j.bio
    
    
    return render_template('fast/profile.html', form=form)
@fast.route('/userlist', methods=['GET','POST'])

def userlist():
    
    if current_user.user_info is None:
        flash('Please update your profile to see more Monkeys!')
        return redirect(url_for('fast.profile'))
    
    userlist=PersonalInfo.query.join(User.user_info).join(User.friend).filter(Friend.status==False).filter(User.id!=current_user.id)
    

    return render_template('fast/userlist.html',userlist=userlist )

@fast.route('/friendadd', methods=['GET','POST'])
def friendadd():
    id=request.args.get('id', type=int)
    user=User.query.get_or_404(id)
    q=Friend.query.filter(Friend.friend_Account==user.id).filter(Friend.user_id==current_user.id).first()
    
    try:
    
        if q is None:
            f=Friend(friends=current_user)
            if current_user.is_authenticated():
                f.user_account=current_user.id
                f.friend_Account=user.id
                f.status=True
                db.session.add(f)
                db.session.commit()
                flash('Thank you! You sent friend request for {0}'.format(user.username))
                            
    
          
        else:
            flash('Remember you sent friend request for {0}'.format(user.username))
        q=Friend.query.filter(Friend.friend_Account==user.id).filter(Friend.user_id==current_user.id).filter(Friend.status==1).first()
        flash('{0}'.format(q))
    except sqlite3.OperationalError:
        flash("database missing!!")

    return render_template('fast/userlist.html',q=q) 

@fast.route('/friendrequest')
@login_required
def friendrequest():
    q=Friend.query.filter(Friend.approved==False).filter(Friend.user_account==current_user.id).first()
    
    if q is None:
        flash ('Sorry! You don\'t have friend request')
    friends=Friend.query.join(User, User.id==Friend.user_id).filter(Friend.approved==False ).filter(Friend.friend_Account==current_user.id).all()
    pinfo=[]
    for i in friends:
        pinfo=PersonalInfo.query.filter(PersonalInfo.user_id==i.user_account).all()
  
    return render_template ('fast/friendrequest.html',pinfo=pinfo, friends=friends)
@fast.route('/confirm/<int:id>', methods=['GET','PUT'])
def confirm(id):
    account=Friend.query.get_or_404(id)
    
    try:
        if account.approved:
            return flash('your friendship confirmed')
        account.approved=True
        db.session.add(account)
        db.session.commit()
        flash('Thank you accepting the friend request!')
    except sqlite3.OperationalError:
        flash("database missing!!")
    return redirect(url_for('fast.friendrequest'))
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
@fast.route('/acceptedFriend')
def acceptedFriend():
    f=Friend.query.filter(Friend.user_id==current_user.id).filter(Friend.approved==True).first()
    if f is None:
        flash('Please add monkey! Now you don\'t have friend')
        return redirect(url_for('fast.userlist'))
    k=Friend.query.join(User.friend).filter(Friend.approved==True).filter(Friend.user_id==current_user.id)
    b=[]
    for i in k:
        b.append(i.friend_Account)
        friends=PersonalInfo.query.join(User.user_info).filter(User.id.in_(b)).all()
    best_friend=BestFriend.query.join(Friend.bestFriend).filter(BestFriend.best_friend==True).filter(Friend.user_account==current_user.id).first()
    if best_friend is None:
      
            return render_template('fast/acceptedFriend.html',friends=friends)
    else:
        return render_template('fast/friends.html', friends=friends)
@fast.route('/bestFriend', methods=['GET','POST'])
def bestFriend():
    id=request.args.get('id', type=int)
    user=User.query.get_or_404(id)
    d=Friend.query.filter(Friend.friend_Account==user.id).filter(Friend.user_id==current_user.id).first()
    faccount=Friend.query.join(Friend.bestFriend).filter(BestFriend.best_friend==True).filter(Friend.user_account==current_user.id).filter(Friend.friend_Account==user.id).first()
    if faccount is None:
        try:
            
            f=BestFriend(best_friend=True, friend_id=d.id)
            db.session.add(f)
            db.session.commit()
            flash('Now you are best friend with him/her')
        except sqlite3.OperationalError:
            flash("database missing!! \n")
         
        return redirect(url_for('fast.index'))
   
    else:
        flash('Sorry! you already have one best friend')
        return redirect(url_for('fast.acceptedFriend'))

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

    
    best=Friend.query.join (Friend.bestFriend).filter(Friend.user_account==current_user.id).filter(BestFriend.best_friend==True).first()
    if best is None:
        flash('Please add Best Friend or add Friend first')
        return redirect(url_for('fast.userlist'))
      
       
    else:
          bestList=PersonalInfo.query.join(User.user_info).filter(User.id==best.friend_Account)
        
        
    
    
    return render_template ('fast/bestFriendList.html', bestList=bestList)
    
    



    






    
    
    
   
    
    
    
    
    
    
