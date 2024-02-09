from functools import wraps
from flask import session, g, flash, redirect, url_for
from idealog.models import User

CURR_USER_KEY = "curr_user"

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def requires_login(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized. Login to proceed.", "danger")
            return redirect(url_for('views.homepage'))
        return view_func(*args, **kwargs)
    return wrapper      

def requires_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'admin' not in g.user.user_type:
            flash("You don't have admin level access.", "danger")
            return redirect(url_for('views.homepage'))
        return view_func(*args, **kwargs)
    return wrapper