from flask import Blueprint, jsonify, request
from idealog.models import KnowledgeBase
from .helpers import requires_login, requires_admin

bp = Blueprint('api', __name__)

# Restful API Routes
# These routes return JSON Files
#this route is not follwing REST api standard so it must be changes but I'm not sure how to
#change routes that display users below
#either a separate service or handle via fronted JS calls

@bp.route('/api/users', methods=["GET"])
def return_all_users():
    """Return All users within a specified limite of users returned from db as a JSON object."""
    all_users = "Query all users from db and jsonify"
    return all_users

##############################################################################
# KNOWLEDGE BASES
@bp.route('/api/knowledge-bases/<int:knowledge_base_id>', methods=["GET"])
def return_knowledge_base_json(knowledge_base_id):
    """Return a Knowledge Base JSON object if processing of KB has been completed(status = 'ready')."""
    authorized = request.args.get('authorized')
    knowledge_base = KnowledgeBase.query.get_or_404(knowledge_base_id)
    if (knowledge_base.privacy == "private") and (authorized != 'authorized'):
        return {"error": "No knowledge bases found"}, 404
    knowledge_base_json=knowledge_base.json_object
    return knowledge_base_json

@bp.route('/api/knowledge-bases', methods=["GET"])
def return_latest_knowledge_base_json():
    """Return a Knowledge Base JSON object if processing of KB has been completed(status = 'ready')."""
    content = request.args.get('content')

    if content == 'latest':
        knowledge_base = KnowledgeBase.query.order_by(KnowledgeBase.id.desc()).first()
        if knowledge_base:
            knowledge_base_json = knowledge_base.json_object
            return knowledge_base_json
        else:
            return {"error": "No knowledge bases found"}, 404

    return {"error": "Invalid content parameter"}, 400