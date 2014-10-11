from flask import render_template, current_app, request, redirect, url_for, \
    flash, session
from flask.ext.login import login_user, logout_user, login_required
from ..models import User
from . import auth
from .forms import LoginForm
from app import login_manager
from app.connection import con




@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    flash("check1")
    
    if request.method == "POST":
        flash("check2")
    
    
        '''if not current_app.config['DEBUG'] and not current_app.config['TESTING'] \
                    and not request.is_secure:
            return redirect(url_for('.login', _external=True, _scheme='https'))'''
        
    
 
        if form.validate_on_submit():
            flash("check3")
            
    
            user = User.query.filter_by(email=form.email.data).first()
            
            flash("{0}".format(user.username))
    
            if user.username is None or not user.verify_password(form.password.data):
                flash("Invalid email or password.")
                return redirect(url_for('auth.login'))
            else:
                
                remember=form.remember_me.data
                session["remember_me"] =  remember
                login_user(user, remember=remember)
                flash("Welcome! You are logged in sucessfuly!")
              
                return redirect(request.args.get("next") or url_for("fast.index"))
    flash("check6")
    
    return render_template("auth/login.html", form=form)
        
        


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("auth.login"))
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


