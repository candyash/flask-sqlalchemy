from flask import render_template, current_app, request, redirect, url_for, \
    flash
from flask.ext.login import login_user, logout_user, login_required
from ..models import User
from . import fastlog
from .forms import LoginForm
from app.connection import con



@fastlog.route('/login', methods=['GET', 'POST'])
def login():

        
    if not current_app.config['DEBUG'] and not current_app.config['TESTING'] \
                and not request.is_secure:
        return redirect(url_for('.login', _external=True, _scheme='https'))
    
    
    form = LoginForm()
        
    if form.validate_on_submit():
        email=form.email.data
      
        user = User.query.filter_by(email=form.email.data).first()
        #sql='select * from users where email=%s'
        #user=con.execute(sql%(email).first()
        #user=User(password=user.passward_hash)
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid email or password.')
            return redirect(url_for('.login'))
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('fast.index'))
    return render_template('fastlog/login.html', form=form)


@fastlog.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('fastlog.login'))


