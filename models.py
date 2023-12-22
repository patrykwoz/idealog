"""SQLAlchemy models for Idealog."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)
    user_type = db.Column(db.Text, nullable=False, default="registered")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}, type={self.user_type}>"

    @classmethod
    def signup(cls, username, email, password, image_url, user_type):
        """Sign up user.

        Hashes password and adds user to system.
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            user_type=user_type
        )

        db.session.add(user)
        return user
    
    @classmethod
    def hash_existing(cls, password):
        """Hash password for an existing user"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        return hashed_pwd


    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

# user = User(email="a@a.com", username="a", password="abc")
# idea = Idea(title="test", text="test text", url="hello.com", user_id=1)

class Idea(db.Model):
    """User's idea model."""

    __tablename__ = 'ideas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False, default = datetime.utcnow())
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)

    privacy = db.Column(db.Text, nullable=False, default="private")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    user = db.relationship('User', backref='ideas')

    groups = db.relationship('Group', secondary='idea_groups', backref='ideas')

    def __repr__(self):
        return f"<Idea #{self.id}: {self.name}>"

    @classmethod
    def sorted_query(self):
        return self.query.order_by(self.name).all()

class Group(db.Model):
    """Ideas group model."""

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    user = db.relationship('User', backref='groups')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    

    def __repr__(self):
        return f"<Group #{self.id}: {self.name}>"

class Artifact(db.Model):
    """Idea's artifact model."""

    __tablename__ = 'artifacts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.Text, nullable=False, default = datetime.utcnow())
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete="CASCADE"))
    idea = db.relationship('Idea', backref='artifacts')

    def __repr__(self):
        return f"<Artifact #{self.id}: {self.name}>"

    @classmethod
    def sorted_query(self):
        return self.query.order_by(self.name).all()

class KnowledgeSource(db.Model):
    """
    Knowledge source model.

    It's similar to ideas but it includes "ideas" extracted from published paper, internet articles, other sources, etc.
    It usually is a bigger chunk of information.
    """
    __tablename__='knowledge_sources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False, default = datetime.utcnow())
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)

    privacy = db.Column(db.Text, nullable=False, default="private")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    user = db.relationship('User', backref='knowledge_sources')

    knowledge_domains = db.relationship('KnowledgeDomain', secondary='knowledge_source_knowledge_domains', backref='knowledge_sources')

    def __repr__(self):
        return f"<Knowledge Source #{self.id}: {self.name}>"

    @classmethod
    def sorted_query(self):
        return self.query.order_by(self.name).all()

class KnowledgeDomain(db.Model):
    """Knowledge domain model. Similar to the idea's group."""

    __tablename__ = 'knowledge_domains'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref='knowledge_domains')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    

    def __repr__(self):
        return f"<Knowledge Domain #{self.id}: {self.name}>"

class KnowledgeBase(db.Model):
    """Knowledge basee model. Storing objects of KBClass. """
    __tablename__ = 'knowledge_bases'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    privacy = db.Column(db.Text, nullable=False, default="private")
    status = db.Column(db.Text, nullable=False, default="pending")

    user = db.relationship('User', backref='knowledge_bases')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))

    def __repr__(self):
        return f"<Knowledge Base #{self.id}: {self.name}>"

class Tag(db.Model):
    """"""
    __tablename__='tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Tag #{self.id}: {self.name}>"

class UserKnowledgeBase(db.Model):
    """Storing relationships between users and knowledge bases"""
    __tablename__ = 'user_knowledge_bases'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    knowledge_base_id = db.Column(db.Integer, db.ForeignKey('knowledge_bases.id', ondelete="CASCADE"))
    user = db.relationship('User')
    knowledge_base = db.relationship('KnowledgeBase')

class UserKnowledgeSource(db.Model):
    """Storing relationships between users and knowledge sources"""
    __tablename__ = 'user_knowledge_sources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    knowledge_base_id = db.Column(db.Integer, db.ForeignKey('knowledge_sources.id', ondelete="CASCADE"))
    user = db.relationship('User')
    knowledge_source = db.relationship('KnowledgeSource')

class IdeaGroup(db.Model):
    """Storing relationships between ideas and idea groups"""
    __tablename__ = 'idea_groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete="CASCADE"))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete="CASCADE"))
    idea = db.relationship('Idea')
    group = db.relationship('Group')

class Connection(db.Model):
    """Storing connection between two different idieas"""
    __tablename__ = 'connections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idea_id_1 = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete="CASCADE"))
    idea_id_2 = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete="CASCADE"))
    idea_1 = db.relationship('Idea', foreign_keys=[idea_id_1])
    idea_2 = db.relationship('Idea', foreign_keys=[idea_id_2])

class KnowledgeSourceKnowledgeDomain(db.Model):
    """Storing relationships between knowledge sources and knowledge domains"""
    __tablename__ = 'knowledge_source_knowledge_domains'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    knowledge_source_id = db.Column(db.Integer, db.ForeignKey('knowledge_sources.id', ondelete="CASCADE"))
    knowledge_domain_id = db.Column(db.Integer, db.ForeignKey('knowledge_domains.id', ondelete="CASCADE"))
    knowledge_source = db.relationship('KnowledgeSource')
    knowledge_domain = db.relationship('KnowledgeDomain')

class KnowledgeBaseComponents(db.Model):
    """Storing relationships between components of a knowledge base for processing"""
    __tablename__ = 'knowledge_base_components'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    knowledge_source_id = db.Column(db.Integer, db.ForeignKey('knowledge_sources.id', ondelete="CASCADE"))
    knowledge_domain_id = db.Column(db.Integer, db.ForeignKey('knowledge_domains.id', ondelete="CASCADE"))
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete="CASCADE"))
    status = db.Column(db.Text, nullable=False, default="pending")

    knowledge_source = db.relationship('KnowledgeSource')
    knowledge_domain = db.relationship('KnowledgeDomain')
    idea = db.relationship('Idea')

class IdeaTag(db.Model):
    """Storing relationships between ideas and tags"""
    __tablename__ = 'idea_tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete="CASCADE"))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"))
    idea = db.relationship('Idea')
    tag = db.relationship('Tag')


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)