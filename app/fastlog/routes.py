from flask import render_template, current_app, request, redirect, url_for, \
    flash, session
from flask.ext.login import login_user, logout_user, login_required
from ..models import User
from . import fastlog
from .forms import LoginForm
from app import login_manager



@fastlog.route('/login', methods=['GET', 'POST'])
def login():

        
    if not current_app.config['DEBUG'] and not current_app.config['TESTING'] \
                and not request.is_secure:
        return redirect(url_for('.login', _external=True, _scheme='https'))
    
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid email or password.')
            return redirect(url_for('.login'))
        remember=form.remember_me.data
        #session['remember_me'] =  remember
        login_user(user, remember=remember)
      
        return redirect(request.args.get('next') or url_for('talks.index'))
    return render_template('fastlog/login.html', form=form)
        
        


@fastlog.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('fastlog.login'))
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('fastlog.login'))
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


