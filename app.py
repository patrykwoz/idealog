import os

from functools import wraps
from flask import Flask, render_template, request, flash, redirect, session, g, send_file
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm, IdeaAddForm, GroupAddForm
from models import db, connect_db, User, Idea, Group

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///idealog'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


connect_db(app)




##############################################################################
# User signup/login/logout


@app.before_request
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

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()


    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
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


@app.route('/login', methods=["GET", "POST"])
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


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    return redirect("/")


##############################################################################
# General user web routes (pages):

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/show_all_users.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.route('/users/profile', methods=["GET", "POST"])
@requires_login
def profile():
    """Update profile for current user."""    
    form = UserEditForm(obj=g.user)


    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.email = form.email.data
        g.user.image_url = form.image_url.data
        authenticate_user = User.authenticate(form.username.data, form.password.data)
        if authenticate_user:
            db.session.commit()
            flash("Succesffully saved changes.", "success")
        else:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        
        return redirect(f"/users/{g.user.id}")

    return render_template("users/edit.html", form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

##############################################################################
# General idea web routes (pages)
@app.route('/ideas', methods=["GET"])
@requires_login
def render_all_ideas():
    ideas = Idea.sorted_query()
    return render_template('ideas/show_all_ideas.html', ideas=ideas)


@app.route('/ideas/new', methods=["GET", "POST"])
@requires_login
def add_new_idea():
    form = IdeaAddForm()
    form.group.choices = [(group.id, group.name) for group in Group.query.all()]

    

    if form.validate_on_submit():
        
        try:
            groups_choices_ids = form.group.data
            if not isinstance(groups_choices_ids, list):
                groups_choices_ids = [groups_choices_ids]

            groups = Group.query.filter(Group.id.in_(groups_choices_ids)).all()
            if len(groups) != len(groups_choices_ids):
                flash("One or more selected groups do not exist.", "danger")
                return render_template('ideas/new_idea.html', form=form)

            idea = Idea(
                name=form.name.data,
                publish_date=form.publish_date.data,
                description=form.description.data,
                url=form.url.data,
                privacy=form.privacy.data,
                groups=groups,
            )
            

            db.session.add(idea)
            db.session.commit()
            flash("Successfully added a new idea.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")

        return redirect("/ideas")

    return render_template('ideas/new_idea.html', form=form)


##############################################################################
# General Group web routes (web pages).
@app.route('/idea-groups', methods=["GET"])
@requires_login
def render_all_groups():
    groups = Group.query.all()
    return render_template('groups/show_all_groups.html', groups=groups)

@app.route('/idea-groups/new', methods=["GET", "POST"])
@requires_login
def add_new_group():
    form = GroupAddForm()

    

    if form.validate_on_submit():
        
        try:

            group = Group(
                name=form.name.data,
                user_id = g.user.id
            )
            

            db.session.add(group)
            db.session.commit()
            flash("Successfully added a new group.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")

        return redirect("/idea-groups")

    return render_template('groups/new_group.html', form=form)



##############################################################################
# Homepage


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    if g.user:        
        return render_template('users/registered_home.html')

    else:
        return render_template('home_guest.html')

#######################
# Handle files

@app.route('/js/<path:filename>')
def serve_js(filename):

    return send_file(f'js/{filename}')

@app.route('/prototypes/buildingKB/lib/bindings/<path:filename>')
def serve_bindings_js(filename):
    p=1
    return send_file(f'prototypes/buildingKB/lib/bindings/{filename}')


##############################################################################
# Error Pages
@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


##############################################################################
# Restful API Routes
# These routes return JSON Files
#this route is not follwing REST api standard so it must be changes but I'm not sure how to
#change routes that display users below
#either a separate service or handle via fronted JS calls

@app.route('/api/users', methods=["GET"])
def return_all_users():
    """Return All users within a specified limite of users returned from db as a JSON object."""
    all_users = "Query all users from db and jsonify"
    return all_users