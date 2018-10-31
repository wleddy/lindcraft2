from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, Blueprint, Response
from users.admin import login_required, table_access_required
from takeabeltof.utils import printException, cleanRecordID
from date_utils import getDatetimeFromString, local_datetime_now
from lindcraft.models import Product, Category,  Model

mod = Blueprint('model',__name__, template_folder='../templates/lindcraft', url_prefix='/model')


def setExits():
    g.listURL = url_for('.display')
    g.editURL = url_for('.edit')
    g.deleteURL = url_for('.delete')
    g.title = 'Inventory Model'


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
    
    prod_id=cleanRecordID(prod_id)
    product_rec = None
    rec = None
    
    model = Model(g.db)
    model_id = cleanRecordID(id)
    if model_id > 0:
        rec = model.get(model_id)
        
    if rec:
        prod_id = rec.prod_id
    else:
        rec = model.new()
        if 'last_model' in session:
            model.update(rec,session['last_model'])
    
    # Handle Response?
    if request.form:
        #import pdb;pdb.set_trace()
        error_list=[]
        model.update(rec,request.form)
        if save_record(rec,error_list):
            return "success" # the success function looks for this...
        else:
            pass
            
    
    if prod_id > 0:
        product_rec = Product(g.db).get(prod_id)
    
    if not product_rec:
        flash("This is not a valid product id")
        return "failure: This is not a valid product id."
    else:
        rec.prod_id=prod_id
        
            
    return render_template('model_edit_from_list.html',rec=rec,current_product=product_rec)
    
#@mod.route('/add_from_list/',methods=["GET", "POST",])
#@mod.route('/add_from_list/<int:prod_id>/',methods=["GET", "POST",])
#@table_access_required(Model)
#def add_from_list(prod_id=None):
#    import pdb;pdb.set_trace()
#    
#    return edit_from_list(0,prod_id)
        
    
@mod.route('/delete_from_list/',methods=["GET", "POST",])
@mod.route('/delete_from_list/<int:id>/',methods=["GET", "POST",])
@table_access_required(Model)
def delete_from_list(id=None):
    setExits()
    if handle_delete(id):
        return "success"

    return 'failure: Could not delete that {}'.format(g.title)
    
@mod.route('/edit',methods=["GET", "POST",])
@mod.route('/edit/',methods=["GET", "POST",])
@mod.route('/edit/<int:id>/',methods=["GET", "POST",])
@table_access_required(Model)
def edit(id=None):
    setExits()
    #import pdb;pdb.set_trace()
    
    model = Model(g.db)
    
    if request.form:
        id = request.form.get('id',None)
    id = cleanRecordID(id)
    products = Product(g.db).select()
    current_product = None
    
    if id < 0:
        flash("Invalid Record ID")
        return redirect(g.listURL)
    
    if id >= 0 and not request.form:
        if id == 0:
            rec = model.new()
            rec.price_change_date = local_datetime_now()
            if 'last_model' in session:
                model.update(rec,session['last_model'])
        else:
            rec = model.get(id)
            
        if not rec:
            flash('Record not Found')
            return redirect(g.listURL)
        else:
            #Get the product if there is one
            if rec.prod_id != 0:
                current_product = Product(g.db).get(rec.prod_id)
                
            
    elif request.form:
        current_product = Product(g.db).get(cleanRecordID(request.form.get('prod_id',"0")))
        if id == 0:
            rec = model.new()
        else:
            rec = model.get(id)
            if not rec:
                flash('Record not found when trying to save')
                return redirect(g.listURL)
                
        model.update(rec,request.form)
        error_list = []
        if save_record(rec,error_list):
            return redirect(g.listURL)
        else:
            for err in error_list:
                flash(err)
        return redirect(g.listURL)
                    
    return render_template('model_edit.html',rec=rec,current_product=current_product,products=products)


@mod.route('/get_model_list/',methods=["GET", ])
@mod.route('/get_model_list/<int:prod_id>/',methods=["GET", ])
def get_list_for_product(prod_id=None):
    """Render an html snippet of the transaciton list for the product"""
    prod_id = cleanRecordID(prod_id)
    models = None
    if prod_id and prod_id > 0:
        models = Model(g.db).select(where='prod_id = {}'.format(prod_id))
        
    return render_template('model_embed_list.html',models=models,prod_id=prod_id)
    
    
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
    
    
def save_record(rec,err_list=[]):
    """Attempt to validate and save a record"""
    if validate_form(rec):
        Model(g.db).save(rec)
        try:
            g.db.commit()
            #Save the date and comment to session
            session['last_model'] = {"price_change_date":rec.price_change_date,}
            return True
            
        except Exception as e:
            g.db.rollback()
            err_list.append(printException('Error attempting to save Model record',str(e)))
            return false
    
    
def validate_form(rec):
    valid_form = True
    datestring = request.form.get('price_change_date','').strip()
    price_change_dateDate = getDatetimeFromString(datestring)
    if datestring == '':
        valid_form = False
        flash('Date may not be empty')
        
    if price_change_dateDate is None:
        flash('Date is not in a known format ("mm/dd/yy")')
        valid_form = False
    else:
        rec.price_change_date = price_change_dateDate
        
    # Must be attached to an product
    productID = cleanRecordID(request.form.get('prod_id',0))
    if not productID or productID < 0:
        flash("You must select an product to use with this model")
        valid_form = False
        
    return valid_form