"""WTF forms for Idealog."""
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Email, Length

#############################################################################
# User Model FORMS
class UserForm(FlaskForm):
    """Base form for user-related forms."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class UserAddForm(UserForm):
    """Form for adding users."""
    user_type = SelectField('User Type', choices=[('admin', 'Administrator'), ('registered', 'Registered')])

class UserSignupForm(UserForm):
    """Form for adding users."""
    user_type = SelectField('User Type', choices=[('admin', 'Administrator'), ('registered', 'Registered')])

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(UserForm):
    """Form for editing users."""

    user_type = SelectField('User Type', choices=[('admin', 'Administrator'), ('registered', 'Registered')])

#############################################################################
# IDEA MODEL FORMS
class IdeaForm(FlaskForm):
    """Base form for idea-related forms."""
    name = StringField('Idea Name', validators=[DataRequired()])
    publish_date = DateTimeField('Idea Publish Date', default=datetime.now)
    text = TextAreaField('Idea Description', validators=[DataRequired(), Length(min=3)])
    url = StringField('(Optional) Idea URL')
    privacy = SelectField('Idea Privacy', choices=[('private', 'Private'), ('public', 'Public')])
    creation_mode = SelectField('Creation Mode', choices=[('manual', 'Manual'), ('automated', 'Automated')])

class IdeaAddForm(IdeaForm):
    """Form for adding ideas."""
    idea_groups = SelectMultipleField('Idea Groups', choices=[], coerce=int)

#############################################################################
# GROUP MODEL FORMS

class GroupAddForm(FlaskForm):
    """Form for adding idea-groups."""
    name = StringField('Group Name', validators=[DataRequired()])

#############################################################################
# KNOWLEDGE SOURCE MODEL FORMS
class KnowledgeSourceForm(FlaskForm):
    """Base form for knowledge-source-related forms."""
    name = StringField('Knowledge Source Name', validators=[DataRequired()])
    publish_date = DateTimeField('Knowledge Source Publish Date', default=datetime.now)
    text = TextAreaField('Knowledge Source Full Text', validators=[DataRequired(), Length(min=3)])
    url = StringField('(Optional) Knowledge Source URL')
    privacy = SelectField('Knowledge Source Privacy', choices=[('private', 'Private'), ('public', 'Public')])
    creation_mode = SelectField('Creation Mode', choices=[('manual', 'Manual'), ('automated', 'Automated')])

class KnowledgeSourceAddForm(KnowledgeSourceForm):
    """Form for adding knowledge-sources."""
    knowledge_domains = SelectMultipleField('Knowledge Domains', choices=[], coerce=int)

#############################################################################
# KNOWLEDGE DOMAIN MODEL FORMS
class KnowledgeDomainAddForm(FlaskForm):
    """Form for adding knowledge domains."""

    name = StringField('Knowledge Domain Name', validators=[DataRequired()])

#############################################################################
# KNOWLEDGE BASE MODEL FORMS
class KnowledgeBaseForm(FlaskForm):
    """Base form for knowledge-base-related forms."""
    name = StringField('Knowledge Base Name', validators=[DataRequired()])

class KnowledgeBaseAddForm(KnowledgeBaseForm):
    """Form for adding knowledge bases."""
    ideas = SelectMultipleField('Ideas', choices=[], coerce=int)
    idea_groups = SelectMultipleField('Idea Groups', choices=[], coerce=int)
    knowledge_sources = SelectMultipleField('Knowledge Sources', choices=[], coerce=int)
    knowledge_domains = SelectMultipleField('Knowledge Domains', choices=[], coerce=int)

class KnowledgeBaseEditForm(KnowledgeBaseForm):
    """Form for editing knowledge bases."""
    privacy = SelectField('Knowledge Source Privacy', choices=[('private', 'Private'), ('public', 'Public')])
    creation_mode = SelectField('Creation Mode', choices=[('manual', 'Manual'), ('automated', 'Automated')])