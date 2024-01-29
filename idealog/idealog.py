from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    g,
    jsonify,
)

from .models import (
    db,
    connect_db,
    User,
    Idea,
    Group,
    KnowledgeSource,
    KnowledgeDomain,
    KnowledgeBase,
)

from .forms import (
    IdeaAddForm,
    GroupAddForm,
    KnowledgeSourceAddForm,
    KnowledgeDomainAddForm,
    KnowledgeBaseAddForm,
    KnowledgeBaseEditForm,
)

from ml_functions import class_kb

bp = Blueprint('idealog', __name__)

##############################################################################
# General idea web routes (pages)
@bp.route('/ideas', methods=["GET"])
@requires_login
def render_all_ideas():
    if 'admin' in g.user.user_type:
        ideas = Idea.sorted_query()
    else:
        ideas = Idea.query.filter((Idea.privacy == 'public') | (Idea.user_id == g.user.id)).all()

    return render_template('ideas/show_all_ideas.html', ideas=ideas, user=g.user)

@bp.route('/ideas/<int:idea_id>', methods=["GET"])
@requires_login
def detail_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    return render_template('ideas/detail_idea.html', idea=idea)

@bp.route('/ideas/new', methods=["GET", "POST"])
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

@bp.route('/ideas/<int:idea_id>/edit', methods=["GET", "POST"])
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


@bp.route('/ideas/<int:idea_id>/delete', methods=["POST"])
@requires_login
def delete_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()

    return redirect('/ideas')


##############################################################################
# General Group web routes (web pages).
@bp.route('/idea-groups', methods=["GET"])
@requires_login
def render_all_groups():
    if 'admin' in g.user.user_type:
        groups = Group.query.all()
    else:
        groups = Group.query.filter((Group.user_id == g.user.id)).all()

    return render_template('groups/show_all_groups.html', groups=groups, user=g.user)

@bp.route('/idea-groups/<int:group_id>', methods=["GET"])
@requires_login
def detail_group(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template('groups/detail_group.html', group=group)

@bp.route('/idea-groups/new', methods=["GET", "POST"])
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


@bp.route('/idea-groups/<int:group_id>/edit', methods=["GET", "POST"])
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

@bp.route('/idea-groups/<int:group_id>/delete', methods=["POST"])
@requires_login
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Successfully deleted your group.", "success")

    return redirect('/idea-groups')



##############################################################################
# General KNOWLEDGE SOURCE web routes (web pages).
@bp.route('/knowledge-sources', methods=["GET"])
@requires_login
def render_all_knowledge_sources():
    if 'admin' in g.user.user_type:
        knowledge_sources = KnowledgeSource.query.all()
    else:
        knowledge_sources = KnowledgeSource.query.filter((KnowledgeSource.privacy == 'public') | (KnowledgeSource.user_id == g.user.id)).all()
    
    return render_template('knowledge_sources/show_all_knowledge_sources.html', knowledge_sources=knowledge_sources)

@bp.route('/knowledge-sources/<int:knowledge_source_id>', methods=["GET"])
@requires_login
def detail_knowledge_source(knowledge_source_id):
    knowledge_source = KnowledgeSource.query.get_or_404(knowledge_source_id)


    return render_template('knowledge_sources/detail_knowledge_source.html', knowledge_source=knowledge_source)

@bp.route('/knowledge-sources/new', methods=["GET", "POST"])
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

@bp.route('/knowledge-sources/new-from-internet', methods=["GET", "POST"])
@requires_login
@requires_admin
def add_new_knowledge_source_internet():
    return render_template('knowledge_sources/new_knowledge_source.html', form=form)

@bp.route('/knowledge-sources/new-from-files', methods=["GET", "POST"])
@requires_login
@requires_admin
def add_new_knowledge_source_files():
    return render_template('knowledge_sources/new_knowledge_source.html', form=form)


@bp.route('/knowledge-sources/<int:knowledge_source_id>/edit', methods=["GET", "POST"])
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

@bp.route('/knowledge-sources/<int:knowledge_source_id>/delete', methods=["POST"])
@requires_login
def delete_knowledge_source(knowledge_source_id):
    knowledge_source = KnowledgeSource.query.get_or_404(knowledge_source_id)
    db.session.delete(knowledge_source)
    db.session.commit()
    flash("Successfully deleted your knowledge_source.", "success")

    return redirect('/knowledge-sources')

##############################################################################
# General KNOWLEDGE DOMAIN web routes (web pages).

@bp.route('/knowledge-domains', methods=["GET"])
@requires_login
def render_all_knowledge_domains():
    if 'admin' in g.user.user_type:
        knowledge_domains = KnowledgeDomain.query.all()
    else:
        knowledge_domains = KnowledgeDomain.query.filter((KnowledgeDomain.user_id == g.user.id)).all()
    
    return render_template('knowledge_domains/show_all_knowledge_domains.html', knowledge_domains=knowledge_domains)

@bp.route('/knowledge-domains/<int:knowledge_domain_id>', methods=["GET"])
@requires_login
def detail_knowledge_domain(knowledge_domain_id):
    knowledge_domain = KnowledgeDomain.query.get_or_404(knowledge_domain_id)
    return render_template('knowledge_domains/detail_knowledge_domain.html', knowledge_domain=knowledge_domain)

@bp.route('/knowledge-domains/new', methods=["GET", "POST"])
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

@bp.route('/knowledge-domains/<int:knowledge_domain_id>/edit', methods=["GET", "POST"])
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

@bp.route('/knowledge-domains/<int:knowledge_domain_id>/delete', methods=["POST"])
@requires_login
def delete_knowledge_domain(knowledge_domain_id):
    knowledge_domain = KnowledgeDomain.query.get_or_404(knowledge_domain_id)
    db.session.delete(knowledge_domain)
    db.session.commit()
    flash("Successfully deleted your knowledge domain.", "success")

    return redirect('/knowledge-domains')

##############################################################################
# General KNOWLEDGE BASE web routes (web pages).

@bp.route('/knowledge-bases', methods=["GET"])
@requires_login
def render_all_knowledge_bases():
    if 'admin' in g.user.user_type:
        knowledge_bases = KnowledgeBase.query.all()
    else:
        knowledge_bases = KnowledgeBase.query.filter((KnowledgeBase.privacy == 'public') | (KnowledgeBase.user_id == g.user.id)).all()

    return render_template('knowledge_bases/show_all_knowledge_bases.html', knowledge_bases=knowledge_bases)

@bp.route('/knowledge-bases/<int:knowledge_base_id>', methods=["GET"])
@requires_login
def detail_knowledge_base(knowledge_base_id):
    knowledge_base = KnowledgeBase.query.get_or_404(knowledge_base_id)
    return render_template('knowledge_bases/detail_knowledge_base.html', knowledge_base=knowledge_base)

@bp.route('/knowledge-bases/refresh', methods=["GET", "POST"])
@requires_login
@requires_admin
def refresh_knowledge_base():
    """Check whether all existing ideas and knowledge sources are included in the auto generated knowledge base of all ideas and kss
    and if there isn't one that has all ideas and kss - create a new one and display when ready """
    return redirect('/')

@bp.route('/knowledge-bases/new', methods=["GET", "POST"])
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

@bp.route('/knowledge-bases/<int:knowledge_base_id>/edit', methods=["GET", "POST"])
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

@bp.route('/knowledge-bases/merge', methods=["GET", "POST"])
@requires_login
@requires_admin
def merge_knowledge_bases():
    """Select knowledge bases and merge them"""
    return redirect('/')

@bp.route('/knowledge-bases/<int:knowledge_base_id>/delete', methods=["GET", "POST"])
@requires_login
@requires_admin
def delete_knowledge_base(knowledge_base_id):
    knowledge_base = KnowledgeBase.query.get_or_404(knowledge_base_id)
    db.session.delete(knowledge_base)
    db.session.commit()
    flash("Successfully deleted your knowledge base.", "success")

    return redirect("/knowledge-bases")
