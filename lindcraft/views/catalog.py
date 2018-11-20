from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from takeabeltof.utils import printException, cleanRecordID
from lindcraft.models import Product, Category,  Model

mod = Blueprint('catalog',__name__, template_folder='../templates/lindcraft/catalog')


def setExits():
    g.title = 'Home'
    g.view_catalog = True

@mod.route('/',methods=["GET",])
def home():
    setExits()
    
    parking_list = None
    display_list = None
    parking_list, display_list = get_nav_context()
    
    return render_template('home.html',display_list=display_list,parking_list=parking_list)
    
    
@mod.route('/product',methods=["GET",])
@mod.route('/product/',methods=["GET",])
@mod.route('/product/<prod_id>',methods=["GET",])
@mod.route('/product/<prod_id>/',methods=["GET",])
def product(prod_id=0):
    setExits()
    g.title = 'Product'
    prod_id = cleanRecordID(prod_id)
    if prod_id > 0:
        return "No Products Yet"
    elif prod_id == 0:
        return "Here is a list of all products"

    # Not a valid request
    return abort(400)
        
@mod.route('/prices',methods=["GET",])
@mod.route('/prices/',methods=["GET",])
@mod.route('/prices/<prod_id>',methods=["GET",])
@mod.route('/prices/<prod_id>/',methods=["GET",])
def prices(prod_id=0):
    setExits()
    g.title = 'Prices'
    prod_id = cleanRecordID(prod_id)
    if prod_id > 0:
        return "No Prices Yet"
    elif prod_id == 0:
        return "Here is a list of all prices for all products"
        
    # Not a valid request
    return abort(400)



@mod.route('/parking_info',methods=["GET",])
def parking_info():
    setExits()
    
    return "No Parking info yet"
    
@mod.route('/display_info',methods=["GET",])
def display_info():
    setExits()
    
    return "No display info yet"
    
def get_nav_context():
    
    parking_list = None
    display_list = None
    
    # THis is ugly as sin, but it works for now. To dependent on the sql in lindcraft.models
    #.  and it would be better if it returned a single row
    cat = Category(g.db).select_active(where="lower(c.name) = 'parking rack'")
    if cat: # and Category(g.db).is_active(cat.id):
        parking_list = Product(g.db).select_active(where='cat_id = {}'.format(cat[0].id))
        
    cat = Category(g.db).select_active(where="lower(c.name) = 'display rack'")
    if cat: # and Category(g.db).is_active(cat.id):
        display_list = Product(g.db).select_active(where='cat_id = {}'.format(cat[0].id))
    
    
    return parking_list, display_list
    