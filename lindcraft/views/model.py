from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from users.admin import login_required, table_access_required
from takeabeltof.utils import printException, cleanRecordID
from takeabeltof.date_utils import getDatetimeFromString, local_datetime_now
from lindcraft.models import Product, Category,  Model

mod = Blueprint('model',__name__, template_folder='../templates/lindcraft/admin', url_prefix='/admin/model')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Model'


@mod.route('/',methods=["GET",])
@table_access_required(Model)
def display():
    setExits()
    
    recs = Model(g.db).select()
   
    #Get categories to display
    products = Product(g.db)
    product = {}
    #import pdb;pdb.set_trace()
    
    if recs:
        for rec in recs:
            fnd = products.get(rec.prod_id)
            if fnd:
                product[rec.prod_id] = fnd.name

    return render_template('model_list.html',recs=recs,product=product)
    
    
@mod.route('/edit_from_list',methods=["GET", "POST",])
@mod.route('/edit_from_list/',methods=["GET", "POST",])
@mod.route('/edit_from_list/<int:id>/',methods=["GET", "POST",])
@mod.route('/edit_from_list/<int:id>/<int:prod_id>/',methods=["GET", "POST",])
@table_access_required(Model)
def edit_from_list(id=None,prod_id=None):
    """Handle creation of model from the Product record form"""
    setExits()
    #import pdb;pdb.set_trace()
    
    return handle_edit(id,prod_id,from_list=True)
    
@mod.route('/edit',methods=["GET", "POST",])
@mod.route('/edit/',methods=["GET", "POST",])
@mod.route('/edit/<int:id>/',methods=["GET", "POST",])
@table_access_required(Model)
def edit(id=None):
    setExits()
    #import pdb;pdb.set_trace()
    return handle_edit(id,None,from_list=False)

    
def handle_edit(model_id=None,prod_id=None,from_list=False):
    """Handle special parts of model record edit"""

    #import pdb;pdb.set_trace()
    
    products = Product(g.db).select()

    model = Model(g.db)
    model_id = cleanRecordID(model_id)
    rec = model.get(model_id)
    rec_prev = model.get(model_id)
    if rec:
        prod_id = rec.prod_id
        
    current_product = None
    if prod_id == None:
        prod_id = request.form.get('prod_id',0) # attempt to set from form such as in the case of a new model
    prod_id = cleanRecordID(prod_id)
    current_product = Product(g.db).get(prod_id)

    if model_id == 0:
        rec = model.new()
        rec.price_change_date = local_datetime_now()
        rec.prod_id = prod_id
        
        if 'last_model' in session:
            model.update(rec,session['last_model'])
        
    if not rec:
        mes = "not a valid Model ID"
        if from_list:
            return "failure: {}".format(mes)
        else:
            flash(mes)
            return redirect(g.listURL)
             
    # Handle Response?
    if request.form:
        model.update(rec,request.form)
        if validate_form(rec):
    
            if (rec_prev and
                rec.price != rec_prev.price and
                getDatetimeFromString(rec.price_change_date) == getDatetimeFromString(rec_prev.price_change_date)):
                #If the price changed and the date didn't, change the date
                rec.price_change_date = local_datetime_now()
                
            if not rec.prod_id:
                rec.prod_id = prod_id
                
            if save_record(rec):
                if from_list:
                    return "success"
                else:
                    return redirect(g.listURL)
            else:
                if from_list:
                    return "failure: Unable to save changes."
                else:
                    pass #redisplay template below
        else:
            #invalid form
            model.update(rec,request.form)
            
    if from_list:
        return render_template('model_edit_from_list.html',rec=rec,current_product=current_product,products=products)
    else:
        return render_template('model_edit.html',rec=rec,current_product=current_product,products=products)


@mod.route('/get_model_list/',methods=["GET", ])
@mod.route('/get_model_list/<int:prod_id>/',methods=["GET", ])
def get_model_list_for_product(prod_id=None):
    """Render an html snippet of the transaciton list for the product"""
    prod_id = cleanRecordID(prod_id)
    models = None
    if prod_id and prod_id > 0:
        models = Model(g.db).select(where='prod_id = {}'.format(prod_id))
        
    return render_template('model_embed_list.html',models=models,prod_id=prod_id)
    
    
@mod.route('/delete_from_list/',methods=["GET", "POST",])
@mod.route('/delete_from_list/<int:id>/',methods=["GET", "POST",])
@table_access_required(Model)
def delete_from_list(id=None):
    setExits()
    if handle_delete(id):
        return "success"

    return 'failure: Could not delete that {}'.format(g.title)
    
    
@mod.route('/delete',methods=["GET", "POST",])
@mod.route('/delete/',methods=["GET", "POST",])
@mod.route('/delete/<int:id>/',methods=["GET", "POST",])
@table_access_required(Model)
def delete(id=None):
    setExits()
    if handle_delete(id):
        flash("{} Deleted".format(g.title))
        
    return redirect(g.listURL)
    
    
def handle_delete(id=None):
    if id == None:
        id = request.form.get('id',request.args.get('id',-1))
    
    id = cleanRecordID(id)
    if id <=0:
        #flash("That is not a valid record ID")
        return False
        
    rec = Model(g.db).get(id)
    if not rec:
        #flash("Record not found")
        return False
    else:
        Model(g.db).delete(rec.id)
        g.db.commit()
        return True


def save_record(rec):
    """Attempt to save a record"""
    try:
        Model(g.db).save(rec)
        g.db.commit()
        #Save the date and comment to session
        session['last_model'] = {"price_change_date":rec.price_change_date,}
        return True
        
    except Exception as e:
        g.db.rollback()
        flash(printException('Error attempting to save Model record',str(e)))
        return False
    
    
def validate_form(rec):
    valid_form = True
    where = ""
    #import pdb;pdb.set_trace()
    if not rec.model:
        flash("Model Name is required.")
        valid_form = False
    else:
        where = "model = '{}'".format(rec.model.strip())
        if rec.id:
            where += "and id <> {}".format(rec.id)
            
        existing_model_cnt = Model(g.db).select(where=where) #return a row object or None
    
        if existing_model_cnt:
            valid_form = False
            flash('That model name is already taken')
        
    datestring = request.form.get('price_change_date','').strip()
    change_date = getDatetimeFromString(datestring)
    if datestring == '':
        valid_form = False
        flash('Date may not be empty')
        
    elif change_date is None:
        flash('Date is not in a known format ("mm/dd/yy")')
        valid_form = False
    else:
        rec.price_change_date = change_date
        
    # Must be attached to an product
    productID = cleanRecordID(request.form.get('prod_id',0))
    if not productID or productID < 0:
        flash("You must select an product to use with this model")
        valid_form = False
    else:
        # product must exist
        prod = Product(g.db).get(productID)
        if not prod:
            flash("That is not a valid product")
            valid_form = False
            
    # price may not be None
    if rec.price == None:
        flash('The price may not be None')
        valid_form = False
        
    elif type(rec.price) is int or type(rec.price) is float:
        pass #ok
        
    if type(rec.price) is str:
        x = rec.price.partition('.')
        if not x[0].isdigit():
            flash('The price must be a number')
            valid_form = False
        
    return valid_form