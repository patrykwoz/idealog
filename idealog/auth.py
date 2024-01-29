from flask import Flask, render_template, request, flash, redirect, session, g

bp = Blueprint('auth', __name__)

CURR_USER_KEY = "curr_user"

##############################################################################
# User signup/login/logout
@bp.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

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
            flash("Access unauthorized.", "danger")
            return redirect("/")
        return view_func(*args, **kwargs)
    return wrapper      

def requires_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'admin' not in g.user.user_type:
            flash("You don't have admin level access.", "danger")
            return redirect("/")
        return view_func(*args, **kwargs)
    return wrapper

@bp.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup. """
    form = UserSignupForm()

    default_profile_img = 'images/default_profile_pic.jpg'

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or default_profile_img,
                user_type='registered'
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        flash("Username successfully created.", 'success')

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@bp.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@bp.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    return redirect("/")

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@bp.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

##############################################################################
##############################################################################
##############################################################################
##############################################################################
