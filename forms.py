"""WTF forms for Idealog."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length

#############################################################################
# User Model FORMS
class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    user_type = SelectField('User Type', choices=[('admin', 'Administrator'), ('registered', 'Registered')])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    user_type = SelectField('User Type', choices=[('admin', 'Administrator'), ('registered', 'Registered')])
    


#############################################################################
#IDEA MODEL FORMS

class IdeaAddForm(FlaskForm):
    """Form for adding ideas."""

    name = StringField('Idea Name', validators=[DataRequired()])
    publish_date = StringField('Idea Publish Date')
    description = StringField('Idea Description', validators=[DataRequired(), Length(min=3)])
    url = StringField('(Optional) Idea URL')
    privacy = SelectField('Idea Privacy', choices=[('private', 'Private'), ('public', 'Public')])
    group = SelectField('Idea Group', choices=[])


    #############################################################################
#GROUP MODEL FORMS

class GroupAddForm(FlaskForm):
    """Form for adding idea-groups."""

    name = StringField('Group Name', validators=[DataRequired()])