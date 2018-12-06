from flask import Flask, render_template, g, session, url_for, request, redirect
from flask_mail import Mail

from lindcraft.models import Model, Category, Product, init_db as lindcraft_init_db
from takeabeltof.database import Database
from takeabeltof.jinja_filters import register_jinja_filters
from users.models import User,Role,init_db, Pref
from users.admin import Admin

# Create app
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('site_settings.py', silent=True)


# work around some web servers that mess up root path
from werkzeug.contrib.fixers import CGIRootFix
if app.config['CGI_ROOT_FIX_APPLY'] == True:
    fixPath = app.config.get("CGI_ROOT_FIX_PATH","/")
    app.wsgi_app = CGIRootFix(app.wsgi_app, app_root=fixPath)

register_jinja_filters(app)

# Create a mailer obj
mail = Mail(app)


def get_db(filespec=app.config['DATABASE_PATH']):
    if 'db' not in g:
        g.db = Database(filespec).connect()
    return g.db


@app.before_request
def _before():
    # Force all connections to be secure
    if app.config['REQUIRE_SSL'] and not request.is_secure :
        return redirect(request.url.replace("http://", "https://"))
        
    get_db()
    
    # Change styling when displaying catalog
    g.view_catalog = False # set to true when you want the special styling
    
    # Is the user signed in?
    g.user = None
    if 'user' in session:
        g.user = session['user']
        
    if 'admin' not in g:
        g.admin = Admin(g.db)
        # Add items to the Admin menu
        # the order here determines the order of display in the menu
        g.admin.register(Product,url_for('product.display'),display_name='Products',header_row=True,minimum_rank_required=500)
        g.admin.register(Product,url_for('product.display'),display_name='Products',minimum_rank_required=500,roles=['admin',])
        g.admin.register(Model,url_for('model.display'),display_name='Models',minimum_rank_required=500,roles=['admin',])
        g.admin.register(Category,url_for('category.display'),display_name='Categories',minimum_rank_required=500,roles=['admin',])
        
        # a header row must have the some permissions or higher than the items it heads
        g.admin.register(User,url_for('user.display'),display_name='User Admin',header_row=True,minimum_rank_required=500)
            
        g.admin.register(User,url_for('user.display'),display_name='Users',minimum_rank_required=500,roles=['admin',])
        g.admin.register(Role,url_for('role.display'),display_name='Roles',minimum_rank_required=1000)
        g.admin.register(Pref,url_for('pref.display'),display_name='Prefs',minimum_rank_required=1000)
        

@app.teardown_request
def _teardown(exception):
    if 'db' in g:
        g.db.close()

@app.errorhandler(404)
def page_not_found(error):
    from takeabeltof.utils import handle_request_error
    handle_request_error(error,request,404)
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    from takeabeltof.utils import handle_request_error
    handle_request_error(error,request,500)
    return render_template('500.html'), 500

from www.views import home
app.register_blueprint(home.mod)

from users.views import user, login, role, pref
app.register_blueprint(user.mod)
app.register_blueprint(login.mod)
app.register_blueprint(role.mod)
app.register_blueprint(pref.mod)

from lindcraft.views import product, category, model, catalog
app.register_blueprint(category.mod)
app.register_blueprint(product.mod)
app.register_blueprint(model.mod)
app.register_blueprint(catalog.mod)

from lindcraft.jinja_filters import register_jinja_filters as reg_catalog_filters
reg_catalog_filters(app)

if __name__ == '__main__':
    with app.app_context():
        init_db(get_db())
        lindcraft_init_db(get_db())
        get_db().close()
        
    #app.run(host='172.20.10.2', port=5000)
    app.run()
    