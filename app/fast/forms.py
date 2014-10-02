from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, IntegerField,PasswordField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, Required, URL, Email
from flask.ext.pagedown.fields import PageDownField

class ProfileForm(Form):
    firstName=StringField('First Name', validators=[Required(),Length(1,30)])
    lastName=StringField('Last Name', validators=[Required(), Length(1,30)])
    Age=IntegerField('Age', validators=[Required()])
    location=StringField('Location',validators=[Optional(),Length(1,30)] )
    bio=TextAreaField('Bio')
    submit=SubmitField('Submit')
class PresenterCommentForm(Form):
    body = PageDownField('Comment', validators=[Required()])
    submit = SubmitField('Submit')
class CommentForm(Form):
    name = StringField('Name', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    body = PageDownField('Comment', validators=[Required()])
    notify = BooleanField('Notify when new comments are posted', default=True)
    submit = SubmitField('Submit')
class RegisterForm(Form):
    username=StringField('User Name', validators=[Required()])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    
    password = PasswordField('Password', validators=[Required(), Length(1,30)])
    submit = SubmitField('Register')
    

