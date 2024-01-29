from flask import (Flask, render_template, redirect, request, flash, session, g, jsonify, Blueprint)

from .helpers import requires_login, requires_admin

from idealog.models import db, User, Idea, Group, KnowledgeSource, KnowledgeDomain, KnowledgeBase

bp = Blueprint('views', __name__)

##############################################################################
# Homepage
@bp.route('/')
def homepage():
    """Show homepage.  """
    if g.user:
        user=g.user        
        return render_template('users/registered_home.html', user=user)

    else:
        knowledge_bases = KnowledgeBase.query.filter((KnowledgeBase.privacy == 'public')).all()

        return render_template('users/guest_home.html', knowledge_bases=knowledge_bases)

##############################################################################
# Docs page

@bp.route('/docs')
def documentation_page():
    """Show docs page."""

    return render_template('docs/index.html')