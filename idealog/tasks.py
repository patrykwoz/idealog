import time

from celery import shared_task, Task

from idealog.models import db, KnowledgeBase
from idealog.ml_functions import class_kb
from idealog.ml_functions.class_kb import from_text_to_kb

tokenizer = class_kb.tokenizer
model = class_kb.model

@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    time.sleep(5)
    return a + b

@shared_task(ignore_result=False, time_limit=420)
def create_kb(kb_id: int):
    try:
        knowledge_base = db.session.query(KnowledgeBase).get(kb_id)

        if knowledge_base:
            ideas = knowledge_base.ideas
            knowledge_sources = knowledge_base.knowledge_sources

            idea_groups = knowledge_base.idea_groups
            ideas_from_groups=[]
            for idea_group in idea_groups:
                ideas_from_groups.extend(idea_group.ideas)

            domains = knowledge_base.knowledge_domains
            knowledge_sources_from_domains = []
            for domain in domains:
                knowledge_sources_from_domains.extend(domain.knowledge_sources)
                 
            merged_ideas = ideas + knowledge_sources + ideas_from_groups + knowledge_sources_from_domains
            
            kb = class_kb.from_ideas_to_kb(merged_ideas,verbose=False)

            knowledge_base.json_object = kb.to_json()
            knowledge_base.status = 'ready'
            db.session.commit()

            return kb_id
        else:
            raise ValueError('Could not find the knowledge_base')

    except Exception as e:
        db.session.rollback()
        return str(e)