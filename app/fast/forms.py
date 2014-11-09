from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, Required, Email
from flask.ext.pagedown.fields import PageDownField


class AddMonkeyForm(Form):
    Name = StringField('Name', validators=[Required()])
    Email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    Age = IntegerField('Age', validators=[Required()])
    submit = SubmitField('Submit')


