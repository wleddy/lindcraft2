from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from takeabeltof.utils import printException, cleanRecordID, render_markdown_text
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
    
        
@mod.route('/prices',methods=["GET",])
@mod.route('/prices/',methods=["GET",])
@mod.route('/prices/<prod_id>',methods=["GET",])
@mod.route('/prices/<prod_id>/',methods=["GET",])
@mod.route('/product',methods=["GET",])
@mod.route('/product/',methods=["GET",])
@mod.route('/product/<prod_id>',methods=["GET",])
@mod.route('/product/<prod_id>/',methods=["GET",])
def prices(prod_id=0):
    setExits()
    product_desc_html = ''
    prod_id = cleanRecordID(prod_id)
    price_list = get_price_list(prod_id)
    show_groups = True
    effective_date = get_effective_date()
    if price_list:
        if prod_id <= 0:
            # Price List
            g.title = 'Price List'
            template = 'prices.html'
            
        else:
            # Prices for a single product
            g.title = price_list[0]['product'].name
            show_groups = False
            template = 'product.html'
            product_desc_html = render_markdown_text(price_list[0]['product'].desc)
        return render_template(template,price_list=price_list,show_groups=show_groups,effective_date=effective_date,product_desc_html=product_desc_html,)
            
    flash('Could not find that product')
    return redirect(url_for('.home'))
        
    
@mod.route('/display_info/',methods=["GET",])
@mod.route('/display_info/<int:cat_id>',methods=["GET",])
@mod.route('/display_info/<int:cat_id>/',methods=["GET",])
def display_info(cat_id=0):
    setExits()
    cat_id = cleanRecordID(cat_id)
    if cat_id < 1:
        abort(404)
        
    cat = Category(g.db).get(cat_id)
    if not cat:
        abort(404)
        
    recs = Product(g.db).select_active(where="cat_id = {}".format(cat_id))
    if not recs:
        abort(404)
        
    g.title = cat.name
    
    return render_template('display_info.html',recs=recs)
    
    
def get_nav_html():
    """Return fully rendered html for the catalog navigation menu"""
    
    #Create a list to hold a dict of Cat and Product Data for nav display
    cat_list = []
    #Get a selection of categories with active models associated
    cats = Category(g.db).select_active(where="category.display_order >= 0")
    for cat in cats:
        # Get selection of active products for this category
        prods = Product(g.db).select_active(where="cat_id = {}".format(cat.id,))
        if prods:
            # Modify the image name for nav display
            for prod in prods:
                prod.image_path = prod.image_path.replace('.jpg','_sm.jpg')
            cat_list.append({'cat':cat,'prods':prods,})
        
        
    return render_template('nav.html',cat_list=cat_list)
    
    
def get_price_list(prod_id=0):
    """Return a list of dicts with product and model for price list"""
    #import pdb;pdb.set_trace()
    prod_id = cleanRecordID(prod_id)
    prod_list = []
    #Get a selection of products with active models associated
    where = ''
    if prod_id > 0:
        where = "p.id = {}".format(prod_id,)
            
    products = Product(g.db).select_active(where=where)
    for product in products:
        # Get selection of active products for this category
        where = 'prod_id = {}'.format(product.id)
        models = Model(g.db).select_active(where=where)
        if models:
            prod_list.append({'product':product,'models':models,})
    
    
    return prod_list
    
    
def get_effective_date():
    """Return the most recent price update date from all models"""
    
    models = Model(g.db).select_one(order_by = 'price_change_date DESC ')
    if models:
        return models.price_change_date
        
    return local_datetime_now() #default to today
    
    
        