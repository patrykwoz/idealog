import os

from functools import wraps
from flask import Flask, render_template, request, flash, redirect, session, g, send_file
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy import func

from forms import UserAddForm, UserSignupForm, LoginForm, UserEditForm, IdeaAddForm, GroupAddForm, KnowledgeSourceAddForm, KnowledgeDomainAddForm, KnowledgeBaseAddForm, KnowledgeBaseEditForm
from models import db, connect_db, User, Idea, Group, KnowledgeSource, KnowledgeDomain, KnowledgeBase

from helpers.ml_functions import class_kb

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

def requires_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'admin' not in g.user.user_type:
            flash("You don't have admin level access.", "danger")
            return redirect("/")
        return view_func(*args, **kwargs)
    return wrapper

@app.route('/signup', methods=["GET", "POST"])
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
        
        return redirect(f"/")

    return render_template("users/profile.html", form=form)

##############################################################################
# Admin user web routes (pages):


@app.route('/users')
@requires_login
@requires_admin
def list_users():
    """Page with listing of users.    """
    users = User.query.all()

    return render_template('users/show_all_users.html', users=users)

@app.route('/users/<int:user_id>')
@requires_login
@requires_admin
def user_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    return render_template('users/detail_user.html', user=user)

@app.route('/users/new', methods=["GET","POST"])
@requires_login
@requires_admin
def new_user():
    """Handle user signup. """
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

        return redirect("/users")
    else:
        return render_template('users/new_user.html', form=form)

@app.route('/users/<int:user_id>/edit', methods=["GET","POST"])
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
        flash("Succesffully saved changes.", "success")

        return redirect(f"/users/{user_id}")

    return render_template("users/edit_user.html", form=form, user=user)

@app.route('/users/<int:user_id>/delete', methods=["POST"])
@requires_login
@requires_admin
def delete_user(user_id):
    """Delete user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")
##############################################################################
# General user search routes (pages)
@app.route('/search', methods=["GET"])
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

##############################################################################
# General idea web routes (pages)
@app.route('/ideas', methods=["GET"])
@requires_login
def render_all_ideas():
    if 'admin' in g.user.user_type:
        ideas = Idea.sorted_query()
    else:
        ideas = Idea.query.filter((Idea.privacy == 'public') | (Idea.user_id == g.user.id)).all()

    return render_template('ideas/show_all_ideas.html', ideas=ideas, user=g.user)

@app.route('/ideas/<int:idea_id>', methods=["GET"])
@requires_login
def detail_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)


    return render_template('ideas/detail_idea.html', idea=idea)

@app.route('/ideas/new', methods=["GET", "POST"])
@requires_login
def add_new_idea():
    form = IdeaAddForm()
    form.idea_groups.choices = [(group.id, group.name) for group in Group.query.all()]

    

    if form.validate_on_submit():
        
        try:
            groups_choices_ids = form.idea_groups.data
            if not isinstance(groups_choices_ids, list):
                groups_choices_ids = [groups_choices_ids]

            groups = Group.query.filter(Group.id.in_(groups_choices_ids)).all()
            if len(groups) != len(groups_choices_ids):
                flash("One or more selected groups do not exist.", "danger")
                return render_template('ideas/new_idea.html', form=form)

            idea = Idea(
                name=form.name.data,
                publish_date=form.publish_date.data,
                text=form.text.data,
                url=form.url.data,
                privacy=form.privacy.data,
                creation_mode=form.creation_mode.data,
                groups=groups,
                user_id=g.user.id
            )
            

            db.session.add(idea)
            db.session.commit()
            flash("Successfully added a new idea.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")

        return redirect("/ideas")

    return render_template('ideas/new_idea.html', form=form)

@app.route('/ideas/<int:idea_id>/edit', methods=["GET", "POST"])
@requires_login
def edit_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)

    form = IdeaAddForm(obj=idea)

    form.idea_groups.choices = [(group.id, group.name) for group in Group.query.all()]

    #form.idea_groups.data = [group.id for group in idea.groups]

    if form.validate_on_submit():
        groups_choices_ids = form.idea_groups.data
        if not isinstance(groups_choices_ids, list):
                groups_choices_ids = [groups_choices_ids]

        groups = Group.query.filter(Group.id.in_(groups_choices_ids)).all()
        if len(groups) != len(groups_choices_ids):
            flash("One or more selected groups do not exist.", "danger")
            return render_template('ideas/new_idea.html', form=form)

        idea.name = form.name.data
        idea.text = form.text.data
        idea.publish_date = form.publish_date.data
        idea.url = form.url.data
        idea.groups = groups
        idea.privacy = form.privacy.data
        idea.creation_mode = form.creation_mode.data

        try:
            db.session.commit()
        except(e):
            flash(f"Something went wrong. Here's your error: {e}", "danger")
        return redirect("/ideas")

    return render_template('ideas/edit_idea.html', form=form)


@app.route('/ideas/<int:idea_id>/delete', methods=["POST"])
@requires_login
def delete_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()

    return redirect('/ideas')


##############################################################################
# General Group web routes (web pages).
@app.route('/idea-groups', methods=["GET"])
@requires_login
def render_all_groups():
    if 'admin' in g.user.user_type:
        groups = Group.query.all()
    else:
        groups = Group.query.filter((Group.user_id == g.user.id)).all()

    return render_template('groups/show_all_groups.html', groups=groups, user=g.user)

@app.route('/idea-groups/<int:group_id>', methods=["GET"])
@requires_login
def detail_group(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template('groups/detail_group.html', group=group)

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


@app.route('/idea-groups/<int:group_id>/edit', methods=["GET", "POST"])
@requires_login
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)
    form = GroupAddForm(obj=group)

    if form.validate_on_submit():
        try:
            group.name=form.name.data
            
            db.session.commit()
            flash("Successfully edited your group.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")

        return redirect("/idea-groups")

    return render_template('groups/edit_group.html', form=form)

@app.route('/idea-groups/<int:group_id>/delete', methods=["POST"])
@requires_login
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Successfully deleted your group.", "success")

    return redirect('/idea-groups')



##############################################################################
# General KNOWLEDGE SOURCE web routes (web pages).
@app.route('/knowledge-sources', methods=["GET"])
@requires_login
def render_all_knowledge_sources():
    if 'admin' in g.user.user_type:
        knowledge_sources = KnowledgeSource.query.all()
    else:
        knowledge_sources = KnowledgeSource.query.filter((KnowledgeSource.privacy == 'public') | (KnowledgeSource.user_id == g.user.id)).all()
    
    return render_template('knowledge_sources/show_all_knowledge_sources.html', knowledge_sources=knowledge_sources)

@app.route('/knowledge-sources/<int:knowledge_source_id>', methods=["GET"])
@requires_login
def detail_knowledge_source(knowledge_source_id):
    knowledge_source = KnowledgeSource.query.get_or_404(knowledge_source_id)


    return render_template('knowledge_sources/detail_knowledge_source.html', knowledge_source=knowledge_source)

@app.route('/knowledge-sources/new', methods=["GET", "POST"])
@requires_login
def add_new_knowledge_source():
    form = KnowledgeSourceAddForm()
    form.knowledge_domains.choices = [(knowledge_domain.id, knowledge_domain.name) for knowledge_domain in KnowledgeDomain.query.all()]

    if form.validate_on_submit():
        
        try:
            knowledge_domains_choices_ids = form.knowledge_domains.data
            if not isinstance(knowledge_domains_choices_ids, list):
                knowledge_domains_choices_ids = [knowledge_domains_choices_ids]

            knowledge_domains = KnowledgeDomain.query.filter(KnowledgeDomain.id.in_(knowledge_domains_choices_ids)).all()
            if len(knowledge_domains) != len(knowledge_domains_choices_ids):
                flash("One or more selected knowledge_domains do not exist.", "danger")
                return render_template('knwoledge_srouce/new_knowledge_source.html', form=form)

            knowledge_source = KnowledgeSource(
                name=form.name.data,
                publish_date=form.publish_date.data,
                text=form.text.data,
                url=form.url.data,
                privacy=form.privacy.data,
                creation_mode = form.creation_mode.data,
                knowledge_domains=knowledge_domains,
                user_id=g.user.id
            )
            
            db.session.add(knowledge_source)
            db.session.commit()
            flash("Successfully added a new knowledge source.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")

        return redirect("/knowledge-sources")

    return render_template('knowledge_sources/new_knowledge_source.html', form=form)

@app.route('/knowledge-sources/new-from-internet', methods=["GET", "POST"])
@requires_login
@requires_admin
def add_new_knowledge_source_internet():
    return render_template('knowledge_sources/new_knowledge_source.html', form=form)

@app.route('/knowledge-sources/new-from-files', methods=["GET", "POST"])
@requires_login
@requires_admin
def add_new_knowledge_source_files():
    return render_template('knowledge_sources/new_knowledge_source.html', form=form)


@app.route('/knowledge-sources/<int:knowledge_source_id>/edit', methods=["GET", "POST"])
@requires_login
def edit_knowledge_source(knowledge_source_id):
    knowledge_source = KnowledgeSource.query.get_or_404(knowledge_source_id)

    form = KnowledgeSourceAddForm(obj=knowledge_source)

    form.knowledge_domains.choices = [(knowledge_domain.id, knowledge_domain.name) for knowledge_domain in KnowledgeDomain.query.all()]


    if form.validate_on_submit():
        knowledge_domains_choices_ids = form.knowledge_domains.data
        if not isinstance(knowledge_domains_choices_ids, list):
            knowledge_domains_choices_ids = [knowledge_domains_choices_ids]

        knowledge_domains = KnowledgeDomain.query.filter(KnowledgeDomain.id.in_(knowledge_domains_choices_ids)).all()
        if len(knowledge_domains) != len(knowledge_domains_choices_ids):
            flash("One or more selected knowledge domains do not exist.", "danger")
            return render_template('knowledge_sources/new_knowledge_source.html', form=form)

        knowledge_source.name = form.name.data
        knowledge_source.text = form.text.data
        knowledge_source.publish_date = form.publish_date.data
        knowledge_source.url = form.url.data
        knowledge_source.knowledge_domains = knowledge_domains
        knowledge_source.privacy = form.privacy.data
        knowledge_source.creation_mode = form.creation_mode.data

        try:
            db.session.commit()
            flash("Successfully edited your knowledge source.", "success")
        except(e):
            flash(f"Something went wrong. Here's your error: {e}", "danger")
        return redirect("/knowledge-sources")

    return render_template('knowledge_sources/edit_knowledge_source.html', form=form)

@app.route('/knowledge-sources/<int:knowledge_source_id>/delete', methods=["POST"])
@requires_login
def delete_knowledge_source(knowledge_source_id):
    knowledge_source = KnowledgeSource.query.get_or_404(knowledge_source_id)
    db.session.delete(knowledge_source)
    db.session.commit()
    flash("Successfully deleted your knowledge_source.", "success")

    return redirect('/knowledge-sources')

##############################################################################
# General KNOWLEDGE DOMAIN web routes (web pages).

@app.route('/knowledge-domains', methods=["GET"])
@requires_login
def render_all_knowledge_domains():
    if 'admin' in g.user.user_type:
        knowledge_domains = KnowledgeDomain.query.all()
    else:
        knowledge_domains = KnowledgeDomain.query.filter((KnowledgeDomain.user_id == g.user.id)).all()
    
    return render_template('knowledge_domains/show_all_knowledge_domains.html', knowledge_domains=knowledge_domains)

@app.route('/knowledge-domains/<int:knowledge_domain_id>', methods=["GET"])
@requires_login
def detail_knowledge_domain(knowledge_domain_id):
    knowledge_domain = KnowledgeDomain.query.get_or_404(knowledge_domain_id)
    return render_template('knowledge_domains/detail_knowledge_domain.html', knowledge_domain=knowledge_domain)

@app.route('/knowledge-domains/new', methods=["GET", "POST"])
@requires_login
def add_new_knowledge_domain():
    form = KnowledgeDomainAddForm()
    if form.validate_on_submit():
        try:
            knowledge_domain = KnowledgeDomain(
                name=form.name.data,
                user_id = g.user.id
            )
            
            db.session.add(knowledge_domain)
            db.session.commit()
            flash("Successfully added a new knowledge_domain.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")
        return redirect("/knowledge-domains")
    return render_template('knowledge_domains/new_knowledge_domain.html', form=form)

@app.route('/knowledge-domains/<int:knowledge_domain_id>/edit', methods=["GET", "POST"])
@requires_login
def edit_knowledge_domain(knowledge_domain_id):
    knowledge_domain=KnowledgeDomain.query.get_or_404(knowledge_domain_id)
    form = KnowledgeDomainAddForm(obj=knowledge_domain)
    if form.validate_on_submit():
        try:
            knowledge_domain.name=form.name.data            
            db.session.commit()
            flash("Successfully edited your knowledge_domain.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")
        return redirect("/knowledge-domains")
    return render_template('knowledge_domains/edit_knowledge_domain.html', form=form)

@app.route('/knowledge-domains/<int:knowledge_domain_id>/delete', methods=["POST"])
@requires_login
def delete_knowledge_domain(knowledge_domain_id):
    knowledge_domain = KnowledgeDomain.query.get_or_404(knowledge_domain_id)
    db.session.delete(knowledge_domain)
    db.session.commit()
    flash("Successfully deleted your knowledge domain.", "success")

    return redirect('/knowledge-domains')

##############################################################################
# General KNOWLEDGE BASE web routes (web pages).

@app.route('/knowledge-bases', methods=["GET"])
@requires_login
def render_all_knowledge_bases():
    if 'admin' in g.user.user_type:
        knowledge_bases = KnowledgeBase.query.all()
    else:
        knowledge_bases = KnowledgeBase.query.filter((KnowledgeBase.privacy == 'public') | (KnowledgeBase.user_id == g.user.id)).all()

    return render_template('knowledge_bases/show_all_knowledge_bases.html', knowledge_bases=knowledge_bases)

@app.route('/knowledge-bases/<int:knowledge_base_id>', methods=["GET"])
@requires_login
def detail_knowledge_base(knowledge_base_id):
    knowledge_base = KnowledgeBase.query.get_or_404(knowledge_base_id)
    return render_template('knowledge_bases/detail_knowledge_base.html', knowledge_base=knowledge_base)

@app.route('/knowledge-bases/refresh', methods=["GET", "POST"])
@requires_login
@requires_admin
def refresh_knowledge_base():
    """Check whether all existing ideas and knowledge sources are included in the auto generated knowledge base of all ideas and kss
    and if there isn't one that has all ideas and kss - create a new one and display when ready """
    return redirect('/')

@app.route('/knowledge-bases/new', methods=["GET", "POST"])
@requires_login
@requires_admin
def add_new_knowledge_base():
    form = KnowledgeBaseAddForm()

    form.ideas.choices = [(idea.id, idea.name) for idea in Idea.query.all()]
    form.idea_groups.choices = [(group.id, group.name) for group in Group.query.all()]
    form.knowledge_sources.choices = [(knowledge_source.id, knowledge_source.name) for knowledge_source in KnowledgeSource.query.all()]
    form.knowledge_domains.choices = [(knowledge_domain.id, knowledge_domain.name) for knowledge_domain in KnowledgeDomain.query.all()]


    if form.validate_on_submit():
        try:
            knowledge_base = KnowledgeBase(
                name=form.name.data,
                user_id = g.user.id,
                status = 'pending'
            )
            
            ideas_choices_ids = form.ideas.data
            if not isinstance(ideas_choices_ids, list):
                ideas_choices_ids = [ideas_choices_ids]

            ideas = Idea.query.filter(Idea.id.in_(ideas_choices_ids)).all()
            if len(ideas) != len(ideas_choices_ids):
                flash("One or more selected ideas do not exist.", "danger")
                return render_template('knowledge_bases/new_knowledge_base.html', form=form)
            
            for idea in ideas:
                knowledge_base.ideas.append(idea)
            
            knowledge_sources_choices_ids = form.knowledge_sources.data
            if not isinstance(knowledge_sources_choices_ids, list):
                knowledge_sources_choices_ids = [knowledge_sources_choices_ids]

            knowledge_sources = KnowledgeSource.query.filter(KnowledgeSource.id.in_(knowledge_sources_choices_ids)).all()
            if len(knowledge_sources) != len(knowledge_sources_choices_ids):
                flash("One or more selected knowledgesources do not exist.", "danger")
                return render_template('knowledge_bases/new_knowledge_base.html', form=form)
            
            for knowledge_source in knowledge_sources:
                knowledge_base.knowledge_sources.append(knowledge_source)
            
            #Ideas from groups
            idea_groups_choices_ids = form.idea_groups.data
            if not isinstance(idea_groups_choices_ids, list):
                idea_groups_choices_ids = [idea_groups_choices_ids]
            
            idea_groups = Group.query.filter(Group.id.in_(idea_groups_choices_ids)).all()
            if len(idea_groups) != len(idea_groups_choices_ids):
                flash("One or more selected groups do not exist.", "danger")
                return render_template('knowledge_bases/new_knowledge_base.html', form=form)
            
            
            ideas_from_groups=[]
            for idea_group in idea_groups:
                ideas_from_groups.extend(idea_group.ideas)
            
            for idea in ideas_from_groups:
                knowledge_base.ideas.append(idea)

            for idea_group in idea_groups:
                knowledge_base.idea_groups.append(idea_group)
            
            #Knowledge Sources from Knowledge Domains
            knowledge_domains_choices_ids = form.knowledge_domains.data
            if not isinstance(knowledge_domains_choices_ids, list):
                knowledge_domains_choices_ids = [knowledge_domains_choices_ids]
            
            knowledge_domains = KnowledgeDomain.query.filter(KnowledgeDomain.id.in_(knowledge_domains_choices_ids)).all()
            if len(knowledge_domains) != len(knowledge_domains_choices_ids):
                flash("One or more selected knowledge domains do not exist.", "danger")
                return render_template('knowledge_bases/new_knowledge_base.html', form=form)
            
            knowledge_sources_from_domains=[]
            for knowledge_domain in knowledge_domains:
                knowledge_sources_from_domains.extend(knowledge_domain.knowledge_sources)
            
            for knowledge_source in knowledge_sources_from_domains:
                knowledge_base.knowledge_sources.append(knowledge_source)
            
            for knowledge_domain in knowledge_domains:
                knowledge_base.knowledge_domains.append(knowledge_domain)


            merged_ideas = ideas + knowledge_sources + ideas_from_groups + knowledge_sources_from_domains
            knowledge_base_class_object = class_kb.from_ideas_to_kb(merged_ideas,verbose=False)
            jsonified_knowledge_base_object = knowledge_base_class_object.to_json()

            knowledge_base.json_object = jsonified_knowledge_base_object
            knowledge_base.status = 'ready'
            
            db.session.add(knowledge_base)
            db.session.commit()
            flash("Successfully added a new knowledge_base.", "success")
        except Exception as e:
            flash(f"Something went wrong. Here's your error: {e}", "danger")
        return redirect("/knowledge-bases")
    return render_template('knowledge_bases/new_knowledge_base.html', form=form)

@app.route('/knowledge-bases/<int:knowledge_base_id>/edit', methods=["GET", "POST"])
@requires_login
@requires_admin
def edit_knowledge_base(knowledge_base_id):
    knowledge_base  = KnowledgeBase.query.get_or_404(knowledge_base_id)
    form = KnowledgeBaseEditForm(obj=knowledge_base)

    if form.validate_on_submit():
        knowledge_base.name = form.name.data
        knowledge_base.privacy = form.privacy.data
        knowledge_base.creation_mode = form.creation_mode.data

        try:
            db.session.commit()
            flash("Successfully edited your knowledge base.", "success")
        except(e):
            flash(f"Something went wrong. Here's your error: {e}", "danger")
        return redirect("/knowledge-bases")
    return render_template('knowledge_bases/edit_knowledge_base.html', form=form)

@app.route('/knowledge-bases/merge', methods=["GET", "POST"])
@requires_login
@requires_admin
def merge_knowledge_bases():
    """Select knowledge bases and merge them"""
    return redirect('/')

@app.route('/knowledge-bases/<int:knowledge_base_id>/delete', methods=["GET", "POST"])
@requires_login
@requires_admin
def delete_knowledge_base(knowledge_base_id):
    knowledge_base = KnowledgeBase.query.get_or_404(knowledge_base_id)
    db.session.delete(knowledge_base)
    db.session.commit()
    flash("Successfully deleted your knowledge base.", "success")

    return redirect("/knowledge-bases")

##############################################################################
# Homepage
@app.route('/')
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

@app.route('/docs')
def documentation_page():
    """Show docs page."""

    return render_template('docs/index.html')


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
# Admin Pages

@app.route('/admin')
@requires_login
@requires_admin
def render_admin_index():

    return redirect('/users')

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
##############################################################################
##############################################################################
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

##############################################################################
# KNOWLEDGE BASES
@app.route('/api/knowledge-bases/<int:knowledge_base_id>', methods=["GET"])
def return_knowledge_base_json(knowledge_base_id):
    """Return a Knowledge Base JSON object if processing of KB has been completed(status = 'ready')."""
    authorized = request.args.get('authorized')
    knowledge_base = KnowledgeBase.query.get_or_404(knowledge_base_id)
    if (knowledge_base.privacy == "private") and (authorized != 'authorized'):
        return {"error": "No knowledge bases found"}, 404
    knowledge_base_json=knowledge_base.json_object
    return knowledge_base_json

@app.route('/api/knowledge-bases', methods=["GET"])
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