from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from takeabeltof.utils import printException, cleanRecordID
from lindcraft.models import Product, Category,  Model

mod = Blueprint('catalog',__name__, template_folder='../templates/lindcraft/catalog')


def setExits():
    #g.listURL = url_for('.display')
    #g.editURL = url_for('.edit')
    #g.deleteURL = url_for('.delete')
    g.title = 'Catelog'
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
def product(prod_id=None):
    setExits()
    
    return "No Product Yet"
    
@mod.route('/prices',methods=["GET",])
@mod.route('/prices/',methods=["GET",])
@mod.route('/prices/<prod_id>',methods=["GET",])
@mod.route('/prices/<prod_id>/',methods=["GET",])
def prices(prod_id=None):
    setExits()
    
    return "No Prices Yet"


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
    
    cat = Category(g.db).select_one(where="lower(name) = 'parking rack'")
    if cat:
        parking_list = Product(g.db).select(where='cat_id = {}'.format(cat.id))
    cat = Category(g.db).select_one(where="lower(name) = 'display rack'")
    if cat:
        display_list = Product(g.db).select(where='cat_id = {}'.format(cat.id))
    
    return parking_list, display_list
    