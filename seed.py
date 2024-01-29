"""Seed database with sample data from CSV Files."""

from csv import DictReader
from idealog.models import db, User, Idea, Group, KnowledgeSource, KnowledgeDomain, KnowledgeBase
from idealog import create_app

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    with open('generator/users.csv') as users:
        db.session.bulk_insert_mappings(User, DictReader(users))

    with open('generator/ideas.csv') as ideas:
        db.session.bulk_insert_mappings(Idea, DictReader(ideas))

    with open('generator/groups.csv') as groups:
        db.session.bulk_insert_mappings(Group, DictReader(groups))
    
    with open('generator/knowledge_sources.csv') as knowledge_sources:
        db.session.bulk_insert_mappings(KnowledgeSource, DictReader(knowledge_sources))

    with open('generator/knowledge_domains.csv') as knowledge_domains:
        db.session.bulk_insert_mappings(KnowledgeDomain, DictReader(knowledge_domains))

    db.session.commit()
