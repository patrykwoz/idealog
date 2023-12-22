"""WTF forms for Idealog."""
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, DateTimeField
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
    publish_date = DateTimeField('Idea Publish Date', default=datetime.now)
    text = TextAreaField('Idea Description', validators=[DataRequired(), Length(min=3)])
    url = StringField('(Optional) Idea URL')
    privacy = SelectField('Idea Privacy', choices=[('private', 'Private'), ('public', 'Public')])
    idea_groups = SelectMultipleField('Idea Groups', choices=[],  coerce=int)




#############################################################################
#GROUP MODEL FORMS

class GroupAddForm(FlaskForm):
    """Form for adding idea-groups."""

    name = StringField('Group Name', validators=[DataRequired()])


#############################################################################
#KNOWLEDGE SOURCE MODEL FORMS

class KnowledgeSourceAddForm(FlaskForm):
    """Form for adding knowledge-sources."""

    name = StringField('Knowledge Source Name', validators=[DataRequired()])
    publish_date = DateTimeField('Knowledge Source Publish Date', default=datetime.now)
    text = TextAreaField('Knowledge Source Full Text', validators=[DataRequired(), Length(min=3)])
    url = StringField('(Optional) Knowledge Source URL')

    privacy = SelectField('Knowledge Source Privacy', choices=[('private', 'Private'), ('public', 'Public')])

    knowledge_domains = SelectMultipleField('Knowledge Domains', choices=[],  coerce=int)


#############################################################################
#KNOWLEDGE DOMAIN MODEL FORMS

class KnowledgeDomainAddForm(FlaskForm):
    """Form for adding knowledge domains."""

    name = StringField('Knowledge Domain Name', validators=[DataRequired()])


#############################################################################
#KNOWLEDGE BASE MODEL FORMS

class KnowledgeBaseAddForm(FlaskForm):
    """Form for adding knowledge bases."""

    name = StringField('Knowledge Base Name', validators=[DataRequired()])

    ideas = SelectMultipleField('Ideas', choices=[],  coerce=int)
    idea_groups = SelectMultipleField('Idea Groups', choices=[],  coerce=int)
    knowledge_sources = SelectMultipleField('Knowledge Sources', choices=[],  coerce=int)
    knowledge_domains = SelectMultipleField('Knowledge Domains', choices=[],  coerce=int)