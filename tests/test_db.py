import pytest
from idealog.models import db, User, Idea, Group, KnowledgeSource, KnowledgeDomain, KnowledgeBase

def test_db(app):
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        assert user is not None