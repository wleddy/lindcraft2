from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from users.admin import login_required, table_access_required
from users.utils import printException, cleanRecordID
from datetime import datetime
from lindcraft.models import Product, Category,  Model
from lindcraft.views.model import get_list_for_product

mod = Blueprint('product',__name__, template_folder='../templates/lindcraft', url_prefix='/products')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Product'
    g.modelListFromProductURL = url_for('.model_list_for_product')

@mod.route('/',methods=["GET",])
@table_access_required(Product)
def display():
    setExits()
    
    recs = Product(g.db).select()
    
    return render_template('product_list.html',recs=recs)
    
    
@mod.route('/edit',methods=["GET", "POST",])
@mod.route('/edit/',methods=["GET", "POST",])
@mod.route('/edit/<int:id>/',methods=["GET", "POST",])
@table_access_required(Product)
def edit(id=None):
    setExits()
    
    product = Product(g.db)
    modelList = None
    #import pdb;pdb.set_trace()
    if request.form:
        id = request.form.get('id',None)
    
    id = cleanRecordID(id)
    
    if id < 0:
        flash("Invalid Record ID")
        return redirect(g.listURL)
    
    categories = Category(g.db).select()
    uoms = Uom(g.db).select()
    
    if id >= 0 and not request.form:
        if id == 0:
            rec = product.new() # allow creation of new properties
            product.save(rec) # need an id for models
            g.db.commit() # have to commit this to protect the ID we just got
            # This name changes behavure of the Cancel link in the edit form
            g.cancelURL = url_for('.cancel') + "{}/".format(rec.id)
            
        else:
            rec = product.get(id)
            
        if not rec:
            flash('Record not Found')
            return redirect(g.listURL)
            
    #import pdb;pdb.set_trace()
    on_hand = product.stock_on_hand(id)
                
    if request.form:
        rec = product.get(id)
        if rec:
            product.update(rec,request.form)
            if validate_form():
                product.save(rec)
                try:
                    g.db.commit()
                    return redirect(g.listURL)
                
                except Exception as e:
                    g.db.rollback()
                    flash(printException('Error attempting to save Product record',str(e)))
                    return redirect(g.listURL)
            else:
                pass # There are imput errors
                
        else:
            flash('Record not Found')
            return redirect(g.listURL)
            
    modelList = get_list_for_product(rec.id)
    
    return render_template('product_edit.html',rec=rec,categories=categories,uoms=uoms,modelList=modelList,on_hand=on_hand)

@mod.route('/cancel',methods=["GET", "POST",])
@mod.route('/cancel/',methods=["GET", "POST",])
@mod.route('/cancel/<int:id>/',methods=["GET", "POST",])
@table_access_required(Product)
def cancel(id=None):
    """If user canceled a new record come here to delete the record stub"""
    setExits()
    
    if id:
        try:
            Product(g.db).delete(id)
            g.db.commit()
        except:
            flash("Could not delete temporary Product with id = {}".format(id))
        
        
    return redirect(g.listURL)
        
    
@mod.route('/model_list_for_product',methods=["GET",])
@mod.route('/model_list_for_product/<int:product_id>',methods=["GET",])
@table_access_required(Product)
def model_list_for_product(product_id=None):
    setExits()
    return get_list_for_product(product_id)
    
    
@mod.route('/delete',methods=["GET", "POST",])
@mod.route('/delete/',methods=["GET", "POST",])
@mod.route('/delete/<int:id>/',methods=["GET", "POST",])
@table_access_required(Product)
def delete(id=None):
    setExits()
    if id == None:
        id = request.form.get('id',request.args.get('id',-1))
    
    id = cleanRecordID(id)
    if id <=0:
        flash("That is not a valid record ID")
        return redirect(g.listURL)
        
    rec = Product(g.db).get(id)
    if not rec:
        flash("Record not found")
    else:
        Product(g.db).delete(rec.id)
        g.db.commit()
        flash("Record Deleted")
        
    return redirect(g.listURL)
        
      
def validate_form():
    valid_form = True
    if request.form['name'].strip() == '':
        valid_form = False
        flash('The name may not be empty')
    
    if request.form['cat_id'] == None or request.form['cat_id'] == "0":
        valid_form = False
        flash('You must select a category for this product')
        
    return valid_form
    
