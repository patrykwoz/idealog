from flask import Flask, render_template, redirect, flash, session, g, request, jsonify, Blueprint, url_for
from .helpers import requires_login, requires_admin
from idealog.models import db, User, Idea, Group, KnowledgeSource, KnowledgeDomain, KnowledgeBase
from idealog.forms import UserEditForm, UserAddForm

bp = Blueprint('users_bp', __name__)

##############################################################################
# General user web routes (pages):
@bp.route('/users/profile', methods=["GET", "POST"])
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
            flash("Successfully saved changes.", "success")
        else:
            flash("Access unauthorized.", "danger")
            return redirect(url_for('views.homepage'))
        
        return redirect(url_for('views.homepage'))

    return render_template("users/profile.html", form=form)

##############################################################################
# Admin user web routes (pages):
@bp.route('/users')
@requires_login
@requires_admin
def list_users():
    """Page with listing of users."""    
    users = User.query.all()
    return render_template('users/show_all_users.html', users=users)

@bp.route('/users/<int:user_id>')
@requires_login
@requires_admin
def user_show(user_id):
    """Show user profile."""    
    user = User.query.get_or_404(user_id)
    return render_template('users/detail_user.html', user=user)

@bp.route('/users/new', methods=["GET","POST"])
@requires_login
@requires_admin
def new_user():
    """Handle user signup."""    
    form = UserAddForm()
    default_profile_img = 'images/default_profile_pic.jpg'

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or default_profile_img,
                user_type=form.user_type.data
            )
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already taken", 'danger')
            return render_template('users/new_user.html', form=form)
        except PendingRollbackError:
            db.session.rollback()
            flash("A database error occurred. Please try again.", 'danger')
            return render_template('users/new_user.html', form=form)  # or any other appropriate response
        
        flash("Username successfully created.", 'success')

        return redirect(url_for('users_bp.list_users'))
    else:
        return render_template('users/new_user.html', form=form)

@bp.route('/users/<int:user_id>/edit', methods=["GET","POST"])
@requires_login
@requires_admin
def edit_user(user_id):
    """Edit user as an admin"""    
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data
        user.password = User.hash_existing(form.password.data)

        db.session.commit()
        flash("Successfully saved changes.", "success")

        return redirect(url_for('users_bp.user_show', user_id=user_id))

    return render_template("users/edit_user.html", form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=["POST"])
@requires_login
@requires_admin
def delete_user(user_id):
    """Delete user."""    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('users_bp.list_users'))

##############################################################################
# General user search routes (pages)
@bp.route('/search', methods=["GET"])
def search_results():
    query = request.args.get('home-query')
    query = f"%{query}%"

    # Check user status
    if g.user:
        if 'admin' in g.user.user_type:
            # Admin: Show all entries
            ideas = Idea.query.filter(Idea.name.ilike(query)).all()
            groups = Group.query.filter(Group.name.ilike(query)).all()
            knowledge_sources = KnowledgeSource.query.filter(KnowledgeSource.name.ilike(query)).all()
            knowledge_domains = KnowledgeDomain.query.filter(KnowledgeDomain.name.ilike(query)).all()
            knowledge_bases = KnowledgeBase.query.filter(KnowledgeBase.name.ilike(query)).all()
        else:
            # Registered user: Show own private entries and public entries
            ideas = Idea.query.filter(Idea.name.ilike(query), (Idea.privacy == 'public') | (Idea.user_id == g.user.id)).all()
            groups = Group.query.filter(Group.name.ilike(query), (Group.privacy == 'public') | (Group.user_id == g.user.id)).all()
            knowledge_sources = KnowledgeSource.query.filter(KnowledgeSource.name.ilike(query), (KnowledgeSource.privacy == 'public') | (KnowledgeSource.user_id == g.user.id)).all()
            knowledge_domains = KnowledgeDomain.query.filter(KnowledgeDomain.name.ilike(query), (KnowledgeDomain.privacy == 'public') | (KnowledgeDomain.user_id == g.user.id)).all()
            knowledge_bases = KnowledgeBase.query.filter(KnowledgeBase.name.ilike(query), (KnowledgeBase.privacy == 'public') | (KnowledgeBase.user_id == g.user.id)).all()
    else:
        # Guest: Show only public entries
        ideas = Idea.query.filter(Idea.name.ilike(query), Idea.privacy == 'public').all()
        groups = Group.query.filter(Group.name.ilike(query), Group.privacy == 'public').all()
        knowledge_sources = KnowledgeSource.query.filter(KnowledgeSource.name.ilike(query), KnowledgeSource.privacy == 'public').all()
        knowledge_domains = KnowledgeDomain.query.filter(KnowledgeDomain.name.ilike(query), KnowledgeDomain.privacy == 'public').all()
        knowledge_bases = KnowledgeBase.query.filter(KnowledgeBase.name.ilike(query), KnowledgeBase.privacy == 'public').all()

    return render_template('searches/home_search.html', ideas=ideas, groups=groups, knowledge_sources=knowledge_sources, knowledge_domains=knowledge_domains, knowledge_bases=knowledge_bases)

@bp.route('/admin')
@requires_login
@requires_admin
def render_admin_index():
    return redirect(url_for('users_bp.list_users'))