from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from takeabeltof.utils import printException, cleanRecordID
from lindcraft.models import Product, Category,  Model

mod = Blueprint('catalog',__name__, template_folder='../templates/lindcraft/catalog')


def setExits():
    g.title = 'Home'
    g.view_catalog = True
    g.catalog_nav = get_nav_html()

@mod.route('/',methods=["GET",])
def home():
    setExits()
            
    return render_template('home.html',)
    
    
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
    
    
def get_nav_html():
    """Return fully rendered html for the catalog navigation menu"""
    
    #Create a list to hold a dict of Cat and Product Data for nav display
    cat_list = []
    #Get a selection of categories with active models associated
    cats = Category(g.db).select_active()
    for cat in cats:
        # Get selection of active products for this category
        prods = Product(g.db).select_active(where="cat_id = {}".format(cat.id,))
        if prods:
            cat_list.append({'cat':cat,'prods':prods,})
        
        
    return render_template('nav.html',cat_list=cat_list)
    
        