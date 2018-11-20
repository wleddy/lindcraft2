from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from users.admin import login_required, table_access_required
from takeabeltof.utils import render_markdown_for
from datetime import datetime
from lindcraft.views import catelog

mod = Blueprint('www',__name__, template_folder='../templates', url_prefix='')


def setExits():
    g.homeURL = url_for('.home')
    g.aboutURL = url_for('.about')
    g.contactURL = url_for('.contact')
    g.title = 'Home'
    g.view_catalog = True
    
@mod.route('/')
def home():
    setExits()

    #rendered_html = render_markdown_for(__file__,mod,'index.md')
    #
    #return render_template('markdown.html',rendered_html=rendered_html,)
    return catelog.display_intro()


@mod.route('/about', methods=['GET',])
@mod.route('/about/', methods=['GET',])
def about():
    setExits()
    g.title = "About"
    
    rendered_html = render_markdown_for(__file__,mod,'about.md')
            
    return render_template('about.html',rendered_html=rendered_html)


@mod.route('/contact', methods=['POST', 'GET',])
@mod.route('/contact/', methods=['POST', 'GET',])
def contact():
    setExits()
    g.name = 'Contact Us'
    from app import app
    from takeabeltof.mailer import send_message
    rendered_html = render_markdown_for(__file__,mod,'contact.md')
    show_form = True
    context = {}
    if request.form:
        if request.form['email'] and request.form['comment']:
            context = request.form
            context['name'] = request.form['name']
            #context['email'] = request.form['email']
            #context['comment'] = request.form['comment']
            #context['p'] = request.form['comment']
            #context['comment'] = request.form['comment']
            #context['comment'] = request.form['comment']
            #context['comment'] = request.form['comment']
            #context['date'] = datetime.now().isoformat(sep=" ")
            #print(context)
            send_message(
                (app.config['CONTACT_NAME'],app.config['CONTACT_EMAIL_ADDR'],),
                subject = "Comment from {}".format(app.config['SITE_NAME']),
                html_template = "home/email/contact_email.html",
                context = context,
                reply_to = request.form['email'],
            )
        
            show_form = False
        else:
            context = request.form
            flash('You left some stuff out.')
            
    
    return render_template('contact.html',rendered_html=rendered_html, show_form=show_form, context=context)
    
    
@mod.route('/robots.txt', methods=['GET',])
def robots():
    resp = Response("""User-agent: *
Disallow: /""" )
    resp.headers['content-type'] = 'text/plain'
    return resp

