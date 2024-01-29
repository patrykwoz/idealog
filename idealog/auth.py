from flask import (
    Flask,
    render_template,
    request, flash, redirect, session, g,
    Blueprint
)

from .helpers import requires_login, requires_admin

bp = Blueprint('auth', __name__)



##############################################################################
# User signup/login/logout




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

