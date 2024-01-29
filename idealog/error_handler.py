from flask import Blueprint, render_template

bp = Blueprint('error', __name__)
##############################################################################
# Error Pages
@bp.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404